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
    if 0 == msg['Content'].find('/google:'): 
        return google(msg)
    elif 0 == msg['Content'].find('/baidu:'): 
        return baidu(msg)

def baidu(msg):
    query = msg['Content'][7:]


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
    response = 'Google 搜索，值得信赖'
    if resJson['responseStatus'] == 200:
        for re in results:
	    response = '%s<a href=\"%s\">%s</a>\n'%(response,re['url'],re['title'])
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

def parseHtml(rootElem):
   

def getTextPicReply():
    extTPL = """<xml><ToUserName><![CDATA[%s]]></ToUserName>
    		<FromUserName><![CDATA[%s]]></FromUserName>
    		<CreateTime>%s</CreateTime>
		<MsgType><![CDATA[%s]]></MsgType>
    		<ArticleCount>1</ArticleCount>
		<Articles>
		<item>
		Title><![CDATA[%s]]></Title>
		<Description><![CDATA[%s]]></Description>
		<PicUrl><![CDATA[%s]]></PicUrl>
		<Url><![CDATA[%s]]></Url>
		</item>
		</Articles>
		</xml>"""
    

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
