import scrapy
import requests
import os
import sys
import json
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from avitoscrapper.spiders.avito_ru import AvitoRuSpider
from avitoscrapper.spiders.cian import CianSpider
from avitoscrapper.spiders.bazarpnz import BazarpnzSpider
from xvfbwrapper import Xvfb

push_url = 'http://realty.zmservice.ru/api/create_order.json'

scrappers = [
   # AvitoRuSpider,
    CianSpider,
   # BazarpnzSpider,
]

with Xvfb() as xvfb:
    # os.environ["http_proxy"] = "http://localhost:8888"
    sys.path.append(os.getcwd())
    output_file = 'output.json'
    if os.path.isfile(output_file):
        os.remove(output_file)
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    for scrapper in scrappers:
        process.crawl(scrapper)
    process.start()
    with open(output_file, 'r') as f:
        text = f.read()
        items = json.loads(text.encode("utf8"))
        for item in items:
            response = requests.post(push_url, data=json.dumps({'order': item}),
                                     headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
            print(response.content)
