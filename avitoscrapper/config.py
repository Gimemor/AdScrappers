class AvitoSettings:
    """
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

    LOCATION_PARTS = [ 'moscow' ]
    SCRAPPING_DEPTH = 1
    AD_DEPTH = 16
    RANGE_LEFT = 0
    RANGE_RIGHT = 6
    ITERATION_LIMIT = None
    ETERNAL_SCRAPPING = True
    EXCLUDE_AGENCY = False
    URL_FORMATS = [
        'https://www.avito.ru/{}/kvartiry?view=list&s=104',
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
    GET_STREET_URL = 'http://{}/api/get_streets'.format(BASE_URL)
    GET_DISTRICT = False

class ProxySettings:
    #PROXY_LIST = 'ips-zone-processed.txt'
    PROXY_LIST = 'ips-processed.test'
