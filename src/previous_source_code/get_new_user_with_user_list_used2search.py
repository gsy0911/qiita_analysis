import sys
import funcs

import http.client
import datetime
import urllib.request
import json

import psycopg2
import http.client
import datetime
import requests

fetched_permanent_id = ""
fetched_user_id = ""
fetched_count = 0

with psycopg2.connect("") as psgr:
	with psgr.cursor() as cur:
		cur.execute("select * from user_list_used2search where search_count = 0 and prcs_status = 0")
		row = cur.fetchall()
		for r in row:
			print(r)
			fetched_permanent_id = str(r[0])
			fetched_user_id = r[1]
			fetched_count = int(r[2])

			# update state = 1(processing)
			funcs.table_upd_ulu2s_processing(psgr=psgr, cur=cur, permanent_id=fetched_permanent_id)

			# get user list with fetched_user_id
			url = "https://qiita.com/api/v2/users/" + fetched_user_id + "/followers"
			p={
				'per_page': 100,
				'page': 1
			}

			r = requests.get(url, headers=funcs.my_header(), params=p)
			# 取得上限対策
			total_count = 0
			try:
				total_count = int(r.headers['Total-Count'])
			except Exception as e:
				print(e)
				continue
			#check if works correctly
			for i in range(total_count):
				p['page'] = i + 1
				r = requests.get(url, headers=funcs.my_header(), params=p)
				# API limitation
				print("remaining : " + str(r.headers['Rate-Remaining']))

			try:
				funcs.insert_user(psgr, cur, r.json())
			except Exception as e:
				psgr.commit()
				# update state = 9(process finishes with error)
				funcs.table_upd_ulu2s_error(psgr=psgr, cur=cur, permanent_id=fetched_permanent_id)
				continue
			print(fetched_permanent_id)
			# update state = 0(process finishes successfully)
			print("come")
			funcs.table_upd_ulu2s_success(psgr=psgr, cur=cur, permanent_id=fetched_permanent_id)
			funcs.update_table_count(psgr=psgr, cur=cur, count="1", permanent_id=fetched_permanent_id)