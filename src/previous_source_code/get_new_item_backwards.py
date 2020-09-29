# to get all qiita item with going backwards
# modified dramatically when 01/12

import sys
import funcs

import psycopg2
import time
import os
import requests
import sys
import math
import datetime

def get_new_item_back(psgr, cur):
	# in order not to over the limitation accessing 1000 times in one hour
	sleep_sec = 3.6

	url = 'https://qiita.com/api/v2/items'
	# get start day
	cur.execute("select * from value_list where key = 'get_item_start'")
	row = cur.fetchall()
	for r in row:
		end = r[1]

	new_end_day = datetime.datetime.strptime(end, "%Y-%m-%d")
	new_start_day = new_end_day - datetime.timedelta(days=5)
	start = str(new_start_day.year) + "-" + str(new_start_day.month) + "-" + str(new_start_day.day)
	end = str(new_end_day.year) + "-" + str(new_end_day.month) + "-" + str(new_end_day.day)

	p = {
		'per_page': 100,
		'page':1,
		'query': 'created:>{} created:<{}'.format(start, end)
	}
	r = requests.get(url, params=p, headers=funcs.my_header())

	# item count in the whole day
	total_count = int(r.headers['Total-Count'])
	# to get all items
	loop_count = math.ceil((total_count - 100)/100)
	if total_count > 10000:
		sys.exit()

	funcs.insert_item(psgr, cur, r.json())
	for i in range(loop_count):
		# for access limitation
		time.sleep(sleep_sec)
		print("loop : "+str(i+2))
		p['page'] = i + 2
		r = requests.get(url, params=p, headers=funcs.my_header())
		print("remaining : " + str(r.headers['Rate-Remaining']))
		funcs.insert_item(psgr, cur, r.json())

	# update database state
	cur.execute("update value_list set value = %s where key = %s ", (start, 'get_item_start'))
	cur.execute("update value_list set value = %s where key = %s ", (end, 'get_item_end'))
	psgr.commit()



if __name__ == "__main__":
	with psycopg2.connect("") as psgr:
		with psgr.cursor() as cur:
			get_new_item_back(psgr, cur)