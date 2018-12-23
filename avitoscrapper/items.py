# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy.loader.processors import TakeFirst


class Ad(scrapy.Item):
    title = scrapy.Field(output_processor=TakeFirst())
    cost = scrapy.Field(output_processor=TakeFirst())
    source = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    order_type = scrapy.Field(output_processor=TakeFirst())
    placed_at = scrapy.Field(output_processor=TakeFirst())
    city = scrapy.Field(output_processor=TakeFirst())
    floor = scrapy.Field(output_processor=TakeFirst())
    flat_area = scrapy.Field(output_processor=TakeFirst())
    plot_size = scrapy.Field(output_processor=TakeFirst())
    phone = scrapy.Field(output_processor=TakeFirst())
    address = scrapy.Field(output_processor=TakeFirst())
    category = scrapy.Field(output_processor=TakeFirst())
    agent = scrapy.Field(output_processor=TakeFirst())
    description = scrapy.Field(output_processor=TakeFirst())
    floor_count = scrapy.Field(output_processor=TakeFirst())
    contact_name = scrapy.Field(output_processor=TakeFirst())
    image_list = scrapy.Field()
    district = scrapy.Field(output_processor=TakeFirst())
