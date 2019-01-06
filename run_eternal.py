import scrapy
import sys
import os
import time
import scrapy.crawler as crawler
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from multiprocessing import Process, Queue
from twisted.internet import reactor
from avitoscrapper.spiders.avito_ru import AvitoRuSpider
from avitoscrapper.spiders.cian import CianSpider
from avitoscrapper.spiders.bazarpnz import BazarpnzSpider
from avitoscrapper.logger import Logger

# the wrapper to make it run more times
scrappers = [
 AvitoRuSpider,
 #CianSpider,
 #BazarpnzSpider
]

configure_logging()

sys.path.append(os.getcwd())
settings_file_path = 'avitoscrapper.settings'  # The path seen from root, ie. from main.py
os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
os.chdir('avitoscrapper')

def run_spider():
    def f(q):
        try:
            runner = crawler.CrawlerRunner(get_project_settings())
            deferred = runner.crawl(AvitoRuSpider)
            deferred.addBoth(lambda _: reactor.stop())
            reactor.run()
            q.put(None)
        except Exception as e:
            q.put(e)

    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result


Logger.log("INFO", "Starting the realty scrappers.")
while True:
    run_spider()
    print('test')
    time.sleep(10)

