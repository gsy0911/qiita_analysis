import http.client
import datetime
import urllib.request
import json

import psycopg2
import http.client
import datetime
import urllib.request
import json
import requests
import time

import sys

import pandas as pd
import re


def insert_user(psgr, cur, json):
    for jsonstr in json:
        permanent_id = jsonstr['permanent_id']
        id = jsonstr['id']
        followers_count = jsonstr['followers_count']
        followees_count = jsonstr['followees_count']
        description = "null" if jsonstr['description'] == None else jsonstr['description']
        facebook_id = "null" if jsonstr['facebook_id'] == None else jsonstr['facebook_id']
        github_login_id = "null" if jsonstr['github_login_name'] == None else jsonstr['github_login_name']
        items_count = jsonstr['items_count']
        linkedin_id = "null" if jsonstr['linkedin_id'] == None else jsonstr['linkedin_id']
        twitter_screen_name = "null" if jsonstr['twitter_screen_name'] == None else jsonstr['twitter_screen_name']
        try:
            cur.execute(
                "insert into user_info (permanent_id, description, facebook_id, github_login_id, items_count, linkedin_id, twitter_screen_name) values (%s, %s, %s, %s, %s, %s, %s)",
                (
                permanent_id, description, facebook_id, github_login_id, items_count, linkedin_id, twitter_screen_name))
            cur.execute(
                "insert into user_list (permanent_id, id, followers_count, followees_count) values (%s, %s, %s, %s)",
                (permanent_id, id, followers_count, followees_count))
            psgr.commit()
        except Exception as e:
            psgr.commit()


def insert_single_user(psgr, cur, jsonstr):
    permanent_id = jsonstr['permanent_id']
    id = jsonstr['id']
    followers_count = jsonstr['followers_count']
    followees_count = jsonstr['followees_count']
    description = "null" if jsonstr['description'] == None else jsonstr['description']
    facebook_id = "null" if jsonstr['facebook_id'] == None else jsonstr['facebook_id']
    github_login_id = "null" if jsonstr['github_login_name'] == None else jsonstr['github_login_name']
    items_count = jsonstr['items_count']
    linkedin_id = "null" if jsonstr['linkedin_id'] == None else jsonstr['linkedin_id']
    twitter_screen_name = "null" if jsonstr['twitter_screen_name'] == None else jsonstr['twitter_screen_name']
    try:
        cur.execute(
            "insert into user_info (permanent_id, description, facebook_id, github_login_id, items_count, linkedin_id, twitter_screen_name) values (%s, %s, %s, %s, %s, %s, %s)",
            (permanent_id, description, facebook_id, github_login_id, items_count, linkedin_id, twitter_screen_name))
        cur.execute(
            "insert into user_list (permanent_id, id, followers_count, followees_count) values (%s, %s, %s, %s)",
            (permanent_id, id, followers_count, followees_count))
        psgr.commit()
    except Exception as e:
        psgr.commit()


def my_header(authorization):
    """
    # get qiita header with specific header
    """
    h = {
        "Authorization": f"Bearer {authorization}",
        "content-type": "application/json"
    }
    return h


def insert_item(psgr, cur, json):
    """
    """
    for jsonstr in json:
        permanent_id = jsonstr['user']['permanent_id']
        item_id = jsonstr['id']
        title = jsonstr['title']
        body = jsonstr['rendered_body']
        created_at = jsonstr['created_at']
        updated_at = jsonstr['updated_at']
        likes_count = jsonstr['likes_count']

        # concatenate
        tag_list = []
        for t in jsonstr['tags']:
            tag_list.append(t['name'])
        # check if works correctly
        tags_str = ",".join(tag_list)
        # insert check if already exists.
        try:
            cur.execute(
                "insert into item_list (item_id, permanent_id, title, body, created_at, updated_at, likes_count, tags_str) values (%s, %s, %s, %s, %s, %s, %s, %s)",
                (item_id, permanent_id, title, body, created_at, updated_at, likes_count, tags_str))
            psgr.commit()
        except Exception as e:
            psgr.commit()
        insert_single_user(psgr, cur, jsonstr['user'])


def update_table_state(psgr=None, cur=None, status="0", permanent_id=""):
    """
    #set table_name.status
    """
    try:
        cur.execute("update user_list_used2search set prcs_status = %s where permanent_id = %s ",
                    (status, permanent_id))
        psgr.commit()
    except Exception as e:
        print(e)
        psgr.commit()


def table_upd_ulu2s_processing(psgr=None, cur=None, permanent_id=""):
    update_table_state(psgr=psgr, cur=cur, status="1", permanent_id=permanent_id)


def table_upd_ulu2s_success(psgr=None, cur=None, permanent_id=""):
    update_table_state(psgr=psgr, cur=cur, status="0", permanent_id=permanent_id)


def table_upd_ulu2s_error(psgr=None, cur=None, permanent_id=""):
    update_table_state(psgr=psgr, cur=cur, status="9", permanent_id=permanent_id)


def update_table_count(psgr=None, cur=None, count="0", permanent_id=""):
    """
    #set table_name.status
    """
    try:
        cur.execute("update user_list_used2search set search_count = %s where permanent_id = %s ",
                    (count, permanent_id))
        psgr.commit()
    except Exception as e:
        print(e)
        psgr.commit()


def send_message(value1="This message", value2="is sent", value3="via IFTTT"):
    url = ""
    method = "POST"
    headers = {"Content-Type": "application/json"}
    obj = {
        "value1": value1,
        "value2": value2,
        "value3": value3
    }
    json_data = json.dumps(obj).encode("utf-8")

    # http request and POST
    request = urllib.request.Request(url, data=json_data, method=method, headers=headers)
    with urllib.request.urlopen(request) as responce:
        print(responce)


def get_connection():
    # https://ohke.hateblo.jp/entry/2017/06/23/230000
    # connection info
    connection_config = {
        'host': 'localhost',
        'database': 'qiita',
        'user': 'postgres',
        'password': 'postgres'
    }
    return psycopg2.connect(**connection_config)


def get_related_tags_with_search_word(search='Python'):
    # compile
    try:
        pattern = r'%s' % (search)
        repattern = re.compile(pattern)
    except Exception as e:
        return pd.DataFrame()

    # get DataFrame
    item_df = pd.read_sql(sql="select tags_str from item_list where tags_str like %s", params=['%{}%'.format(search)],
                          con=get_connection())

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
        if not repattern.match(i) and t > 200:
            df = pd.concat([df, pd.DataFrame({'count': t}, index=[i])])
    if df.empty:
        return pd.DataFrame(columns=[search])
    df.columns = [search]
    return df
