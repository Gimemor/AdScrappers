class AvitoSettings:
    LOCATION_PARTS = ['penza']
    SCRAPPING_DEPTH = None
    AD_DEPTH = None
    RANGE_LEFT = None
    RANGE_RIGHT = None
    ETERNAL_SCRAPPING = False
    EXCLUDE_AGENCY = False
    URL_FORMATS = [
        'https://www.avito.ru/{}/kvartiry?view=list&s=104',
        'https://www.avito.ru/{}/komnaty?view=list&s=104',
        'https://www.avito.ru/{}/doma_dachi_kottedzhi?view=list&s=104',
        'https://www.avito.ru/{}/zemelnye_uchastki?view=list&s=104',
        'https://www.avito.ru/{}/garazhi_i_mashinomesta?view=list&s=104',
        'https://www.avito.ru/{}/kommercheskaya_nedvizhimost?view=list&s=104',
    ]
    """
    LOCATION_PARTS = ['moskva' ]
    SCRAPPING_DEPTH = 1
    AD_DEPTH = None
    RANGE_LEFT = None
    RANGE_RIGHT = None
    ITERATION_LIMIT = None
    ETERNAL_SCRAPPING = True
    EXCLUDE_AGENCY = False
    URL_FORMATS = [
        'https://www.avito.ru/{}/kvartiry?s=104&sort=date',
    ]
"""



class BazarSettings:
    pass


class CianSettings:
    pass


class RemoteServerSettings:
    BASE_URL = 'realty.zmservice.ru'
    PUSH_URL = 'http://{}/api/create_order.json'.format(BASE_URL)
    LOG_URL = 'http://{}/api/create_log.json'.format(BASE_URL)
    DELETE_URL = 'http://{}/api/remove_old.json'.format(BASE_URL)
    GET_STREET_URL = 'http://{}/api/get_streets'.format(BASE_URL)
    GET_CATEGORY_URL = 'http://{}/api/get_categories'.format(BASE_URL)
    ADD_CATEGORY_URL = 'http://{}/api/create_category'.format(BASE_URL)
    GET_DISTRICT = True

class ProxySettings:
    #PROXY_LIST = 'ips-zone-processed.test'
    #PROXY_LIST = 'ips-small.test'
    PROXY_LIST = 'checked_proxies.txt'
