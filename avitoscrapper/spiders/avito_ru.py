# -*- coding: utf-8 -*-
import scrapy
import datetime
import re
from ..config import AvitoSettings
from scrapy.loader import ItemLoader
from ..items import Ad
from ..order_types import OrderTypes, month_format
from ..logger import Logger


class AvitoRuSpider(scrapy.Spider):
    name = 'avito.ru'
    allowed_domains = ['avito.ru']

    item_selector = '//div[contains(@class, \'item_table clearfix js-catalog-item-enum\')]'
    date_regex = re.compile(r"размещено\s*(\d+\s*\w+|сегодня|вчера)", re.I)
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 0
    }

    def __init__(self):
        scrapy.Spider.__init__(self)
        self.total_count = 0
        self.current_depth = {k: 0 for k in AvitoSettings.LOCATION_PARTS}

    def start_requests(self):
        return [
            scrapy.Request(x.format(loc))
            for x in AvitoSettings.URL_FORMATS
            for loc in AvitoSettings.LOCATION_PARTS
        ]

    # noinspection PyMethodMayBeStatic
    def get_date_from_description(self, raw_data):
        date = AvitoRuSpider.date_regex.findall(raw_data)
        if not date:
            return datetime.datetime.today()
        first = date[0].lower()
        if first == 'сегодня':
            return datetime.datetime.today()
        if first == 'вчера':
            return datetime.date.today() - datetime.timedelta(1)
        result = month_format(first)
        return datetime.datetime.strptime(result, '%d %m %Y')

    # noinspection PyMethodMayBeStatic
    def get_ad_data_from_category(self, item):
        return {
            'url': item.xpath('.//a[contains(@class, \'description-title-link\')]/@href').extract_first(),
        }

    # noinspection PyMethodMayBeStatic
    def get_address(self, response):
        district = response.xpath(
            '//span[contains(@class, \'item-map-address\')]/span/text()').extract_first()
        if district is None:
            return None
        # address = response.xpath(
        #    '//span[contains(@class, \'item-map-address\')]/span/span/text()').extract_first().strip()
        return district.strip()  # + address

    # noinspection PyMethodMayBeStatic
    def get_description(self, response):
        descriptions = response.xpath('//div[contains(@class, \'item-description\')]/p/text()').extract()
        return '\r\n'.join(descriptions)

    # noinspection PyMethodMayBeStatic
    def get_phone(self, response):
        phone_raw = response.xpath("//a[contains(@data-marker, 'item-contact-bar/call')]/@href").extract_first()
        reg = re.compile('tel:([\d\+ -]+)', re.I)
        result = reg.findall(phone_raw)
        return result[0] if result else None

    # noinspection PyMethodMayBeStatic
    def get_room_count(self, response):
        data = response.xpath('//li[contains(@class, \'item-params-list-item\')\
         and contains(./span/text(), \'Количество комнат\')]/text()').extract()
        if data is None:
            return None
        regexp = re.compile('\d+', re.I)
        count_raw = regexp.findall(' '.join(data).strip())
        if not count_raw:
            return None
        count = int(count_raw[0])
        return '1 комната' if count == 1 else \
               '{} комнаты'.format(count) if 1 < count < 5 else \
               '{} комнат'.format(count)

    # noinspection PyMethodMayBeStatic
    def get_total_square(self, response):
        data = response.xpath('//li[contains(@class, \'item-params-list-item\')\
         and contains(./span/text(), \'Общая площадь\')]/text()').extract()
        if data is None:
            return None
        return ' '.join(data).strip()

    # noinspection PyMethodMayBeStatic
    def get_floor(self, response):
        data = response.xpath('//li[contains(@class, \'item-params-list-item\')\
         and contains(./span/text(), \'Этаж:\')]/text()').extract()
        if data is None:
            return None
        return ' '.join(data).strip()

    # noinspection PyMethodMayBeStatic
    def get_floor_count(self, response):
        data = response.xpath('//li[contains(@class, \'item-params-list-item\')\
         and contains(./span/text(), \'Этажей в доме:\')]/text()').extract()
        if data is None:
            return None
        return ' '.join(data).strip()

    # noinspection PyMethodMayBeStatic
    def get_contact_name(self, response):
        data = response.xpath('(//div[@class = \'seller-info-name\']/a/text())[1]')
        if data is None:
            Logger.log('Warning', 'Contact name not found')
            return None
        result = data.extract_first()
        return result if result is not None else 'Неизвестно'

    # noinspection PyMethodMayBeStatic
    def get_image_list(self, response):
        data = response.xpath('//div[contains(@class, \'gallery-img-wrapper\')]//img/@src')
        if data is None:
            Logger.log('Warning', 'Image list not found')
            return None
        return data.extract()

    # noinspection PyMethodMayBeStatic
    def get_cost(self, response):
        data = response.xpath('(//span[contains(@class, \'js-item-price\')])[1]/@content').extract_first()
        if data is None:
            Logger.log('Warning', 'Price not found')
            return None
        return int(data)

    def get_category(self, response):
        data = self.get_room_count(response)
        if not data:
            data = response.xpath("//a[contains(@class, 'js-breadcrumbs-link-interaction')]/text()").extract()
            return data[2]
        return data

    # noinspection PyMethodMayBeStatic
    def get_ad_date(self, response):
        raw_data = response.xpath("//div[contains(@class, 'title-info-metadata-item')]/text()").extract_first()
        return  self.get_date_from_description(raw_data)

    # noinspection PyMethodMayBeStatic
    def get_order_type(self, response):
        data = [x.lower() for x in response.xpath(
            "//a[contains(@class, 'js-breadcrumbs-link-interaction')]/text()").extract()]
        if not data:
            Logger.log('Warning', 'Order type is not found')
            return 0
        if 'куплю' in data:
            return OrderTypes['BUY']
        if 'продам' in data:
            return OrderTypes['SALE']
        if 'сниму' in data:
            return OrderTypes['RENT']
        if 'сдам' in data:
            return OrderTypes['RENT_OUT']
        Logger.log('Warning', 'Order type is unknown')
        return 0

    def get_city(self, response):
        city = response.xpath('//meta[@itemprop="addressLocality"]/@content').extract_first()
        return city if city else "Неизвестно"

    def get_district(self, response):
        fallback_value = 'Неизвестно'
        address = self.get_address(response)
        if address is None:
            return fallback_value
        items = address.split(',')
        for i in items:
            if 'р-н' in items:
                return i
        return fallback_value

    # noinspection PyMethodMayBeStatic
    def get_mobile_address(self, response):
        raw_data = response.xpath("//span[@data-marker='delivery/location']/text()").extract_first()
        return raw_data

    def parse_mobile(self, response):
        ad_loader = response.meta['ad_loader']
        ad_loader.add_value('phone', self.get_phone(response))
        ad_loader.add_value('address', self.get_mobile_address(response))
        return ad_loader.load_item()

    def parse_ad(self, response):
        """
        @url https://www.avito.ru/penza/garazhi_i_mashinomesta/garazh_24_m_930948494
        """
        ad_loader = ItemLoader(item=Ad(), response=response)
        ad_loader.add_xpath('title', '//span[contains(@class, \'title-info-title-text\')]/text()')
        ad_loader.add_value('source', 1)
        ad_loader.add_value('link', response.url)
        ad_loader.add_value('order_type', self.get_order_type(response))
        ad_loader.add_value('placed_at', self.get_ad_date(response))
        ad_loader.add_value('city', self.get_city(response))
        ad_loader.add_value('agent', False)
        ad_loader.add_value('floor', self.get_floor(response))
        ad_loader.add_value('flat_area', self.get_total_square(response))
        # plot_size
        # ad_loader.add_value('plot_size', self.get_total_square(response))
        ad_loader.add_value('cost', self.get_cost(response))
        ad_loader.add_value('district', self.get_district(response))
        ad_loader.add_value('description', self.get_description(response))
        ad_loader.add_value('category', self.get_category(response))
        ad_loader.add_value('floor_count', self.get_floor_count(response))
        ad_loader.add_value('contact_name', self.get_contact_name(response))
        ad_loader.add_value('image_list', self.get_image_list(response))
        url = response.url.replace('www.', 'm.')
        yield response.follow(url, callback=self.parse_mobile, meta={'ad_loader': ad_loader})

    def parse(self, response):
        result = []
        for item in response.xpath(self.item_selector):
            self.total_count += 1
            ad = self.get_ad_data_from_category(item)
            result.append(response.follow(ad['url'], callback=self.parse_ad))
        print("Total count {0}".format(self.total_count))
        url = response.xpath('//a[contains(@class,\'js-pagination-next\')]/@href')\
            .extract_first()
        if not url:
            return result
        self.current_depth[response.url.split('/')[3]] += 1

        if AvitoSettings.SCRAPPING_DEPTH is not None and \
                self.current_depth[response.url.split('/')[3]] > AvitoSettings.SCRAPPING_DEPTH:
            return None
        print('Current depth is {}, scrapping_depth is {}'.format(self.current_depth[response.url.split('/')[3]],
                                                                  AvitoSettings.SCRAPPING_DEPTH))
        result.append(response.follow(url, callback=self.parse))
        return result
