class AvitoSettings:
    LOCATION_PARTS = ['moskva']
    SCRAPPING_DEPTH = 1
    AD_DEPTH = 16
    ETERNAL_SCRAPPING = True
    URL_FORMATS = [
        'https://www.avito.ru/{}/kvartiry/sdam/na_dlitelnyy_srok?view=list&s=104',
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
    PROXY_LIST = '../ips-processed.test'
