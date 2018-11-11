import scrapy
import requests
import os
import json
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project   import get_project_settings
from avitoscrapper.spiders.avito_ru import AvitoRuSpider
from avitoscrapper.spiders.cian import CianSpider
from avitoscrapper.spiders.bazarpnz import BazarpnzSpider

push_url = 'http://realty.zmservice.ru/api/create_order.json'

scrappers = [
    # (AvitoRuSpider, 'avito.json'),
    # (CianSpider, 'cian.json'),
    (BazarpnzSpider, 'bazarspider.json')
]
os.environ["http_proxy"] = "http://localhost:8888"

for scrapper in scrappers:
    """

    if os.path.isfile(scrapper[1]):
        os.remove(scrapper[1])
    settings = get_project_settings()
    settings['FEED_URL'] = scrapper[1]
    process = CrawlerProcess(settings)
    process.crawl(scrapper[0])
    process.start()
    """
    with open('output.json', 'r') as f:
        text = f.read()
        items = json.loads(text.encode("utf8"))
        for item in items:
            response = requests.post(push_url, data=json.dumps({'order': item}),
                                     headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
            print(response.content)
