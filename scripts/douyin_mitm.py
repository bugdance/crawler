#! /usr/bin/python3
# -*- coding: utf-8 -*-
""" View Test
@@ package jobs
@@ author pyLeo <lihao@372163.com>

? Problem
! Alert
// Abandon
*** Todo
"""

# # # @@ Import current path
import sys
sys.path.append('..')
# # # @@ Import package
import demjson
import os
import pymongo
from mitmproxy.http import flow
# from libmproxy.protocol.http import decoded
import re


mongo = pymongo.MongoClient('mongodb://localhost:27017', maxPoolSize=None, serverSelectionTimeoutMS=10)
d_db = mongo['douyin']
d_col1 = d_db['base']
# d_col2 = d_db['works']
d_col3 = d_db['followers']
# d_col4 = d_db['followings']
d_col5 = d_db['shops']


def parse_to_regex(regex_syntax: str = "", source_string: str = "") -> tuple:
    """Parse to regex. 解析匹配。

    Args:
        regex_syntax (str): The regex syntax. 正则语法。
        source_string (str): The source string. 来源数据。

    Returns:
        tuple: Return a tuple(a string, a list of strings).
    """
    try:
        return_data = re.findall(regex_syntax, source_string, re.S)
    except Exception as ex:
        return "", []
    else:
        if not return_data:
            return "", []

        return return_data[0], return_data



def response(flow: flow):

    request_url = flow.request.url
    # # 用户基础
    if "/aweme/v1/user/?" in request_url and "sec_user_id" in request_url:
        user_id, temp_list = parse_to_regex("sec_user_id=(.*?)&", request_url)
        if user_id:
            # with decoded(flow.response):  # automatically decode gzipped responses.
            response_page = flow.response.text
            result_dict = demjson.decode(response_page, encoding='utf-8')
            if result_dict:
                result_data = result_dict.get("user", {})
                d_col1.update_one(
                    {"_id": user_id},
                    {'$set': {"user": result_data}},
                    upsert=True
                )

    # # 40粉丝
    elif "/aweme/v1/user/follower/list/?" in request_url and "sec_user_id" in request_url:
        user_id, temp_list = parse_to_regex("sec_user_id=(.*?)&", request_url)
        if user_id:
            response_page = flow.response.text
            result_dict = demjson.decode(response_page, encoding='utf-8')
            if result_dict:
                result_data = result_dict.get("followers", [])
                d_col3.update_one(
                    {"_id": user_id},
                    {'$set': {"followers": result_data}},
                    upsert=True
                )                

    # # # 40关注
    # elif "/aweme/v1/user/following/list/?" in request_url and "sec_user_id" in request_url:
    #     user_id, temp_list = parse_to_regex("sec_user_id=(.*?)&", request_url)
    #     if user_id:
    #         response_page = flow.response.text
    #         result_dict = demjson.decode(response_page, encoding='utf-8')
    #         if result_dict:
    #             result_data = result_dict.get("followings", [])
    #             d_col4.update_one(
    #                 {"_id": user_id},
    #                 {'$set': {"followings": result_data}},
    #                 upsert=True
    #             )

    # # 橱窗
    elif "/aweme/v1/shop/header/?" in request_url and "sec_author_id" in request_url:
        user_id, temp_list = parse_to_regex("sec_author_id=(.*?)&", request_url)
        if user_id:
            response_page = flow.response.text
            result_dict = demjson.decode(response_page, encoding='utf-8')
            if result_dict:
                result_data = result_dict.get("reputation", {})
                d_col5.update_one(
                    {"_id": user_id},
                    {'$set': {"reputation": result_data}},
                    upsert=True
                )
    # # 货品
    elif "/aweme/v1/shop/product/list/?" in request_url and "sec_author_id" in request_url:
        user_id, temp_list = parse_to_regex("sec_author_id=(.*?)&", request_url)
        if user_id:
            response_page = flow.response.text
            result_dict = demjson.decode(response_page, encoding='utf-8')
            if result_dict:
                result_data = result_dict.get("products", [])
                if result_data:
                    d_col5.update_one(
                        {"_id": user_id},
                        {'$addToSet': {"products": result_data}},
                        upsert=True
                    )



    # # # 15个作品
    # elif "/aweme/v1/aweme/post/?" in request_url and "sec_user_id" in request_url:
    #     user_id, temp_list = parse_to_regex("sec_user_id=(.*?)&", request_url)
    #     if user_id:
    #         response_page = flow.response.text
    #         result_dict = demjson.decode(response_page, encoding='utf-8')
    #         if result_dict:
    #             result_data = result_dict.get("aweme_list", [])
    #             d_col2.update_one(
    #                 {"_id": user_id},
    #                 {'$set': {"aweme_list": result_data}},
    #                 upsert=True
    #             )




if __name__ == '__main__':
    os.system("mitmdump -p8888 -s douyin_mitm.py")


