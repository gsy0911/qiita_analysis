# dramatically changed when 01/12

import sys
import funcs

import psycopg2
import time
import os
import requests
import math
import datetime


def get_new_item(page=1, start="2019-1-3", end="2019-1-1"):
	url = 'https://qiita.com/api/v2/items'
	sleep_sec = 3.6

	p = {
        'per_page': 100,
        'page':1,
        'query': 'created:>{} created:<{}'.format(start, end)
	}
	p['page'] = page
	# get request
	r = requests.get(url, params=p, headers=funcs.my_header())
	return r



url = 'https://qiita.com/api/v2/items'

today = datetime.datetime.now()
prev_day = today - datetime.timedelta(days=2)

start = '{}-{}-{}'.format(str(prev_day.year), str(prev_day.month), str(prev_day.day))
end = '{}-{}-{}'.format(str(today.year), str(today.month), str(today.day))


# in order not to over the limitation accessing 1000 times in one hour
sleep_sec = 3.6

p = {
	'per_page': 100,
	'page':1,
	'query': 'created:>{} created:<{}'.format(start, end)
}

r = requests.get(url, params=p, headers=funcs.my_header())

# item count in the whole day
total_count = int(r.headers['Total-Count'])
#print("execute day :=" + start)
#print("total_count :=" + str(total_count))
#print("remaining : " + str(r.headers['Rate-Remaining']))

# to get all items
loop_count = math.ceil((total_count - 100)/100)

with psycopg2.connect("") as psgr:
	with psgr.cursor() as cur:
		funcs.insert_item(psgr, cur, r.json())

		for i in range(loop_count):
			# for access limitation
			time.sleep(sleep_sec)
			print("loop : "+str(i+2))
			p['page'] = i + 2

			r = requests.get(url, params=p, headers=funcs.my_header())
			print("remaining : " + str(r.headers['Rate-Remaining']))
			funcs.insert_item(psgr, cur, r.json())

#if __name__ == "__main__":
#	today = datetime.datetime.now()
#	prev_day = today - datetime.timedelta(days=2)

#	start = '{}-{}-{}'.format(str(prev_day.year), str(prev_day.month), str(prev_day.day))
#	end = '{}-{}-{}'.format(str(today.year), str(today.month), str(today.day))

#	r = get_new_item(start=start, end=end)
#	total_count = int(r.headers['Total-Count'])
	# to get all items
#	loop_count = math.ceil((total_count - 100)/100)

#	with psycopg2.connect("") as psgr:
#		with psgr.cursor() as cur: