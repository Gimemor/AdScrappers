# -*- coding: utf-8 -*-
import scrapy
import logging
import traceback
from scrapy.loader import ItemLoader
from ..items import Ad
from ..order_types import OrderTypes, month_format
import requests
import os
import time
from pandas import *
import json
import datetime
import re


class CianSpider(scrapy.Spider):
    name = 'cian'
    owner_only = True
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 1.1
    }
    allowed_domains = ['cian.ru']
    base_url_format = 'https://penza.cian.ru/export/xls/offers'
    referer_format = 'https://penza.cian.ru/'
    file = 'offers.xlsx'
    date_regex = re.compile(r"\s*(\d+\s*\w+|сегодня|вчера)", re.I)
    floor_regex = re.compile(r'(\d+)/(\d+),.*', re.I)
    total_count = 0

    requests_list = [
        'kupit-kvartiru/',
        'kupit-komnatu/',
        'kupit-dom/',
        'snyat-kvartiru/'
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
    def get_ad_date_from_list(self, item):
        raw_date = response.xpath(".//div[contains(@class, 'c6e8ba5398-absolute--2Znfs')]/text()").extract_first()
        if not raw_date:
            return datetime.datetime.today()
        raw_date = raw_date.lower()
        date = CianSpider.date_regex.findall(raw_date)
        if not date:
            return datetime.datetime.today()
        first = date[0].lower()
        if not first or 'сегодня' in first:
            return datetime.datetime.today()
        if 'вчера' in first:
            return datetime.datetime.today() - datetime.timedelta(1)
        result = month_format(first)
        return datetime.strptime(result, '%d %m %Y')


    # noinspection PyMethodMayBeStatic
    def get_cost(self, response):
        raw = response.xpath("//span[@itemprop='price']/@content").extract_first()
        if not raw:
            return None
        return raw.replace('\xa0', ' ').replace(' ', '')

    # noinspection PyMethodMayBeStatic
    def get_floor(self, response):
        return response.xpath("//li[@class='a10a3f92e9--item--_ipjK' and span[@class='a10a3f92e9--name--3bt8k' and text() = 'Этаж']]/span[@class='a10a3f92e9--value--3Ftu5']/text()").extract_first()

    def get_floor_count(self, response):
        return response.xpath("//li[@class='a10a3f92e9--item--_ipjK' and span[@class='a10a3f92e9--name--3bt8k' and text() = 'Этажей в доме']]/span[@class='a10a3f92e9--value--3Ftu5']/text()").extract_first()

    # noinspection PyMethodMayBeStatic
    def get_flat_area(self, response):
        return response.xpath("//div[@class='a10a3f92e9--info--2ywQI' and div[@class='a10a3f92e9--info-title--mSyXn' and text() = 'Общая']]/div[@class='a10a3f92e9--info-text--2uhvD']/text()").extract_first()


    # noinspection PyMethodMayBeStatic
    def get_phone(self, response):
        raw = response.xpath("//a[@class='a10a3f92e9--phone--3XYRR']/@href").extract_first()
        reg = re.compile('tel:([\d\+ -]+)', re.I)
        result = reg.findall(raw)
        return result[0] if result else None

    # noinspection PyMethodMayBeStatic
    def get_address(self, response):
        raw = response.xpath("//div[@class='a10a3f92e9--geo--18qoo']/span/@content").extract_first()
        return raw

    # noinspection PyMethodMayBeStatic
    def get_category(self, response):
        raw = response.xpath("//div[@class='a10a3f92e9--breadcrumbs--1kChM']/span[3]/a/@title").extract_first()
        return raw if raw else "Неизвестно"

    # noinspection PyMethodMayBeStatic
    def get_category_from_page(self, response):
        raw = response.xpath('//a[contains(@class, \'a10a3f92e9--link--378yo\')]/span/text()').extract()[2]
        return raw

    # noinspection PyMethodMayBeStatic
    def get_description(self, response):
        raw = response.xpath("//meta[@property='og:description']/@content").extract_first()
        return raw

    # noinspection PyMethodMayBeStatic
    def get_order_type(self, response):
        raw = response.xpath("//div[@class='a10a3f92e9--breadcrumbs--1kChM']/span[2]/a/@title").extract_first()
        if 'Продажа' in raw:
            return OrderTypes['SALE']
        if 'Аренда' in raw:
            return OrderTypes['RENT_OUT']

    # noinspection PyMethodMayBeStatic
    def get_title(self, response):
        return response.xpath("//h1[@class='a10a3f92e9--title--2Widg']/text()").extract_first()

    # noinspection PyMethodMayBeStatic
    def get_contact_name(self, response):
        return response.xpath("//h2[@class='a10a3f92e9--title--2Zrxn']/text()").extract_first()

    # noinspection PyMethodMayBeStatic
    def get_image_list(self, response):
        return response.xpath("//img[@class='a10a3f92e9--photo--3ybE1']/@src").extract()

    def parse_ad(self, response):
        """
        @url https://penza.cian.ru/sale/flat/197367444/
        """
        ad_loader = ItemLoader(item=Ad(), response=response)
        ad_loader.add_value('title', self.get_title(response))
        ad_loader.add_value('source', 2)
        ad_loader.add_value('link', response.url)
        # order_type
        ad_loader.add_value('order_type', self.get_order_type(response))
        date = self.get_ad_date(response)
        ad_loader.add_value('placed_at', date)
        ad_loader.add_value('city', 'Пенза')
        ad_loader.add_value('agent', False)
        ad_loader.add_value('cost', self.get_cost(response))
        ad_loader.add_value('phone', self.get_phone(response))
        ad_loader.add_value('description', self.get_description(response))
        ad_loader.add_value('address', self.get_address(response))
        ad_loader.add_value('category', self.get_category(response))
        ad_loader.add_value('flat_area', self.get_flat_area(response))
        ad_loader.add_value('contact_name', self.get_contact_name(response))
        ad_loader.add_value('floor', self.get_floor(response))
        ad_loader.add_value('image_list', self.get_image_list(response))
        """
        # plot_size
        ad_loader.add_value('plot_size', self.get_total_square(response))
        """
        ad_loader.add_value('floor_count', self.get_floor_count(response))

        return ad_loader.load_item()

    # noinspection PyMethodMayBeStatic
    def get_ad_date(self, response):
        raw_date = response.xpath("//div[contains(@class, 'a10a3f92e9--container--3nJ0d')]/text()").extract_first()
        if not raw_date:
            return datetime.datetime.today()
        raw_date = raw_date.lower()
        date = CianSpider.date_regex.findall(raw_date)
        if not date:
            return datetime.datetime.today()
        first = date[0].lower()
        if not first or 'сегодня' in first:
            return datetime.datetime.today()
        if 'вчера' in first:
            return datetime.datetime.today() - datetime.timedelta(1)
        result = month_format(first)
        return datetime.datetime.strptime(result, '%d %m %Y')

    def parse(self, response):
        items = response.xpath("//a[contains(@class, 'c6e8ba5398-header--1_m0_')]/@href").extract()
        for item in items:
            CianSpider.total_count += 1
            yield response.follow(item, headers={"Referer": response.url, "Host": "penza.cian.ru"}, callback=self.parse_ad)
        print(CianSpider.total_count)
        subblocks = response.xpath("//a[contains(@class, 'c6e8ba5398-sub-block--21VAX c6e8ba5398-similar--3RghR')]/@href").extract()
        for block in subblocks:
            yield response.follow(block, callback=self.parse, meta={'dont_merge_cookies': True})
        url = response.xpath(
            '//li[contains(@class, \'93444fe79c-list-item--2QgXB _93444fe79c-list-item--active--2-sVo\')]/following-sibling::li/a/@href') \
            .extract_first()
        if url:
            yield response.follow(url, callback=self.parse, meta={'dont_merge_cookies': True})
        print('Total count ' + str(CianSpider.total_count))
