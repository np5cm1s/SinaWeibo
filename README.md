## 相比原版的改动点
登录方式改为读取cookies.json
图片上传改为读取url
适应海外使用weibo.com地址改为www.weibo.com


# SinaWeibo
>python3脚本,非官方API实现登录新浪微博发送消息和图片

## 安装
> pip install sinaweibo

## API
| Name|Params|Remark|
| --------   | -----:  | :----: |
| uploadPic  | picPath                |上传图片|
| postMessage| message                |发送文本微博|
| postImage  | message,*picPaths      |发送文本加图片(图片可多张)|
| getFollowList  | pageNum      |获取我的关注|
| getFansList  | pageNum      |获取我的粉丝|
| getMyBlogList  | pageNum      |获取我的微博|

## 使用Demo
>test/test.py

## 依赖库
>pip install requests

>pip install rsa

>pip install beautifulsoup4



