# -*- coding: utf-8 -*-
import scrapy
import logging
import traceback
import datetime
from scrapy.loader import ItemLoader
from ..items import Ad
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from PIL import Image
import base64
import pytesseract
import io
import selenium.webdriver.support.expected_conditions as expected_condition
import time


class CianSpider(scrapy.Spider):
    name = 'cian'
    owner_only = True
    allowed_domains = ['cian.ru']
    start_urls = [
        'https://penza.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&region=4923&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1&room7=1&room9=1'
    ]

    requests_list = [
        '?deal_type=sale&engine_version=2&offer_type=flat&region=4923&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1&room7=1&room9=1&totime=-2',
        # '?deal_type=rent&engine_version=2&offer_type=flat&region=4923&room1=1&room2=1&room3=1&room4=1&room5=1&room6=1&room7=1&room9=1&&totime=-2',
    ]

    def __init__(self):
        scrapy.Spider.__init__(self)
        self.item_selector = '//div[contains(@class, "_93444fe79c-card--2Jgih")]'

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

    def parse_ad(self, response):
        ad_loader = ItemLoader(item=Ad(), response=response)
        print(response.url)
        """
        ad_loader.add_xpath('title', '//span[contains(@class, \'title-info-title-text\')]/text()')
        
        ad_loader.add_value('source', 1)
        ad_loader.add_value('link', response.url)
        #order_type
        ad_loader.add_value('order_type', 1)
        ad_loader.add_value('placed_at', datetime.datetime.today())
        # City
        # ...
        ad_loader.add_value('floor', self.get_floor(response))
        ad_loader.add_value('flat_area', self.get_total_square(response))
        # plot_size
        # ad_loader.add_value('plot_size', self.get_total_square(response))
        ad_loader.add_value('cost', self.get_cost(response))
        ad_loader.add_value('phone', self.get_phone(response))
        ad_loader.add_value('address', self.get_address(response))
        ad_loader.add_value('description', self.get_description(response))
        ad_loader.add_value('category', self.get_room_count(response))
        ad_loader.add_value('floor_count', self.get_floor_count(response))
        ad_loader.add_value('contact_name', self.get_contact_name(response))
        ad_loader.add_value('image_list', self.get_image_list(response))
        """

        return ad_loader.load_item()

    def parse(self, response):
        url = response.xpath('//li[contains(@class, \'_93444fe79c-list-item--2QgXB _93444fe79c-list-item--active--2-sVo\')]/following-sibling::li') \
            .extract_first()
        print(url)
        yield response.follow(url, callback=self.parse)

