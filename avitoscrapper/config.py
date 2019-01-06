class AvitoSettings:
    LOCATION_PARTS = ['moskva', 'moskovskaya_oblast']
    SCRAPPING_DEPTH = 1
    ETERNAL_SCRAPPING = True
    URL_FORMATS = [
        'https://www.avito.ru/{}/kvartiry/sdam?view=list&s=104',
        'https://www.avito.ru/{}/komnaty/sdam?view=list&s=104',

        'https://www.avito.ru/{}/kvartiry/snimu?view=list&s=104',
        'https://www.avito.ru/{}/komnaty/snimu?view=list&s=104',
    ]


class BazarSettings:
    pass


class CianSettings:
    pass


class RemoteServerSettings:
    BASE_URL = 'moscow.zmservice.ru'
    PUSH_URL = 'http://{}/api/create_order.json'.format(BASE_URL)
    LOG_URL = 'http://{}/api/create_log.json'.format(BASE_URL)
    DELETE_URL = 'http://{}/api/remove_old.json'.format(BASE_URL)


class ProxySettings:
    PROXY_LIST = 'ips-processed.test'
