# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import RequestContext, Template
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import smart_str, smart_unicode

import xml.etree.ElementTree as ET
import urllib,urllib2,time,hashlib,json

TOKEN = "test4weixintoken"

@csrf_exempt
def handleRequest(request):
    if request.method == 'GET':
        response = HttpResponse(checkSignature(request), content_type="text/plain")
	return response
    elif request.method == 'POST':
        response = HttpResponse(responseMsg(request),content_type="application/xml")
	return response

def checkSignature(request):
    signature = request.GET.get("signature", None)
    timestamp = request.GET.get("timestamp", None)
    nonce = request.GET.get("nonce", None)
    echoStr = request.GET.get("echostr",None)
    token = TOKEN
    tmpList = [token,timestamp,nonce]
    tmpList.sort()
    tmpstr = "%s%s%s" % tuple(tmpList)
    tmpstr = hashlib.sha1(tmpstr).hexdigest()
    if tmpstr == signature:
        return echoStr
    else:
        return None

def responseMsg(request):
    rawStr = smart_str(request.raw_post_data)
    msg = parseMsgXml(ET.fromstring(rawStr))
    if msg['MsgType'] == 'event' and msg['Event'] == 'subscribe':
        return subscribe(msg)
    
    if 0 == msg['Content'].find('/google:'): 
        return google(msg)
    elif 0 == msg['Content'].find('/baidu:'): 
        return baidu(msg)
    elif 0 == msg['Content'].find(':help'):
        return help(msg)
    else:
        return simsimi(msg)

def subscribe(msg):
    h = "Hello, 欢迎关注litterGu4Game，这是我的一个实验测试账号.\n回复/google:加上您要搜索的内容，可以返回google提供的搜索结果；\n回复/baidu:加上您要搜索的内容，可以返回baidu提供的搜索结果；\n回复:help 获取帮助信息;\n回复其他信息，由风趣幽默的小黄鸡为你答复。\n Have fun!"
    return getTextReply(msg, h)

def help(msg):
    h = """/google:加上您要搜索的内容，可以返回google提供的搜索结果；\n/baidu:加上您要搜索的内容，可以返回baidu提供的搜索结果；\n:help 获取帮助信息;\n其他信息，由风趣幽默的小黄鸡为你答复。但是他会在2014/03/14号左右挂掉，因为我没钱买API；\nORZ~~~
    """
    return getTextReply(msg,h)

def baidu(msg):
    return getTextReply(msg, '还是用google吧，骚年~')

def google(msg):
    query = msg['Content'][8:]
    param = {
        'q': query,
	'v': 1.0
    }
    searchapi = 'http://ajax.googleapis.com/ajax/services/search/web?'
    searchapi = searchapi + urllib.urlencode(param)
    f = urllib2.urlopen(searchapi)
    resStr = f.read()
    resJson = json.loads(resStr)
    results = resJson['responseData']['results']
    response = u'Google 搜索，值得信赖\n'.encode('utf8')
    if resJson['responseStatus'] == 200:
        for re in results:
	    response = response + '~~~~~~~~~~~~~~~~~\n'
	    response = response + '<a href=\"%s\">%s</a>\n'%(re['url'].encode('utf8'),re['title'].encode('utf8'))
	return getTextReply(msg, response)
    else:
        return getTextReply(msg, 'Google 坏了')

def simsimi(msg):
    simsimiurl = 'http://sandbox.api.simsimi.com/request.p?'
    simsimikey = ''
    param = {
        'text' : msg['Content'],
        'ft' : 1.0,
        'lc' : 'ch',
        'key': simsimikey,
    }
    simsimiurl = simsimiurl + urllib.urlencode(param)
    f = urllib2.urlopen(simsimiurl,timeout=4)
    resStr = f.read()
    resJson = json.loads(resStr)
    if resJson['result'] == 100:
        return getTextReply(msg, resJson['response'])
    else:
        return getTextReply(msg, '小黄鸡死了~ORZ')
 
def parseMsgXml(rootElem):
    msg = {}
    if rootElem.tag == 'xml':
        for child in rootElem:
	    msg[child.tag] = smart_str(child.text)
    return msg

def getTextReply(msg, replyContent):
    extTPL = """<xml>
    		<ToUserName><![CDATA[%s]]></ToUserName>
		<FromUserName><![CDATA[%s]]></FromUserName>
    		<CreateTime>%s</CreateTime>
		<MsgType><![CDATA[%s]]></MsgType>
    		<Content><![CDATA[%s]]></Content>
		<FuncFlag>0</FuncFlag>
		</xml>"""

    extTPL = extTPL % (msg['FromUserName'],msg['ToUserName'],str(int(time.time())),'text',replyContent)
    return extTPL
