import requests
import json
import os
import datetime
from avitoscrapper.config import RemoteServerSettings

class Logger:
    __url = RemoteServerSettings.LOG_URL

    @staticmethod
    def log(msg_type, message):
        result = {'message_type': msg_type, 'message': "[{}] {}".format(
            datetime.date.today(), message)}
        response = requests.post(Logger.__url,
                                 data=json.dumps({'grubber_log': result}),
                                headers={'Accept': 'application/json', 'Content-Type': 'application/json'})

