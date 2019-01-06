# -*- coding: utf-8 -*-

import json
import codecs

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import requests
from .config import RemoteServerSettings


class AvitoscrapperPipeline(object):
    push_url = RemoteServerSettings.PUSH_URL

    category_map = {
        # AVITO
        "Земельные участки": "Участки",
        "Дома, дачи, коттеджи": "Дома",
        "Коммерческая недвижимость": "Коммерция",
        "Гаражи и машиноместа": "Гаражи",
        # BAZAR
        "С общей кухней": "Комнаты",
        "Студия": " Студии",
        "Дачи": "Дома",
        # CIAN
        "Продажа квартир-студий в Пензе": "Студии",
        "Продажа комнат в Пензе": "Комнаты",
        "Продажа домов в Пензенской области": "Дома"
    }

    # noinspection PyMethodMayBeStatic
    def process_item(self, item, spider):
        result = dict(item)
        print(result)
        if item['category'] in AvitoscrapperPipeline.category_map:
            item['category'] = AvitoscrapperPipeline.category_map[item['category']]

        if 'image_list' in result:
            result['image_list'] = json.dumps(result['image_list'])

        result['placed_at'] = str(result['placed_at'])
        response = requests.post(AvitoscrapperPipeline.push_url,
                                 data=json.dumps({'order': result}),
                                 headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
        print(response.content)
        return item


class JsonWithEncodingPipeline(object):
    def __init__(self):
        pass

    def process_item(self, item, spider):
        file = codecs.open('scraped_data_utf8.json', 'w', encoding='utf-8')
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        file.write(line)
        file.close()
        return item

    def spider_closed(self, spider):
        pass
