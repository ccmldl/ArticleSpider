# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy.http import Request
from scrapy.loader import ItemLoader
from urllib import parse
from items import JobBoleArticleItem, ArticleItemLoader
from utils.common import get_md5

from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']
    
    # start_urls = ['http://blog.jobbole.com/booby/']
    
    def __init__(self):
        self.browser = webdriver.Chrome(executable_path=r"D:\谷歌浏览器\Google_Chrome_v68.0.3440.106_x64\chromedriver.exe")
        super(JobboleSpider, self).__init__()
        # 信号的作用：当spider关闭的时候我们做什么事情
        dispatcher.connect(self.spider_closed, signals.spider_closed)
    
    def spider_closed(self, spider):
        # 当爬虫退出的时候关闭Chrome
        print("spider closed")
        self.browser.quit()
    
    # 收集伯乐在线所有的404的url以及404页面数
    # handle_httpstatus_list = [404]
    #
    # def __init__(self, **kwargs):
    #     self.fail_urls = []
    #     dispatcher.connect(self.handle_spider_closed, signals.spider_closed)
    #
    # def handle_spider_closed(self, spider, reason):
    #     self.crawler.stats.set_value("failed_urls", ",".join(self.fail_urls))
    #     pass
    
    def parse(self, response):
        """
        1.获取文章列表页中的文章url并交给scrapy下载后并进行解析
        2.获取下一页的url并交给scrapy进行下载，下载完成后交给parse
        :param response:
        :return:
        """
        # if response.status == 404:
        #     self.fail_urls.append(response.url)
        #     self.crawler.stats.inc_value("failed_url")
        
        # 解析列表页中的所有文章url并交给scrapy下载后并进行解析
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
                          callback=self.parse_detail)
        
        # 提取下一页并交给scrapy进行下载
        next_urls = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_urls:
            yield Request(url=parse.urljoin(response.url, next_urls), callback=self.parse)
    
    def parse_detail(self, response):
        # 通过item loader加载item
        front_image_url = response.meta.get("front_image_url", "")
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        item_loader.add_css("fav_nums", "span.bookmark-btn::text")
        item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("content", "div.entry")
        item_loader.add_css("tags", ".entry-meta-hide-on-mobile a::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_value("front_image_url", [front_image_url])
        
        article_item = item_loader.load_item()
        
        yield article_item
