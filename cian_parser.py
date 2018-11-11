import requests
import os
import time
from pandas import *
import json
http_proxy  = "http://127.0.0.1:8888"
https_proxy = "https://127.0.0.1:8888"
ftp_proxy   = "ftp://127.0.0.1:8888"

# class CianParser:


def get_column(df, i, j):
    return df[df.columns[j]][i]


user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
base_url_format = 'https://penza.cian.ru/export/xls/offers'
referer_format = 'https://penza.cian.ru/cat.php'

file = 'offers.xlsx'
for request in requests_list:

    url = base_url_format + request
    referer = referer_format + request
    requests.get(referer, headers={'referer': referer,  'User-Agent': user_agent})
    time.sleep(2)
    response = requests.get(url, headers={'referer': referer,  'User-Agent': user_agent})
    if response.status_code == 200:
        with open(file, 'wb') as f:
            f.write(response.content)
    df = pandas.read_excel(file)
    for i in df.index:
        item = dict()
        item['title'] = get_column(df, i, 16)
        item['source'] = 3
        item['link'] = get_column(df, i, 20)
        item['contact_name'] = None
        item['order_type'] = ""
        item['placed_at'] = ""
        item['city'] = "Пенза"
        item['cost'] = get_column(df, i, 7)
        item['floor'] = get_column(df, i, 9)
        item['flat_area'] = get_column(df, i, 4)
        item['plot_size'] = get_column(df, i, 2)
        item['phone'] = get_column(df, i, 8)
        item['address'] = get_column(df, i, 3)
        item['category'] = get_column(df, i, 1)
        item['agent'] = get_column(df, i, 2)
        item['description'] = get_column(df, i, 10)
        item['floor_count'] = get_column(df, i, 5)
        item['contact_name'] = get_column(df, i, 2)
        item['image_list'] = get_column(df, i, 2)
        print(json.dumps(item, ensure_ascii=False))
    os.remove(file)
    time.sleep(3.0)

