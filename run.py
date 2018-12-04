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
from avitoscrapper.logger import Logger
from xvfbwrapper import Xvfb


scrappers = [
  AvitoRuSpider,
#  CianSpider,
# BazarpnzSpider
]

#os.environ["http_proxy"] = "http://localhost:8888"
#os.environ["http_proxy"] = "lum-customer-hl_d97be066-zone-zone1-ip-66.78.37.237:ysjouo4rfjja@zproxy.lum-superproxy.io:22225"

with Xvfb() as xvfb:
    sys.path.append(os.getcwd())
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    Logger.log("INFO", "Starting the realty scrappers.")
    for scrapper in scrappers:
        process.crawl(scrapper)
    process.start()
    Logger.log("INFO", "Stopping the realty scrappers")
    Logger.log("INFO", "Calling for the clean")
    r = requests.delete('http://realty.zmservice.ru/api/remove_old.json')
    print(r.content)
