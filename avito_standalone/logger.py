import requests
import json
import os
import datetime
import traceback
import logging
import sys
from config import RemoteServerSettings

logging.basicConfig(level=logging.DEBUG)


class Logger:
    __url = RemoteServerSettings.LOG_URL
    __send_to_remote = RemoteServerSettings.PUSH_LOGS

    ERR = 'ERR'
    DBG = 'DBG'
    WRN = 'WRN'
    INF = 'INF'

    @staticmethod
    def debug(message):
        Logger.log(Logger.DBG, message)

    @staticmethod
    def info(message):
        Logger.log(Logger.INF, message)

    @staticmethod
    def error(message):
        Logger.log(Logger.ERR, message)

    @staticmethod
    def warn(message):
        Logger.log(Logger.WRN, message)

    @staticmethod
    def log(msg_type, message):
        message = "[{}] {}".format(
            datetime.date.today(), message)

        if msg_type == Logger.DBG:
            logging.debug(message)
        elif msg_type == Logger.INF:
            logging.info(message)
        elif msg_type == Logger.WRN:
            logging.warning(message)
        elif msg_type == Logger.ERR:
            logging.error(message)
        else:
            Logger.log(Logger.ERR, 'Wrong log type, consider to add it or fix the error')
            logging.ERROR(message)

        if Logger.__send_to_remote:
            result = {'message_type': msg_type, 'message': message}
            response = requests.post(Logger.__url,
                                    data=json.dumps({'grubber_log': result}),
                                    headers={'Accept': 'application/json', 'Content-Type': 'application/json'})
            try:
                response.raise_for_status()
            except requests.HTTPError:
                logging.ERROR(traceback.format_exc())
                logging.ERROR(response.text)


if __file__ == sys.argv[0]:
    Logger.info('Hello, test')
