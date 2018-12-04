# -*- coding: utf-8 -*-

import json
import codecs

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import requests


class AvitoscrapperPipeline(object):
    push_url = 'http://realty.zmservice.ru/api/create_order.json'

    # noinspection PyMethodMayBeStatic
    def process_item(self, item, spider):
        result = dict(item)
        print(result)
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
        self.file = codecs.open('scraped_data_utf8.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()