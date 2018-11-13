# -*- coding: utf-8 -*-

from datetime import datetime
from elasticsearch_dsl import Date, Integer, Completion, Keyword, Text, DocType
from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=["localhost"])


class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}


ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])


# 伯乐在线文章类型
class ArticleType(DocType):
    suggest = Completion(analyzer=ik_analyzer)  # 自动补全
    title = Text(analyzer="ik_max_word")
    create_date = Date()
    url = Keyword()
    url_object_id = Keyword()
    front_image_url = Keyword()
    front_image_path = Keyword()
    praise_nums = Integer()
    fav_nums = Integer()
    comment_nums = Integer()
    content = Text(analyzer="ik_max_word")
    tags = Text(analyzer="ik_max_word")
    
    class Meta:
        index = "jobbole"
        doc_type = "article"


if __name__ == '__main__':
    ArticleType.init()  # 自定义mapping




























