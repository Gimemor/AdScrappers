# -*- coding: utf-8 -*-
import scrapy
import logging
import traceback
import datetime
from scrapy.loader import ItemLoader
from ..items import Ad
from ..order_types import OrderTypes
import js2py
import io
import re


class BazarpnzSpider(scrapy.Spider):
    name = 'bazarpnz.ru'
    allowed_domains = ['bazarpnz.ru']
    start_urls = [
        # the S param must be the last one since we use that to determine order type
        #'http://bazarpnz.ru/nedvizhimost/?&sort=date&d=desc&s=1',
        #'http://bazarpnz.ru/nedvizhimost/?&sort=date&d=desc&s=2',
        #'http://bazarpnz.ru/nedvizhimost/?&sort=date&d=desc&s=3',
        'http://bazarpnz.ru/nedvizhimost/?&sort=date&d=desc&s=4',
        # 'http://bazarpnz.ru/nedvizhimost/?&s=5',
        # 'http://bazarpnz.ru/nedvizhimost/?&s=6',
        # 'http://bazarpnz.ru/nedvizhimost/?&s=7',
        # 'http://bazarpnz.ru/nedvizhimost/?&s=8',
    ]

    ORDER_TYPE = {
        # BAZAR SELL -> OUT SELL
        1: OrderTypes['SALE'],
        # BAZAR BUY -> OUR BUY
        2: OrderTypes['BUY'],
        # BAZAR RENT -> OUR RENT
        4: OrderTypes['RENT'],
        # BAZAR RENT OUT -> OUR RENT OUT
        3: OrderTypes['RENT_OUT']
    }

    def __init__(self):
        scrapy.Spider.__init__(self)
        self.uptodate_count  = 0
        self.outdate_treshold = 30
        self.item_selector = "//tr[contains(@class, 'norm') and .//div[contains(@class, 'vdatext')]]"
       # self.item_selector = "//table[contains(@class, 'list')]//tr[.//div[contains(@class, 'vdatext')]]"
        self.js_context = js2py.EvalJs()

    # noinspection PyMethodMayBeStatic
    def normalize(self, raw_str):
        return raw_str.replace('\xa0', ' ')

    # noinspection PyMethodMayBeStatic
    def check_ad_scrapping_eligible(self, item):
        date = ' '.join(item.xpath('.//td[contains(@class, \'date\')]/text()').extract()).strip()
        return 'сегодня' in date.lower()

    def get_ad_data_from_category(self, item, response):
        mode_regexp = re.compile(r'[&?]s=(\d+)', re.I)
        mode = mode_regexp.findall(response.url)
        print(mode[0])
        return {
            'url': item.xpath('.//td[contains(@class, \'text\')]//a/@href').extract_first(),
            'order_type': int(mode[0]) if mode else -1,
            'title': item.xpath('.//td[contains(@class, \'text\')]//a/text()').extract_first()
        }

    # noinspection PyMethodMayBeStatic
    def get_cost(self, response):
        cost = response.xpath('//span[@class="price"]/text()').extract_first()
        return cost

    # noinspection PyMethodMayBeStatic
    def get_phone(self, response):
        element = response.xpath('//p[@class="contact_info"][last()]/script/text()').extract_first()
        if element is None:
            return None
        full_js = """                                                           
            var output;                                                         
            document = {                                                        
                write: function(value){                                         
                    output = value;                                             
                }                                                               
            }                                                                   
        """ + element
        self.js_context.execute(full_js)
        phone_regexp = re.compile('tel: (\d+)', re.I)
        phone = phone_regexp.findall(self.js_context.output)
        return phone[0] if phone else None

    # noinspection PyMethodMayBeStatic
    def get_description(self, response):
        return self.normalize(' '.join(response.xpath("//p[contains(@class, 'adv_text')]/text()").extract()))

    # noinspection PyMethodMayBeStatic
    def get_address(self, response):
        return self.normalize(' '.join(response.xpath("//p[@class='contact_info'][last()]/a/text()").extract()))

    # noinspection PyMethodMayBeStatic
    def get_category(self, response):
        regexp = re.compile("Количество\s*комнат:\s*(\d+)\s*", re.I)
        elements = response.xpath("//p[@class='contact_info']/text()").extract_first()
        if not elements:
            return 'Не указано'
        result = regexp.findall(elements)
        return 'Комнат: {}'.format(result[0]) if result else 'Неизвестно'

    # noinspection PyMethodMayBeStatic
    def get_total_square(self, response):
        regexp = re.compile("Общая\s*площадь:\s*(\d+)\s*", re.I)
        elements = response.xpath("//p[@class='contact_info']/text()").extract_first()
        if not elements:
            return None
        result = regexp.findall(elements)
        return float(result[0]) if result else None

    # noinspection PyMethodMayBeStatic
    def get_contact_name(self, response):
        regexp = re.compile("Имя:\s*(\w+)\s*", re.I)
        elements = response.xpath("//p[@class='contact_info'][last()]/text()").extract_first()
        if not elements:
            return None
        result = regexp.findall(elements)
        return result[0] if result else None

    # noinspection PyMethodMayBeStatic
    def get_ad_date(self, response):
        date_regex = re.compile("Дата публикации объявления:\s*([\d.:\W]+)\s*", re.I | re.MULTILINE)
        element = response.xpath("//span[@class='views' and contains(text(), 'Дата публикации')]/text()").extract_first()
        if not element:
            return datetime.datetime.today()
        results = date_regex.findall(element)
        if not results:
            return datetime.datetime.today()
        date_raw = self.normalize(results[0])
        return datetime.datetime.strptime(date_raw, "%d.%m.%Y %H:%M") if date_raw is not None else None

    # noinspection PyMethodMayBeStatic
    def get_floor(self, response):
        pass

    # noinspection PyMethodMayBeStatic
    def get_image_list(self, response):
        pass

    # noinspection PyMethodMayBeStatic
    def parse_ad(self, response):
        meta = response.meta['ad']
        ad_loader = ItemLoader(item=Ad(), response=response)
        ad_loader.add_value('title', meta['title'])
        ad_loader.add_value('source', 0)
        ad_loader.add_value('link', response.url)
        # order_type
        ad_loader.add_value('order_type', BazarpnzSpider.ORDER_TYPE[meta['order_type']])
        print(meta['order_type'], ' ', BazarpnzSpider.ORDER_TYPE[meta['order_type']])
        date = self.get_ad_date(response)
        ad_loader.add_value('placed_at', date)

        if (datetime.datetime.now() - date).days < self.outdate_treshold:
            self.uptodate_count += 1

        ad_loader.add_value('city', 'Пенза')
        ad_loader.add_value('cost', self.get_cost(response))
        ad_loader.add_value('phone', self.get_phone(response))
        ad_loader.add_value('description', self.get_description(response))
        ad_loader.add_value('address', self.get_address(response))
        ad_loader.add_value('category', self.get_category(response))
        ad_loader.add_value('flat_area', self.get_total_square(response))
        ad_loader.add_value('contact_name', self.get_contact_name(response))
        ad_loader.add_value('floor', self.get_floor(response))
        ad_loader.add_value('image_list', self.get_image_list(response))
        """
        # plot_size
        ad_loader.add_value('plot_size', self.get_total_square(response))
        ad_loader.add_value('floor_count', self.get_floor_count(response))
        """
        return ad_loader.load_item()

    def parse(self, response):
        """
        @url  http://bazarpnz.ru/nedvizhimost/?&sort=date&d=desc&s=4
        """
        self.uptodate_count = 0
        for item in response.xpath(self.item_selector):
            ad = self.get_ad_data_from_category(item, response)
            yield response.follow(ad['url'],
                                  meta={'ad': ad, 'dont_merge_cookies': True},
                                  headers={'Referer': None},
                                  callback=self.parse_ad)
        if self.uptodate_count > 0:
            url = response.xpath("//form[@name='topage']/a[./text()='следующей']/@href")\
                .extract_first()
            yield response.follow(url + '?', callback=self.parse)



