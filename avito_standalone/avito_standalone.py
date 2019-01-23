import requests
import sys
import asyncio
import re
import datetime
from lxml import html
from config import AvitoSettings, ProxySettings, RemoteServerSettings
from proxy_manager import ProxyManager
from web_client import WebClient
from logger import Logger


# Init proxy manager
class AvitoStandalone:
    date_regex = re.compile(r"(?:размещено\s*)?(\d+\s*\w+|сегодня|вчера)", re.I)
    time_regex = re.compile(r"\d{1,2}:\d{1,2}")


    def __init__(self):
        self.proxy_manager = ProxyManager(ProxySettings)
        self.web_client = WebClient(self.proxy_manager)
        self.is_running = True
        self.duplicates = {}

    @staticmethod
    def get_start_urls():
        return [f.format(l)
                for l in AvitoSettings.LOCATION_PARTS
                for f in AvitoSettings.URL_FORMATS]

    # noinspection PyMethodMayBeStatic
    def get_date_from_description(self, raw_data):
        date = self.date_regex.findall(raw_data)
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
    def get_time_from_description(self, raw_data):
        time = self.time_regex.findall(raw_data)
        if not time:
            return datetime.timedelta(0, 0)
        t = time[0].lower().split(':')
        return datetime.timedelta(hours=int(t[0]), minutes=int(t[1]))

    # noinspection PyMethodMayBeStatic
    def get_ad_date_inner(self, raw_data):
        dt = self.get_date_from_description(raw_data)
        time = self.get_time_from_description(raw_data)
        return datetime.datetime(dt.year, dt.month, dt.day) + time

    # noinspection PyMethodMayBeStatic
    def get_ad_data_from_category(self, item):
        link = item.xpath('.//a[contains(@class, \'MBUbs eXo1j e-2RA\')]/@href')[0]
        return {
            'link': AvitoSettings.BASE_MOBILE + link,
            'placed_at': self.get_ad_date_from_category(item) + datetime.timedelta(hours=3)
        }


    def get_ad_date_from_category(self, item):
        response = item.xpath('.//div[contains(@class, \'_2owEx _2cW1K\')]/text()')
        if not response:
            return None
        return self.get_ad_date_inner(response[0])

    # noinspection PyMethodMayBeStatic
    def get_phone(self, item):
        response = item.xpath("//a[contains(@data-marker, 'item-contact-bar/call')]/@href")
        phone_raw = response[0] if response else None
        if phone_raw is None:
            return None
        reg = re.compile('tel:([\d\+ -]+)', re.I)
        result = reg.findall(phone_raw)
        return result[0] if result else None

    # noinspection PyMethodMayBeStatic
    def get_mobile_address(self, response):
        raw_data = response.xpath("//span[@data-marker='delivery/location']/text()")
        return raw_data[0] if raw_data else None

    def is_agent(self, response):
        result = response.xpath('//div[@class="_1qEI9"]//div[@class = "_1Jm7J"]/text()')
        return 'Посредник' in result if result else None

    def get_title(self, response):
        result = response.xpath("//h1[@data-marker='item-description/title']//span[@class='CdyRB _3SYIM _2jvRd']/text()")
        return result[0] if result else None

    def get_price(self, response):
        data = response.xpath('//span[contains(@data-marker, \'item-description/price\')]/text()')
        if not data:
            return None
        raw = data[0].strip().replace(" ", "")
        regex = re.compile("\d+", re.I)
        result = regex.findall(raw)
        return result[0] if result else None


    # noinspection PyMethodMayBeStatic
    def get_room_count(self, response):
        data = self.get_title(response)
        if data is None:
            return None
        regexp = re.compile('(\d+)-к', re.I)
        count_raw = regexp.findall(data.strip())
        if not count_raw:
            return None
        count = int(count_raw[0])
        return '1 комната' if count == 1 else \
               '{} комнаты'.format(count) if 1 < count < 5 else \
               '{} комнат'.format(count)

    def get_category(self, response):
        data = self.get_room_count(response)
        if not data:
            data = response.xpath("//div[@class='_1Jm7J']/text()")
            return data[0] if data else None
        return data

    # noinspection PyMethodMayBeStatic
    def get_contact_name(self, response):
        data = response.xpath("//span[@class='_36-aX']/text()")
        if data is None:
            Logger.warning('Contact name not found')
        return data[0] if data else 'Неизвестно'

    def get_ad_date(self, response):
        raw_data = response.xpath("//span[@class='_1dHGK']/text()")
        if not raw_data:
            return None
        return self.get_ad_date_inner(raw_data[0])

    def get_city(self, response):
        address = self.get_mobile_address(response)
        items = address.split(',')
        return items[0] if items else "Неизвестно"

    async def process_ad(self, ad, session):
        page = await self.web_client.get(ad['link'], session)
        if page is None:
            return
        dom = html.fromstring(page)
        # TODO: add filtering
        ad['city'] = self.get_city(dom)

        ad['source'] = 1
        ad['order_type'] = 1
        ad['title'] = self.get_title(dom)
        ad['phone'] = self.get_phone(dom)
        ad['address'] = self.get_mobile_address(dom)
        ad['agent'] = self.is_agent(dom)
        ad['cost'] = self.get_price(dom)
       # ad['placed_at'] = self.get_ad_date(dom)
        ad['contact_name'] = self.get_contact_name(dom)
        ad['category'] = self.get_category(dom)
        Logger.info('Ad {} collected'.format(ad['link']))
        Logger.debug('Ad Values' + str(ad))
        if not ad['agent']:
            await self.web_client.post_ad(RemoteServerSettings.PUSH_URL, ad)

    async def process_page(self, url):
        session = self.web_client.get_session()
        page = await self.web_client.get(url, session)
        if page is None:
            self.web_client.close_session(session)
            return
        tree = html.fromstring(page)
        loop = asyncio.get_running_loop()
        tasks = []
        for item in tree.xpath('//div[contains(@class, "_328WR _2PXTe")]'):
            ad = self.get_ad_data_from_category(item)
            if ad['placed_at'] >= datetime.datetime.now() - datetime.timedelta(minutes=15) \
                    and not ad['link'] in self.duplicates:
                self.duplicates[ad['link']] = True
                tasks.append(loop.create_task(self.process_ad(ad, session)))

        if(len(tasks) > 0):
            await asyncio.wait(tasks)
        self.web_client.close_session(session)

    # noinspection PyMethodMayBeStatic
    async def process_pages(self):
        tasks = []
        loop = asyncio.get_running_loop()
        while True:
            for url in AvitoStandalone.get_start_urls():
                tasks.append(loop.create_task(self.process_page(url)))
            await asyncio.wait(tasks)
            await asyncio.sleep(61)

    def execute(self):
        Logger.info('Starting the scrapper...')
        asyncio.run(self.process_pages())
        Logger.info('Stopping the scrapper')


if __file__ == sys.argv[0]:
    app = AvitoStandalone()
    app.execute()
