# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.template import RequestContext, Template
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import smart_str, smart_unicode

import xml.etree.ElementTree as ET
import urllib,urllib2,time,hashlib

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
#   print msg
#   print getTextReply(msg, 'hello,world')
    return getTextReply(msg, 'hello,world')

def parseMsgXml(rootElem):
    msg = {}
    if rootElem.tag == 'xml':
        for child in rootElem:
	    msg[child.tag] = smart_str(child.text)
    return msg

def getTextReply(msg, replyContent):
    extTPL = """<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName>
    <CreateTime>%s</CreateTime><MsgType><![CDATA[%s]]></MsgType>
    <Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>"""

    extTPL = extTPL % (msg['FromUserName'],msg['ToUserName'],str(int(time.time())),'text',replyContent)
    return extTPL
