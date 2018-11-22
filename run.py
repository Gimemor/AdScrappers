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


scrappers = [
  AvitoRuSpider,
  CianSpider,
  BazarpnzSpider
]
#os.environ["http_proxy"] = "http://localhost:8888"

with Xvfb() as xvfb:
    sys.path.append(os.getcwd())
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    for scrapper in scrappers:
        process.crawl(scrapper)
    process.start()

