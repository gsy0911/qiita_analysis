import sys
import funcs

import datetime
import urllib.request
import json

import psycopg2
import datetime
import requests

p={
	'per_page': 100,
	'page': 1
}

for i in range(98):
	p['page'] = i + 1
	print(p)
	url = "https://qiita.com/api/v2/users"
	r = requests.get(url, headers=funcs.my_header(), params=p)

	print("remaining : " + str(r.headers['Rate-Remaining']))


	with psycopg2.connect("") as psgr:
		with psgr.cursor() as cur:
			funcs.insert_user(psgr, cur, r.json())
