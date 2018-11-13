#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Dylan"
# Date: 2018/11/3 11:25

import requests
from scrapy.selector import Selector
import MySQLdb

conn = MySQLdb.connect(host="127.0.0.1", user="root", passwd="ccmldl", db="article_spider", charset="utf8")
cursor = conn.cursor()


def crawl_ips():
    # 爬取西刺的免费ip代理
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"
    }
    for i in range(1, 3476):
        re = requests.get("http://www.xicidaili.com/nn/{0}".format(i), headers=headers)
        selector = Selector(text=re.text)
        all_trs = selector.css("#ip_list tr")
        
        ip_list = []
        for tr in all_trs[1:]:
            speed_str = tr.css(".bar::attr(title)").extract_first()
            if speed_str:
                speed = float(speed_str.split("秒")[0])
            all_texts = tr.css("td::text").extract()
            ip = all_texts[0]
            port = all_texts[1]
            proxy_type = all_texts[5]
            ip_list.append((ip, port, proxy_type, speed))
        
        for ip_info in ip_list:
            cursor.execute(
                "insert into proxy_ip(ip, port, speed, proxy_type) values ('{0}', '{1}', {2}, '{3}')".format(
                    ip_info[0], ip_info[1], ip_info[3], ip_info[2]
                )
            )
            conn.commit()


class GetIP(object):
    def delete_ip(self, ip):
        # 从数据库中删除无效的ip
        delete_sql = """
            delete from proxy_ip where ip='{0}'
        """.format(ip)
        cursor.execute(delete_sql)
        conn.commit()
        return True
    
    def judeg_ip(self, ip, port, proxy_type):
        # 判断ip是否可用
        http_url = "http://www.baidu.com"
        proxy_url = "{0}://{1}:{2}".format(proxy_type.lower(), ip, port)
        try:
            proxy_dict = {
                "http": proxy_url
            }
            response = requests.get(http_url, proxies=proxy_dict)
            # return True
        except Exception as e:
            # print("invalid ip and port")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                # print("effective ip")
                return True
            else:
                # print("invalid ip and port")
                self.delete_ip(ip)
                return False
    
    def get_random_ip(self):
        # 从数据库中随机获取一个可用的ip
        random_sql = """
            select ip, port, proxy_type from proxy_ip order by rand() limit 1
        """
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            proxy_type = ip_info[2]
            
            judge_res = self.judeg_ip(ip, port, proxy_type)
            if judge_res:
                return "{0}://{1}:{2}".format(proxy_type, ip, port)
            else:
                return self.get_random_ip()


if __name__ == '__main__':
    crawl_ips()
    get_ip = GetIP()
    print(get_ip.get_random_ip())
