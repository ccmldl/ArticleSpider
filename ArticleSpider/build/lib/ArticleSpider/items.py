# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import re
import datetime
import redis
from scrapy.loader import ItemLoader
from settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT
from scrapy.loader.processors import MapCompose, TakeFirst, Join

from models.es_types import ArticleType
from w3lib.html import remove_tags

from elasticsearch_dsl.connections import connections
es = connections.create_connection(ArticleType._doc_type.using)

redis_cli = redis.StrictRedis(host="localhost", password="dylan")


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def add_jobbole(value):
    return value + "-bobby"


def date_convert(value):
    try:
        value = value.strip().replace("·", "").strip()
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date


def get_nums(value):
    match_re = re.match(r".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums


# 去掉tag中提取的评论
def remove_comment_tags(value):
    if "评论" in value:
        return ""
    else:
        return value


def return_value(value):
    return value


# 根据字符串生成搜索建议数组
def gen_suggest(index, info_tuple):
    # "python重要性" "title" 10
    # "python重要性" "tags" 3
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            # 调用es的analyze的接口分析字符串
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={"filter": ["lowercase"]}, body=text)
            analyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            new_words = analyzed_words - used_words
        else:
            new_words = set()
            
        if new_words:
            suggests.append({"input": list(new_words), "weight": weight})
    return suggests
    

# 自定义ItemLoader
class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()  # 只取第一个值


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field(
        # input_processor=MapCompose(lambda x: x+"-jobbole", add_jobbole)  # 可以添加两个预处理函数
    )
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    content = scrapy.Field()
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(",")
    )
    
    def get_insert_sql(self):
        insert_sql = """
            insert into jobbole_article(title, url, create_date, url_object_id, front_image_url, front_image_path,
            comment_nums, fav_nums, praise_nums, tags, content) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            self['title'], self['url'], self['create_date'], self['url_object_id'],self['front_image_url'],
            self['front_image_path'], self['comment_nums'], self['fav_nums'], self['praise_nums'],
            self['tags'], self['content']
        )
        return insert_sql, params
    
    def save_to_es(self):
        # 将 item 转换为 es 数据
        article = ArticleType()
        article.title = self["title"]
        article.create_date = self["create_date"]
        article.content = remove_tags(self["content"])
        article.front_image_url = self["front_image_url"]
        if "front_image_path" in self:
            article.front_image_path = self["front_image_path"]
        article.fav_nums = self["fav_nums"]
        article.comment_nums = self["comment_nums"]
        article.praise_nums = self["praise_nums"]
        article.url = self["url"]
        article.tags = self["tags"]
        article.meta.id = self["url_object_id"]
        
        # 建立搜索建议池
        article.suggest = gen_suggest(ArticleType._doc_type.index, ((article.title, 10), (article.tags, 7)))
    
        article.save()
        # 文章数加1
        redis_cli.incr("jobbole_count")
        
        return
    
    
def remove_splash(value):
    # 去掉工作城市的斜线
    return value.replace("/", "")


def handel_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip() != "查看地图"]
    return "".join(addr_list)
    

class LagouJobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()  # 只取第一个值
    
    
class LagouJobItem(scrapy.Item):
    # 拉勾网职位信息
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    dagree_need = scrapy.Field(
        input_processor=MapCompose(remove_splash)
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(",")
    )
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field(
        input_processor=MapCompose(remove_tags)  # 去掉HTML的tag
    )
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, handel_jobaddr)
    )
    company_url = scrapy.Field()
    company_name = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()
    
    def get_inset_sql(self):
        insert_sql = """
            insert into lagou_job(title, url, url_object_id, salary, job_city, work_years, dagree_need, job_type,
            publish_time, job_advantage, job_desc, job_addr, company_name, company_url, tags, crawl_time) values
            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE salary=VALUES (salary),
            job_desc=VALUES (job_desc)
        """
        params = (
            self["title"], self["url"], self["url_object_id"], self["salary"], self["job_city"], self["work_years"], self["dagree_need"],
            self["job_type"], self["publish_time"], self["job_advantage"], self["job_desc"], self["job_addr"],
            self["company_name"], self["company_url"], self["tags"], self["crawl_time"].strftime(SQL_DATETIME_FORMAT)
        )
        
        return insert_sql, params











































