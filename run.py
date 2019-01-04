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
from avitoscrapper.config import RemoteServerSettings

scrappers = [
 AvitoRuSpider,
 #CianSpider,
 #BazarpnzSpider
]

sys.path.append(os.getcwd())
settings = get_project_settings()
process = CrawlerProcess(settings)
Logger.log("INFO", "Starting the realty scrappers.")
for scrapper in scrappers:
    process.crawl(scrapper)
process.start()
Logger.log("INFO", "Stopping the realty scrappers")
Logger.log("INFO", "Calling for the clean")
r = requests.delete(RemoteServerSettings.DELETE_URL)
print(r.content)
