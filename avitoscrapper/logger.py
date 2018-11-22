import requests


class Logger:
    __url = 'http://realty.zmservice.ru/api/create_log'

    @staticmethod
    def log(type, message):
        print(type, message)
