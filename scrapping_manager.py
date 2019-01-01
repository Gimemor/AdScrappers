import requests
import os
import sys
import time
import daemon
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from avitoscrapper.spiders.bazarpnz import BazarpnzSpider
from avitoscrapper.logger import Logger


class ScrappingDaemon:
    scrappers = [
        # AvitoRuSpider,
        # CianSpider,
        BazarpnzSpider
    ]

    def __init__(self):
        self.is_running = True
        sys.path.append(os.getcwd())

    # noinspection PyMethodMayBeStatic
    def run_scrapping(self):
        settings = get_project_settings()
        process = CrawlerProcess(settings)
        Logger.log("INFO", "Starting the realty scrappers.")
        for scrapper in ScrappingDaemon.scrappers:
            process.crawl(scrapper)
        process.start()
        Logger.log("INFO", "Stopping the realty scrappers")
        Logger.log("INFO", "Calling for the clean")
        r = requests.delete('http://realty.zmservice.ru/api/remove_old.json')
        print(r.content)

    # noinspection PyMethodMayBeStatic
    def execute(self):
        while self.is_running:
            print('run')
            time.sleep(10)


if __file__ == sys.argv[0]:
    with daemon.DaemonContext():
        daemon = ScrappingDaemon()
        daemon.execute()
