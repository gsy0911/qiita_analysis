import sys
import funcs

import psycopg2
import time
import os
import requests
import math
import datetime

url = 'https://qiita.com/api/v2/items'

today = datetime.datetime.now()
prev_day = today - datetime.timedelta(days=1)

start = str(prev_day.year) + "-" + str(prev_day.month) + "-" + str(prev_day.day)
end = str(today.year) + "-" + str(today.month) + "-" + str(today.day)

start = "2019-1-15"
end = "2019-1-20"

# in order not to over the limitation accessing 1000 times in one hour
sleep_sec = 3.6

p = {
    'per_page': 100,
    'page': 1,
    'query': 'created:>{} created:<{}'.format(start, end)
}

r = requests.get(url, params=p, headers=funcs.my_header())
# item count in the whole day
total_count = int(r.headers['Total-Count'])

print(p)

# print("execute day :=" + start)
# print("total_count :=" + str(total_count))
# print("remaining : " + str(r.headers['Rate-Remaining']))

# sys.exit()

# to get all items
loop_count = math.ceil((total_count - 100) / 100)

with psycopg2.connect("") as psgr:
    with psgr.cursor() as cur:
        funcs.insert_item(psgr, cur, r.json())

        for i in range(loop_count):
            time.sleep(sleep_sec)  # アクセス制限対策
            print("loop : " + str(i + 2))
            p['page'] = i + 2

            r = requests.get(url, params=p, headers=funcs.my_header())
            print("remaining : " + str(r.headers['Rate-Remaining']))
            funcs.insert_item(psgr, cur, r.json())
