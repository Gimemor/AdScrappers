import sys
import random
# noinspection UnresolvedReference
from config import ProxySettings
from logger import Logger

class ProxyManager:
    def __init__(self, settings):
        self.proxies = self.get_proxies(settings)
        pass

    @staticmethod
    def get_proxies(settings):
        with open(settings.PROXY_LIST) as f:
            return [
                {'http': proxy.strip(), 'https': proxy.strip()} for proxy in f.readlines()
            ]

    def get_random_proxy(self, except_list=[]):
        current_proxy = None
        while current_proxy is None or current_proxy in except_list:
            current_proxy = random.choice(self.proxies)
        return current_proxy

    def delete_proxy(self, current_proxy):
        self.proxies.remove(current_proxy)
        if len(proxy) == 0:
            Logger.debug('PROXY LIST IS EMPTY')
            raise Exception('Empty Proxy List')


if __file__ == sys.argv[0]:
    manager = ProxyManager(ProxySettings)
    proxy = manager.get_random_proxy()
