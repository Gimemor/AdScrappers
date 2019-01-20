
class AvitoSettings:
    LOCATION_PARTS = ['moskva']
    SCRAPPING_DEPTH = 1
    AD_DEPTH = 16
    RANGE_LEFT = 0
    RANGE_RIGHT = 16
    ITERATION_LIMIT = 10000
    ETERNAL_SCRAPPING = True
    EXCLUDE_AGENCY = True
    URL_FORMATS = [
        'https://www.avito.ru/{}/kvartiry?s=104&sort=date',
    ]
    BASE_MOBILE = 'https://m.avito.ru'

class RemoteServerSettings:
    BASE_URL = 'moscow.zmservice.ru'
    PUSH_URL = 'http://{}/api/create_order.json'.format(BASE_URL)
    LOG_URL = 'http://{}/api/create_log.json'.format(BASE_URL)
    DELETE_URL = 'http://{}/api/remove_old.json'.format(BASE_URL)
    GET_STREET_URL = 'http://{}/api/get_streets'.format(BASE_URL)
    GET_DISTRICT = False
    PUSH_LOGS = False

class ProxySettings:
    #PROXY_LIST = 'ips-zone-processed.txt'
    PROXY_LIST = '../ips-processed.test'
