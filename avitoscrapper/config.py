
class AvitoSettings:
    LOCATION_PARTS = ['moskva', 'moskovskaya_oblast']
    SCRAPPING_DEPTH = 4
    ETERNAL_SCRAPPING = False


class BazarSettings:
    pass


class CianSettings:
    pass


class RemoteServerSettings:
    BASE_URL = 'moscow.zmservice.ru'
    PUSH_URL = 'http://{}/api/create_order.json'.format(BASE_URL)
    LOG_URL = 'http://{}/api/create_log.json'.format(BASE_URL)
    DELETE_URL = 'http://{}/api/remove_old.json'.format(BASE_URL)
