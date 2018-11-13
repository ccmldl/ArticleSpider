#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Dylan"
# Date: 2018/10/26 15:31

import requests
try:
    import cookielib
except:
    import http.cookiejar as cookielib
import re

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename="cookies.txt")
try:
    session.cookies.load(ignore_discard=True)
except:
    print("cookie未能加载")

agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
header = {
    "HOST": "www.zhihu.com",
    "Referer": "https://www.zhihu.com",
    "User_Agent": agent
}


# 获取xsrf code
def get_xsrf():
    response = requests.get("https://www.zhihu.com", headers=header)
    print(response.text)
    match_obj = re.match('.*name="_xsrf" value="(.*?)"', response.text)
    if match_obj:
        return match_obj.group(1)
    else:
        return ""


def get_index():
    response = session.get("https://www.zhihu.com", headers=header)
    with open("index_page.html", "wb") as f:
        f.write(response.text.encode("utf-8"))
    print("ok")


def zhihu_login(account, password):
    # 知乎登录
    if re.match("^1\d{10}", account):
        post_url = "https://www.zhihu.com/api/v3/oauth/sign_in"
        post_data = {
            "_xsrf": get_xsrf(),
            "phone_num": account,
            "password": password
        }
        response_text = session.post(post_url, data=post_data, headers=header)
        
        session.cookies.save()
  
 
# zhihu_login("18338725230", "ccm1234ldl.")
get_xsrf()













