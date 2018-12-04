import requests
import json
import os
import datetime


class Logger:
    __url = 'http://realty.zmservice.ru/api/create_log'

    @staticmethod
    def log(msg_type, message):
        result = {'message_type': msg_type, 'message': "[{}] {}".format(
            datetime.date.today(), message)}
        response = requests.post(Logger.__url,
                                 data=json.dumps({'grubber_log': result}),
                                 headers={'Accept': 'application/json', 'Content-Type': 'application/json'})

