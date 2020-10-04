# compute big dataframe to show adjacency matrix

import sys

import funcs

import pandas as pd
import psycopg2
import sys
import datetime

import re


def get_related_tags_with_search_word(search='python'):
    # compile
    try:
        pattern = r'%s' % (search)
        repattern = re.compile(pattern)
    except Exception as e:
        return pd.DataFrame()

    # get DataFrame
    item_df = pd.read_sql(sql="select tags_str from item_list where tags_str like %s", params=['%{}%'.format(search)],
                          con=funcs.get_connection())

    # split tags_str
    tag_df = item_df['tags_str'].str.split(',')
    tmp = []
    for tag in tag_df:
        tmp.append([e.strip() for e in tag])

    tag_df = pd.DataFrame(tmp)
    tag_all = pd.concat([tag_df[0], tag_df[1], tag_df[2], tag_df[3], tag_df[4]]).dropna()

    # get tags_str and count
    df = pd.DataFrame()
    for i, t in tag_all.value_counts().iteritems():
        if not repattern.match(i) and t > 500:
            df = pd.concat([df, pd.DataFrame({'count': t}, index=[i])])
    if df.empty:
        return pd.DataFrame(columns=[search])
    df.columns = [search]
    return df


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
print(con_df)
