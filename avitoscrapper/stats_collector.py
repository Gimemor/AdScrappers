from scrapy import signals
from twisted.internet.task import LoopingCall


class PersistStats(object):

    def __init__(self, interval):
        self.interval = interval
        self.tasks = {}

    @classmethod
    def from_crawler(cls, crawler):
        obj = cls(crawler.settings.getint('PERSIST_STATS_INTERVAL', 60))
        crawler.signals.connect(obj.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(obj.spider_closed, signal=signals.spider_closed)
        return obj

    def spider_opened(self, spider):
        task = self.tasks[spider.name] = LoopingCall(self.perist_stats, spider)
        task.start(self.interval)

    def spider_closed(self, spider):
        task = self.tasks.pop(spider.name)
        task.stop()

    # noinspection MethodMayBeStatic
    def perist_stats(self, spider):
        # TODO: store stats somewhere.
        data = spider.crawler.stats.get_stats()
        spider.logger.info("Persisting stats:\n%s", data)
