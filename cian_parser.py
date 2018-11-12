


user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'

for request in requests_list:

    url = base_url_format + request
    referer = referer_format + request

    time.sleep(3.0)

