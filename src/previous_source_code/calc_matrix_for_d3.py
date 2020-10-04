# this program is to make row values to paste javascript directory

import sys
import funcs

import pandas as pd
import psycopg2
import sys
import datetime

import re

search = 'Python'
left = "{"
tag = "a"
right = "}"
col_num = 0
col_count = 0
index_num = 0

tmp_df = pd.DataFrame()
con_df = pd.DataFrame()

tag_df = pd.read_sql(sql="select tag_name from tag_appear_count where count >= 10000 and calc_date = %s",
                     params=['2019-1-7'], con=funcs.get_connection())
for tag in tag_df['tag_name']:
    tmp_df = funcs.get_related_tags_with_search_word(tag)
    if con_df.empty:
        con_df = tmp_df
    elif not tmp_df.empty:
        con_df = con_df.join(tmp_df, how='outer')

con_df = con_df.fillna(0)
print(con_df.head())

col_count = len(con_df.columns)

# sys.exit()


for column_name, item in con_df.iteritems():
    index_num = col_count
    #	print('{0} id: {1}, label: "{2}" {3},'.format(left, str(col_num), column_name, right))
    #	print(column_name)
    for i in item:
        if i > 1:
            #			print('{0} id: "{1}", label: "{2}" {3},'.format(left, str(index_num), i[0], right))
            print('{0} source: {1}, target: {2} {3},'.format(left, str(col_num), str(index_num), right))
        index_num = index_num + 1
    #		print(num)
    col_num = col_num + 1

sys.exit()

index_num = col_count + 1
for index_name, row in con_df.iterrows():
    print('{0} id: {1}, label: "{2}" {3},'.format(left, str(index_num), index_name, right))
    index_num = index_num + 1

p_df = funcs.get_related_tags_with_search_word(search=search)

print('{0} id: "{1}", label: "{1}" {2},'.format(left, search, right))

num = 1
for d in p_df.iterrows():
    tag = str(d[0])
    print('{0} id: "{1}", label: "{2}" {3},'.format(left, str(num), tag, right))
    num = num + 1

num = 1
for d in p_df.iterrows():
    tag = str(d[0])
    print('{0} source: 0, target: {1} {2},'.format(left, str(num), right))
    num = num + 1
