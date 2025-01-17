# -*- coding: utf-8 -*-
import scrapy
import logging
import traceback
import datetime
from scrapy.loader import ItemLoader
from ..items import Ad
from ..logger import Logger
from ..order_types import OrderTypes
import js2py
import io
import re


class BazarpnzSpider(scrapy.Spider):
    name = 'bazarpnz.ru'
    allowed_domains = ['bazarpnz.ru', 'i58.ru']
    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 3.1
    }
    start_urls = [
        # the S param must be the last one since we use that to determine order type
        'http://bazarpnz.ru/nedvizhimost/?&sort=date&d=desc&s=1',
        'http://bazarpnz.ru/nedvizhimost/?&sort=date&d=desc&s=2',
        'http://bazarpnz.ru/nedvizhimost/?&sort=date&d=desc&s=3',
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
        self.outdate_treshold = 2
        #self.item_selector = "//tr[contains(@class, 'norm') and .//div[contains(@class, 'vdatext')]]"
        self.item_selector = "//table[contains(@class, 'list')]//tr[.//div[contains(@class, 'vdatext')]]"
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
        return {
            'url': item.xpath('.//td[contains(@class, \'text\')]//a/@href').extract_first(),
            'order_type': int(mode[0]) if mode else -1,
            'title': item.xpath('.//td[contains(@class, \'text\')]//a/text()').extract_first()
        }

    # noinspection PyMethodMayBeStatic
    def get_cost(self, response):
        cost = response.xpath('//span[@class="price"]/text()').extract_first()
        if cost is None:
            return None
        cost = cost.replace(' ', '').replace('\xa0', '')
        output = re.findall('\d+', cost)
        return output[0] if output else ''

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
        output = self.js_context.output
        output = output.replace('&#45;', '')
        output = output.replace('&#43;', '')
        output = output.replace('&#40;', '')
        output = output.replace('&#41;', '')
        if 'href' in output:
            href_regex = re.compile('tel:\s*([\d\ -]+)', re.I)
            phones = href_regex.findall(output)
            return phones[0] if phones else None
        phone_regexp = re.compile('[\d\-\(\)\ ]+', re.I)
        phone = phone_regexp.findall(output)
        if not phone:
            Logger.log("WARN", "Unable to parse phone from " + response.url)
            return None
        return phone[0] if phone else None

    # noinspection PyMethodMayBeStatic
    def get_description(self, response):
        return self.normalize(' '.join(response.xpath("//p[contains(@class, 'adv_text')]/text()").extract()))

    # noinspection PyMethodMayBeStatic
    def get_address(self, response):
        return self.normalize(' '.join(response.xpath("//p[@class='contact_info'][last()]/a/text()").extract()))

    # noinspection PyMethodMayBeStatic
    def get_category(self, response):
        contact_info = response.xpath('//p[contains(@class, "contact_info")]').extract()
        if contact_info:
            raw = "\n".join(contact_info)
            regexp = re.compile("Количество комнат: (.+?)<br>", re.I)
            result = regexp.findall(raw)
            if result is not None and len(result) > 0:
                return result[0]
        return self.get_category_from_breadcrumbs(response)

    # noinspection PyMethodMayBeStatic
    def get_category_from_breadcrumbs(self, response):
        category_number = '3'
        if 'i58.ru' in response.url:
            category_number = '4'
        breadcrumb_category = response.xpath('//div[contains(@id, \'nav\')]/a[' + category_number + ']/text()').extract_first()
        if breadcrumb_category is not None:
            return breadcrumb_category
        regexp = re.compile("Количество\s*комнат:\s*(\d+)\s*", re.I)
        elements = response.xpath("//p[@class='contact_info']/text()").extract_first()
        if not elements:
            Logger.log("WARN", "Unable to parse category from " + response.url)
            return 'Не указано'
        result = regexp.findall(elements)
        return 'Комнат: {}'.format(result[0]) if result else 'Неизвестно'

    # noinspection PyMethodMayBeStatic
    def is_new_building(self, response):
        category_number = '4'
        if 'i58.ru' in response.url:
            category_number = '5'
        breadcrumb_category = response.xpath(
            '//div[contains(@id, \'nav\')]/a[' + category_number + ']/text()').extract_first()
        return breadcrumb_category == 'Новостройки' if breadcrumb_category is not None else False

    # noinspection PyMethodMayBeStatic
    def get_total_square(self, response):
        regexp = re.compile("Общая\s*площадь:\s*(\d+)\s*", re.I)
        elements = '\n'.join(response.xpath("//p[@class='contact_info']/text()").extract())
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
        raw = response.xpath('//a[contains(@class, "big_photo")]/@href')
        if not raw:
            return []
        hrefs = raw.extract()
        return [BazarpnzSpider.name + x for x in hrefs]

    # noinspection PyMethodMayBeStatic
    def parse_ad(self, response):
        """
        @url: http://bazarpnz.ru/ann/36330946/
        """

        meta = response.meta['ad']
        ad_loader = ItemLoader(item=Ad(), response=response)
        ad_loader.add_value('title', meta['title'])
        ad_loader.add_value('source', 0)
        ad_loader.add_value('link', response.url)
        # order_type
        ad_loader.add_value('order_type', BazarpnzSpider.ORDER_TYPE[meta['order_type']])
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
        ad_loader.add_value('agent', 'i58.ru' in response.url)
        ad_loader.add_value('contact_name', self.get_contact_name(response))
        ad_loader.add_value('floor', self.get_floor(response))
        ad_loader.add_value('image_list', self.get_image_list(response))
        ad_loader.add_value('new_building', self.is_new_building(response))
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
        #if self.uptodate_count > 0:
        url = response.xpath("//form[@name='topage']/a[./text()='следующей']/@href")\
            .extract_first()
        if not url:
            Logger.log('WARN', 'Next page url not found on the {}'.format(response.url))
            return None
        yield response.follow(url + '?', callback=self.parse)



