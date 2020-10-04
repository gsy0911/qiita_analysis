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
num = 0

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

# print(type(p_df))
# print(p_df.head())

sys.exit()

tmp_df = pd.DataFrame()
con_df = pd.DataFrame()

tag_df = pd.read_sql(sql="select tag_name from tag_appear_count where count >= 500 and calc_date = %s",
                     params=['2019-1-4'], con=funcs.get_connection())
for tag in tag_df['tag_name']:
    tmp_df = get_related_tags_with_search_word(tag)
    if con_df.empty:
        con_df = tmp_df
    elif not tmp_df.empty:
        con_df = con_df.join(tmp_df, how='outer')

con_df = con_df.fillna(0)
# print(con_df)
