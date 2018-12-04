OrderTypes = {
    'RENT': 0,
    'RENT_OUT': 1,
    'BUY': 2,
    'SALE': 3
}

RU_MONTH_VALUES = {
    'января': 1,
    'февраля': 2,
    'марта': 3,
    'апреля': 4,
    'мая': 5,
    'июня': 6,
    'июля': 7,
    'августа': 8,
    'сентября': 9,
    'октября': 10,
    'ноября': 11,
    'декабря': 12,
}
RU_SHORT_MONTH_VALUES = { 
    'янв': 1,
    'фев': 2,
    'мар': 3,
    'апр': 4,
    'май': 5,
    'июн': 6,
    'июл': 7,
    'авг': 8,
    'сен': 9,
    'окт': 10,
    'ноя': 11,
    'дек': 12,
}


def month_format(date_str):
    date_str = date_str.lower()
    for k, v in RU_MONTH_VALUES.items():
        date_str = date_str.replace(k, str(v))
    for k, v in RU_SHORT_MONTH_VALUES.items():
        date_str = date_str.replace(k, str(v))
    return date_str + ' 2018'
