"""
宗教查询
URL: http://www.cdmzzj.gov.cn/news.do?method=getTWebCoreArticlePageQuery&channelId=channelId201308271454054502532096
"""
import re
import sys
import time
import random
import requests
import lxml.html
import mysql.connector
from urllib.parse import urlencode


class ReligionSpider(object):

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36",
        "Mozilla/5.0 (Linux; U; Android 4.4.4; zh-cn; MI NOTE LTE Build/KTU84P) AppleWebKit/533.1 (KHTML, like Gecko)Version/4.0 MQQBrowser/5.4 TBS/025489 Mobile Safari/533.1 MicroMessenger/6.3.13.49_r4080b63.740 NetType/cmnet Language/zh_CN",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 9_2_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13D15 MicroMessenger/6.3.13 NetType/WIFI Language/zh_CN",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; Shuame; .NET4.0C; .NET4.0E)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Maxthon/4.9.1.1000 Chrome/39.0.2146.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36",
        "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.13) Gecko/20101209 Firefox/3.6.13",
        "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 5.1; Trident/5.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 6.0)",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; ru; rv:1.9.2.3) Gecko/20100401 Firefox/4.0 (.NET CLR 3.5.30729)",
        "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.8) Gecko/20100804 Gentoo Firefox/3.6.8",
        "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.7) Gecko/20100809 Fedora/3.6.7-1.fc14 Firefox/3.6.7",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.1.4322)",
        "Googlebot/2.1 (http://www.googlebot.com/bot.html)",
        "Opera/9.20 (Windows NT 6.0; U; en)",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.1) Gecko/20061205 Iceweasel/2.0.0.1 (Debian-2.0.0.1+dfsg-2)",
        "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:47.0) Gecko/20100101 Firefox/47.0",
    ]

    config = {
        'user': 'root',
        'password': 'hello',
        'host': '192.168.86.86',
        'port': '3306',
        'database': 'service',
        'raise_on_warnings': True,

    }

    URL = "http://www.cdmzzj.gov.cn/news.do?method=getTWebCoreArticlePageQuery&channelId=channelId201308271454054502532096"
    BASE_URL = "http://www.cdmzzj.gov.cn"

    def __init__(self):
        # Init mysql
        self.conn = mysql.connector.connect(**self.config)
        self.cursor = self.conn.cursor()

    def save2db(self, data):

        template = "INSERT INTO religion(name, type, intro) " \
                   "VALUES (%(name)s, %(type)s, %(intro)s)"
        self.cursor.execute(template, data)
        self.conn.commit()

    # 1st crawl, get total
    def crawl(self):
        data = {
            "pres_curPage": 1,
            "pres_rows": 200,
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        browser = requests.post(self.URL, headers=headers, data=urlencode(data))

        if browser.status_code == 200:
            html = lxml.html.fromstring(browser.text)
            trs = html.xpath('//*[@id="pageDispatchFrom"]/table[1]/tr')
            print(len(trs))
            for tr in trs:
                a = tr.xpath('.//td/a')
                link = self.BASE_URL + a[0].attrib["href"]

                text = tr.xpath('./td[1]')[0].text_content().strip()
                m = re.findall(r'【(.*)】(.*)', text)

                self.crawl2(link, m[0])
        else:
            print("Error while crawling page 1")

    def crawl2(self, url, msg):
        print("processing url: {}".format(url))
        headers = {
            "User-Agent": random.choice(self.USER_AGENTS)
        }
        browser = requests.get(url, headers=headers)
        if browser.status_code == 200:
            html = lxml.html.fromstring(browser.text)
            td = html.xpath('//*[@id="main_body"]/div[2]/table/tr/td/table/tr[2]/td/table/tr[5]/td')
            intro = str(td[0].text_content())

            data = {
                "name": msg[0],
                "type": msg[1],
                "intro": intro,
            }
            self.save2db(data)

        else:
            print("Error while crawling page {}".format(p))

if __name__ == "__main__":
    spider = ReligionSpider()
    spider.crawl()

    spider.cursor.close()
    spider.conn.close()

