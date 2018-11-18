# -*- coding: utf-8 -*-
import scrapy
import logging
import traceback
import datetime
from scrapy.loader import ItemLoader
from ..items import Ad
import requests
import os
import time
from pandas import *
import json
import time
import re

class CianSpider(scrapy.Spider):
    name = 'cian'
    owner_only = True
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 93.1
    }
    allowed_domains = ['cian.ru']
    base_url_format = 'https://penza.cian.ru/export/xls/offers'
    referer_format = 'https://penza.cian.ru/cat.php'
    file = 'offers.xlsx'
    floor_regex = re.compile(r'(\d+)/(\d+),.*', re.I)

    requests_list = [
        '?deal_type=sale&engine_version=2&offer_type=flat&region=4923&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1&room7=1&room9=1&totime=-2',
        '?deal_type=rent&engine_version=2&offer_type=flat&region=4923&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1&room7=1&room9=1&&totime=-2',
    ]

    def start_requests(self):
        return [
             scrapy.Request(CianSpider.referer_format + request,
                            meta={'request': request}) for request in CianSpider.requests_list
        ]

    def __init__(self):
        scrapy.Spider.__init__(self)
        self.item_selector = '//div[contains(@class, "_93444fe79c-card--2Jgih")]'

    # noinspection PyMethodMayBeStatic
    def get_column(self, df, i, j):
        return df[df.columns[j]][i]

    # noinspection PyMethodMayBeStatic
    def check_ad_scrapping_eligible(self, item):
        date = item.xpath('.//div[contains(@class, \'c6e8ba5398-absolute--2Znfs\')]/text()').extract_first()
        owner_type = item.xpath('.//div[contains(@class, \'owner_badge_component-tag-bDgeVixfEsS\')]/text()').extract_first()
        owner_eligible = owner_type or not CianSpider.owner_only
        if date and 'сегодня' in date and owner_eligible:
            return True
        else:
            return False

    def get_ad_data_from_category(self, item):
        return {
            'url': item.xpath('.//a[contains(@class, \'c6e8ba5398-header--1_m0_\')]/@href').extract_first(),
            'scrapping_eligible': self.check_ad_scrapping_eligible(item)
        }

    # noinspection PyMethodMayBeStatic
    def get_title_column(self, df, i):
        for j in df.columns:
            if 'название' in j.lower() and df[j][i] != 'nan':
                return df[j][i]
        return None

    # noinspection PyMethodMayBeStatic
    def get_link(self, df, i):
        for j in df.columns:
            if 'ссылка' in j.lower() and df[j][i]:
                return df[j][i]
        return None

    # noinspection PyMethodMayBeStatic
    def get_cost(self, df, i):
        for j in df.columns:
            if ('цена' in j.lower() or 'стоимость' in j.lower()) and df[j][i]:
                return df[j][i]
        return None

    # noinspection PyMethodMayBeStatic
    def get_floor(self, df, i):
        for j in df.columns:
            if 'дом' in j.lower()  and df[j][i]:
                description = df[j][i]
                match_result = CianSpider.floor_regex.match(description)
                return None if not match_result else match_result.groups(0)[0]
        return None

    # noinspection PyMethodMayBeStatic
    def get_flat_area(self, df, i):
        for j in df.columns:
            if 'площадь' in j.lower() and df[j][i]:
                return df[j][i]
        return None

    # noinspection PyMethodMayBeStatic
    def get_phone(self, df, i):
        for j in df.columns:
            if 'телефон' in j.lower() and df[j][i]:
                return str(df[j][i])
        return None

    # noinspection PyMethodMayBeStatic
    def get_address(self, df, i):
        for j in df.columns:
            if 'адрес' in j.lower() and df[j][i]:
                return df[j][i]
        return None

    # noinspection PyMethodMayBeStatic
    def get_category(self, df, i):
        for j in df.columns:
            if 'количество комнат' in j.lower() and df[j][i]:
                return 'Комнат '+ str(df[j][i])
        return None

    # noinspection PyMethodMayBeStatic
    def get_description(self, df, i):
        for j in df.columns:
            if 'описание' in j.lower() and df[j][i]:
                return 'Комнат ' + str(df[j][i])
        return None

    # noinspection PyMethodMayBeStatic
    def get_floor_count(self, df, i):
        for j in df.columns:
            if 'дом' in j.lower()  and df[j][i]:
                description = df[j][i]
                match_result = CianSpider.floor_regex.match(description)
                return None if not match_result else match_result.groups(0)[1]
        return None

    def parse_ad(self, df, response):
        results = []
        for i in df.index:
            item = dict()
            item['title'] = self.get_title_column(df, i)
            item['source'] = 2
            item['link'] = self.get_link(df, i)
            item['contact_name'] = None
            item['order_type'] = 2 if 'rent' in response.url else 1
            item['placed_at'] = datetime.today()
            item['city'] = "Пенза"
            item['cost'] = self.get_cost(df, i)
            item['floor'] = self.get_floor(df, i)
            item['flat_area'] = self.get_flat_area(df, i)
            item['phone'] = self.get_phone(df, i)
            item['address'] = self.get_address(df, i)
            item['category'] = self.get_category(df, i)
            #item['agent'] = self.get_column(df, i, 2)
            item['description'] = self.get_description(df, i)
            item['floor_count'] = self.get_floor_count(df, i)
            #item['contact_name'] = self.get_column(df, i, 2)
            #item['image_list'] = self.get_column(df, i, 2)
            results.append(item)
        return results

    def parse(self, response):
        url = response.xpath(
            '//li[contains(@class, \'_93444fe79c-list-item--2QgXB _93444fe79c-list-item--active--2-sVo\')]/following-sibling::li/a/@href') \
            .extract_first()
        request = CianSpider.base_url_format + '?' + response.url.split('?', 1)[1]
        time.sleep(15)
        xls_response = requests.get(request,
                                headers={
                                    'referer': response.url,
                                    "User-Agent": response.request.headers['User-Agent']
                                })
        if xls_response.status_code == 200:
            with open(CianSpider.file, 'wb') as f:
                f.write(xls_response.content)
        df = pandas.read_excel(CianSpider.file)
        df = df.where((pandas.notnull(df)), None)
        items = self.parse_ad(df, response)
        for item in items:
            yield item
        os.remove(CianSpider.file)
        if url:
            yield response.follow(url, callback=self.parse, meta={'dont_merge_cookies': True})
