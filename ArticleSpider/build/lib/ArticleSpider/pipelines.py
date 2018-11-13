# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
import json
import MySQLdb
import MySQLdb.cursors
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi  # 将mysqldb操作变成异步化的操作


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


# 自定义json文件的导出
class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open("article.json", 'w', encoding="utf-8")
    
    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item
    
    def spider_close(self, spider):
        self.file.close()


# 调用scrapy提供的json export导出json文件
class JsonExportPipeline(object):
    def __init__(self):
        self.file = open("articleexport.json", 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()
    
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
    
    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


# 采用同步的机制写入MySQL
# class MysqlPipeline(object):
#     def __init__(self):
#         self.conn = MySQLdb.connect('127.0.0.1', 'root', 'ccmldl', 'article_spider', charset='utf8', use_unicode=True)
#         self.cursor = self.conn.cursor()
#
#     def process_item(self, item, spider):
#         insert_sql = """
#             insert into jobbole_article(title, url, create_date, url_object_id, front_image_url, front_image_path,
#             comment_nums, fav_nums, praise_nums, tags, content) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#         """
#         self.cursor.execute(insert_sql, (item['title'], item['url'], item['create_date'], item['url_object_id'],
#                                          item['front_image_url'], item['front_image_path'], item['comment_nums'],
#                                          item['fav_nums'], item['praise_nums'], item['tags'], item['content']))
#         self.conn.commit()


# 采用异步的机制写入MySQL
class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)  # **dbparms变成可变化的参数
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将MySQL插入变成异步操作
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)  # 处理异常

    def handle_error(self, failure):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path
        
        return item


# 将数据写入到elasticsearch中
class ElasticsearchPipeline(object):
    def process_item(self, item, spider):
        # 将 item 转换为 es 数据
        item.save_to_es()
        
        return item


































