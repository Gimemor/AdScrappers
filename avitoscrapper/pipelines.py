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
    get_category_url = RemoteServerSettings.GET_CATEGORY_URL
    add_category_url = RemoteServerSettings.ADD_CATEGORY_URL

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

    street_map = {

    }

    def __init__(self):
        if RemoteServerSettings.GET_DISTRICT:
            self.street_map = AvitoscrapperPipeline.get_street_map()
        else:
            self.street_map = None
        cat_list = AvitoscrapperPipeline.get_categories()
        print(cat_list)
        self.categories = {}
        for i in cat_list: 
              self.categories[i['name']] = (i['id'], i['mapping'])

    @staticmethod
    def get_street_map():
        url = RemoteServerSettings.GET_STREET_URL
        response = requests.get(url).text
        print(response)
        objs = json.loads(response)
        map = dict((x['name'], x['district_id']) for x in objs)
        return map

    # noinspection PyMethodMayBeStatic
    def process_item(self, item, spider):
        result = dict(item)
        print(result)
        if item['category'] in AvitoscrapperPipeline.category_map:
            item['category'] = AvitoscrapperPipeline.category_map[item['category']]

        if 'image_list' in result:
            result['image_list'] = json.dumps(result['image_list'])

        result['placed_at'] = str(result['placed_at'])

        if self.street_map is not None:
            self.get_district(result)
            if 'district_id' in result:
                print(result['district_id'])

        category_found = False
        for key in self.categories:
            if key == item['category']:
                result['category_id'] = self.categories[key][0]
                category_found = True
                break
            raw_mapping = self.categories[key][1]
            if not raw_mapping:
                continue
            mapping = raw_mapping.split("|")
            if item['category'] in mapping:
                result['category_id'] = self.categories[key][0]
                category_found = True

        if not category_found:
            cat_result = AvitoscrapperPipeline.add_category(item['category'])
            self.categories[item['category']] = (cat_result['id'], None)
            result['category_id'] = self.categories[item['category']]

        response = requests.post(AvitoscrapperPipeline.push_url,
                                 data=json.dumps({'order': result}),
                                 headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
        print(response.content)
        return item

    @staticmethod
    def get_categories():
        response = requests.get(AvitoscrapperPipeline.get_category_url,
		headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
        data = json.loads(response.text)
        print(data)
        return data

    @staticmethod
    def add_category(name):
        result = {'name': name }
        print(json.dumps({'category': result}))
        response = requests.post(AvitoscrapperPipeline.add_category_url, 
               data=json.dumps({'category': result}),
               headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
        result = json.loads(response.text)

        print(result)
        return result  
    @staticmethod
    def normalize_string(s):
        if s is None:
            return None
        return s.lower().replace('ё', 'е')

    def get_district(self, item):
        title = AvitoscrapperPipeline.normalize_string(item['title'] if 'title' in item else None)
        address = AvitoscrapperPipeline.normalize_string(item['address'] if 'address' in item else None)
        if title:
            for key in self.street_map:
                if key in title:
                    item['district_id'] = self.street_map[key]
                    return

        if address:
            for key in self.street_map:
                if key in address:
                    item['district_id'] = self.street_map[key]
                    return
        return


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
