#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Dylan"
# Date: 2018/11/4 14:41

from selenium import webdriver
from scrapy.selector import Selector
import time

# browser = webdriver.Chrome(executable_path="D:\谷歌浏览器\Google_Chrome_v68.0.3440.106_x64\chromedriver.exe")
# browser.get("https://item.taobao.com/item.htm?id=576958029358&ali_refid=a3_430582_1006:1123213702:N:%E6%89%8B%E6%9C%BA%E5%A3%B3:efb945622fbf64d3738ce97360c0bd57&ali_trackid=1_efb945622fbf64d3738ce97360c0bd57&spm=a230r.1.14.1#detail")

# print(browser.page_source)
# t_selector = Selector(text=browser.page_source)
# print(t_selector.css(".tb-promo-item-bd #J_PromoPriceNum::text").extract())

# 模拟登录知乎
# browser.get("https://www.zhihu.com/#signin")
# browser.find_element_by_css_selector(".view-signin input[name='account']").send_keys("18338725230")
# browser.find_element_by_css_selector(".view-signin input[name='password']").send_keys("ccm1234ldl.")
# browser.find_element_by_css_selector(".view-signin button.sign-button").click()

# selenium完成微博模拟登录
# browser.get("https://weibo.com/")
# time.sleep(15)
# browser.find_element_by_css_selector("#loginname").send_keys("18338725230")
# browser.find_element_by_css_selector(".info_list.password input[node-type='password']").send_keys("ccm1234ldl")
# # 需要输入验证码，可以利用yundama_requests识别验证码然后找到对应的元素send_keys过去
# browser.find_element_by_css_selector(".info_list.login_btn a[node-type='submitBtn']").click()

# browser.get("https://www.oschina.net/blog")
# time.sleep(5)

# for i in range(3):
#     # 模拟鼠标下滑加载动态页面
#     browser.execute_script(
#         "window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;"
#     )
#     time.sleep(3)

# 设置chromdriver不加载图片
# chrome_opt = webdriver.ChromeOptions()
# prefs = {"profile.managed_default_content_settings.images": 2}
# chrome_opt.add_experimental_option("prefs", prefs)
# browser = webdriver.Chrome(
#     executable_path="D:\谷歌浏览器\Google_Chrome_v68.0.3440.106_x64\chromedriver.exe",
#     chrome_options=chrome_opt
# )
# browser.get("https://www.taobao.com")

# phantomjs,无界面的浏览器，多进程情况下phantomjs性能会下降很严重
browser = webdriver.PhantomJS(executable_path=r"D:\phantomjs-2.1.1-windows\bin\phantomjs.exe")
browser.get("https://item.taobao.com/item.htm?spm=a212er.steins1370012.act-universal-2018-item-1x5-pc3.7.6f97t26Rt26RRA&id=576493632809")
print(browser.page_source)

browser.quit()

















