#!/usr/bin/python
# -*- coding: utf-8 -*-
import base64
import json
import random
import re
import time
import requests
from .utils import WbUtils
from requests.cookies import RequestsCookieJar
import urllib
from requests import Request

WBCLIENT = 'ssologin.js(v1.4.19)'
user_agent = (
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.11 (KHTML, like Gecko) '
    'Chrome/20.0.1132.57 Safari/536.11'
)


class Weibo(object):

    logincode = ""
    password = ""
    uid = ""
    homeUrl = ""

    def __init__(self,logincode,password):
        self.logincode = logincode
        self.password = password

        self.session = requests.session()
        self.session.headers = {
            "User-Agent": user_agent
        }
        self.__login()
        follow, fans, weibo = self.userInfo()
        print("关注：%s,粉丝:%s,微博:%s"%(follow,fans,weibo))

    def __login(self):
        try:
            with open('cookies.json', 'r', encoding='utf-8') as f:
                    listCookies = json.loads(f.read())

            cookies=RequestsCookieJar()

            for cookie in listCookies:
                cookies[cookie['name']]=cookie['value']
            
            self.session.cookies = cookies
            
            self.uid = "你的uid"

            print("%s 登录成功"%self.logincode)
        except Exception as e:
            print("%s 登录失败"%self.logincode)
            raise e

    def __str__(self):
        return "logincode:%s,password:%s,uid:%s,url:%s"%(self.logincode,self.password,self.uid,self.homeUrl)

    def userInfo(self):
        resp = self.session.get("https://www.weibo.com/")
        self.homeUrl = resp.url
        print(self.homeUrl)
        self.baseUrl = self.homeUrl[:self.homeUrl.index("home")-1]
        fmDict = WbUtils.getFMViewObjDict(resp.text)
        follow, fans, weibo = WbUtils.getMyInfo(fmDict)
        return follow, fans, weibo

    def __postData(self,data):
        currTime = "%d" % (time.time()*1000)
        self.session.headers["Host"]="www.weibo.com"
        self.session.headers["Origin"]="https://www.weibo.com"
        Referer = "https://www.weibo.com/u/%s/home?wvr=5" % self.uid
        self.session.headers["Referer"] = Referer
        resp = self.session.post(
            'https://www.weibo.com/aj/mblog/add?ajwvr=6&__rnd=%s'%currTime,data = data
        )
        #req = Request('POST','https://www.weibo.com/aj/mblog/add?ajwvr=6&__rnd=%s'%currTime,data=data)
        #prepped = self.session.prepare_request(req)
        #print('\n'.join(['%s:%s' % item for item in prepped.__dict__.items()]))
        #resp = self.session.send(prepped)
        print('\n'.join(['%s:%s' % item for item in resp.request.__dict__.items()]))
        try:
            result, msg, txt= WbUtils.checkResultMessage(resp.content)
            if result == True:
                print("消息发送成功:%s" % data['text'])
            else:
                print("消息发送失败:%s" % msg)
        except Exception as e:
            print("消息发送失败:%s" % data)
            raise e

    def postMessage(self,message):
        self.__postData(WbUtils.getTextStructure(message))

    def uploadPic(self,picPath):
        url = 'www.weibo.com/u/' + self.uid
        self.session.headers["Referer"] = self.homeUrl
        self.session.headers["Host"] = "picupload.weibo.com"
        self.session.headers["Origin"] = "https://www.weibo.com"
        resp = self.session.post(
            'https://picupload.weibo.com/interface/pic_upload.php?app=miniblog' +
            '&data=1&url=' + url + '&markpos=1&logo=1&nick=&marks=1&url=' + url +
            '&mime=image/png&ct=' + str(random.random()),
           # data=open(picPath, 'rb')
            data = urllib.request.urlopen(picPath).read()
        )
        resultJson = json.loads(re.search('{"code.*', resp.text).group(0))
        return resultJson["data"]["pics"]["pic_1"]["pid"]

    def postImage(self,message,*picPaths):
        picList = []
        for pic in picPaths:
            picList.append(self.uploadPic(pic))
        self.__postData(WbUtils.getImageStructure(message,"|".join(picList),len(picList)))

    def getFollowList(self,pageNum=1):
        url = "https://www.weibo.com/p/100505%s/myfollow?t=1&cfs=&Pl_Official_RelationMyfollow__93_page=%d#Pl_Official_RelationMyfollow__93"%(self.uid,pageNum)
        resp = self.session.get(url)
        fmDict = WbUtils.getFMViewObjDict(resp.text)
        followList,pageCount = WbUtils.getFollowList(fmDict)
        return followList,pageNum < pageCount

    def getFansList(self,pageNum=1):
        url = "https://www.weibo.com/%s/fans?cfs=600&relate=fans&t=1&f=1&type=&Pl_Official_RelationFans__88_page=%d#Pl_Official_RelationFans__88"%(self.uid,pageNum)
        resp = self.session.get(url)
        fmDict = WbUtils.getFMViewObjDict(resp.text)
        fansList, pageCount = WbUtils.getFansList(fmDict)
        return fansList, pageNum < pageCount

    def __getMyBlogList(self,pageNum,pagebar = 0):
        url = "https://www.weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=100505&is_search=0&visible=0&is_all=1&is_tag=0&profile_ftype=1" \
            "&pl_name=Pl_Official_MyProfileFeed__21&id=1005051656558815&script_uri=&feed_type=0" \
            "&page=%d&pagebar=%d&pre_page=1&domain_op=100505&__rnd=1516869103198"%(pageNum,pagebar)
        resp = self.session.get(url)
        _flag,msg,data = WbUtils.checkResultMessage(resp.text)
        if _flag:
            contentList = WbUtils.getBlogList(data)
            return contentList

    def getMyBlogList(self,pageNum=1):
        url = self.baseUrl + "/profile?pids=Pl_Official_MyProfileFeed__21&is_search=0&visible=0&is_all=1&is_tag=0&profile_ftype=1&page=%d&ajaxpagelet=1&ajaxpagelet_v6=1&__ref="%(pageNum)
        resp = self.session.get(url)
        htmlStr =  WbUtils.getProfileHtml(resp.text)
        blogList = WbUtils.getBlogList(htmlStr)
        blogList.extend(self.__getMyBlogList(pageNum,0))
        blogList.extend(self.__getMyBlogList(pageNum,1))
        return blogList


