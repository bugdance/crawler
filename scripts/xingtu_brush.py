#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> xingtu brush
@@..> package scripts
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> import current path
import sys
sys.path.append('..')
# @@..> base import
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import random
# @@..> import utils
from utils.auto_tools import AutoAct
from utils.base_tools import BaseAct, LogAct
from utils.json_tools import JsonAct
from utils.net_tools import NetAct
from utils.pool_tools import PoolAct
from utils.num_tools import NumAct, TimeAct
from utils.str_tools import StrAct, UrlAct


logger, handler = LogAct.init_log("xingtu_brush.log")
auto = AutoAct()
auto.logger = logger
sessAct = NetAct()
seAct = NetAct()
sessAct.logger = logger
seAct.logger = logger

TimeAct.logger = logger
JsonAct.logger = logger
UrlAct.logger = logger
NumAct.logger = logger
StrAct.logger = logger

sessAct.set_session()
sessAct.timeout = 10
header_version, user_agent, init_header = sessAct.set_header("chrome")
# header_version, user_agent, init_header = sessAct.set_header("firefox")

seAct.set_session()
seAct.timeout = 10


csrftoken = ""
# login_cookies = 'gfsitesid=ZmYwMWFiMTIxZHwxNjM1ODEzMjgwOTN8fDE1MTI1NTE4NDk0MDE2OTMHBwcHBwcH; csrftoken=CHHPig72RYv7WsaMUgXQyxOVhQkMpBK5; tt_webid=6987640213347960327; ttcid=c3601124b91c48c090c73c4fdb4785d530; MONITOR_WEB_ID=e7b7eaf0-ac35-4519-9176-9ed6e59b8bb0; tt_scid=N1Gi1Qe4-SxmKdUCmyMWfcWqgyhWosPCCxdqh6ZMkN0F8NlYUadRV42K1vqbm3FN0ad0; s_v_web_id=verify_38ef614d5b71f50e92c0699119ff83ef; _tea_utm_cache_2018=undefined; MONITOR_DEVICE_ID=ca2cc663-92bd-4abb-ad29-414e5d28f7db; passport_csrf_token_default=803f939d6a511a87348208f6afca37b7; sid_guard=ff01ab121d927ba8eabe9a1a20daa138%7C1635813279%7C5183999%7CSat%2C+01-Jan-2022+00%3A34%3A38+GMT; uid_tt=6ea0a81d62bfcee05c6a707f85469bda; uid_tt_ss=6ea0a81d62bfcee05c6a707f85469bda; sid_tt=ff01ab121d927ba8eabe9a1a20daa138; sessionid=ff01ab121d927ba8eabe9a1a20daa138; sessionid_ss=ff01ab121d927ba8eabe9a1a20daa138; sid_ucp_v1=1.0.0-KGZmZjNkZWIwMDM1OWM0NzhlMTdjZDhiY2ZiZjIzYmU2MjE3MTYxN2IKFwjdusDdhvXXAhCfj4KMBhj6EzgBQOsHGgJsZiIgZmYwMWFiMTIxZDkyN2JhOGVhYmU5YTFhMjBkYWExMzg; ssid_ucp_v1=1.0.0-KGZmZjNkZWIwMDM1OWM0NzhlMTdjZDhiY2ZiZjIzYmU2MjE3MTYxN2IKFwjdusDdhvXXAhCfj4KMBhj6EzgBQOsHGgJsZiIgZmYwMWFiMTIxZDkyN2JhOGVhYmU5YTFhMjBkYWExMzg; passport_csrf_token=803f939d6a511a87348208f6afca37b7; star_sessionid=c438ea3a976c8b8defbf5d7854043155; gftoken=ZmYwMWFiMTIxZHwxNjM1ODEzMjgwOTN8fDAGBgYGBgY'
# login_cookies = 'gfsitesid=Mzk0ODJlZjA2YnwxNjM1ODI2MTM4MzN8fDI3OTc2MDU4ODc0MTE3NzQHBwcHBwcH; MONITOR_DEVICE_ID=b41ac1f1-d772-46a9-8e56-bf7fe84c83a2; passport_csrf_token_default=06e4d69d12ba0cb1d9cc92387614622e; passport_csrf_token=06e4d69d12ba0cb1d9cc92387614622e; csrftoken=YuBHRfD78oVMBRrMvdt0OCmbUhomidcx; tt_webid=7017627710985897485; ttcid=60e6648a5db04577b285838bb28be7a484; _tea_utm_cache_2018=undefined; MONITOR_WEB_ID=477f7f7f-f12d-4a1f-9e04-0b0151e920b6; tt_scid=LQ3Y9vpXb8n0ToWj.UZ5e6G5ZzTTBry7NhIJwIa8LwDDDba5nTD-8sz5Ra5yHbVsaa2d; s_v_web_id=verify_56e4beddbdf8b2d5dcae72f433755a07; uid_tt=756803f84c1d7570fd621901fd3596e3; uid_tt_ss=756803f84c1d7570fd621901fd3596e3; sid_tt=39482ef06b89df0a2398639f778489d0; sessionid=39482ef06b89df0a2398639f778489d0; sessionid_ss=39482ef06b89df0a2398639f778489d0; sid_ucp_v1=1.0.0-KDI1ODczYjMyNDkyNWY1NzNiNGQ0Nzc5YmQ3ZjkzOTFlMTE5ZDE2MmIKFwi-jJCJho38BBDY84KMBhj6EzgBQOsHGgJsZiIgMzk0ODJlZjA2Yjg5ZGYwYTIzOTg2MzlmNzc4NDg5ZDA; ssid_ucp_v1=1.0.0-KDI1ODczYjMyNDkyNWY1NzNiNGQ0Nzc5YmQ3ZjkzOTFlMTE5ZDE2MmIKFwi-jJCJho38BBDY84KMBhj6EzgBQOsHGgJsZiIgMzk0ODJlZjA2Yjg5ZGYwYTIzOTg2MzlmNzc4NDg5ZDA; sid_guard=39482ef06b89df0a2398639f778489d0%7C1635826136%7C5184000%7CSat%2C+01-Jan-2022+04%3A08%3A56+GMT; star_sessionid=e529a6aee9cb4c6348b21898e1f07b24; gftoken=Mzk0ODJlZjA2YnwxNjM1ODI2MTM4MzN8fDAGBgYGBgY'
# login_cookies = 'gfsitesid=NDliZmRhMmMwN3wxNjM1ODMzNDk1MDB8fDMyMDIyMTE2ODE5NTg0NjIHBwcHBwcH; MONITOR_DEVICE_ID=b41ac1f1-d772-46a9-8e56-bf7fe84c83a2; passport_csrf_token_default=06e4d69d12ba0cb1d9cc92387614622e; passport_csrf_token=06e4d69d12ba0cb1d9cc92387614622e; csrftoken=YuBHRfD78oVMBRrMvdt0OCmbUhomidcx; tt_webid=7017627710985897485; ttcid=60e6648a5db04577b285838bb28be7a484; _tea_utm_cache_2018=undefined; MONITOR_WEB_ID=477f7f7f-f12d-4a1f-9e04-0b0151e920b6; tt_scid=113YBDz2pU2NM6zrC3zH-UtxNGMME3rTAm6.FehXtE8KhpvBA.f0hWU1QuaKBP5W8047; s_v_web_id=verify_618cca5cb38c07903ac47f3c1c7186d6; uid_tt=3de3b2b5d24c83b801b047f7fb30265b; uid_tt_ss=3de3b2b5d24c83b801b047f7fb30265b; sid_tt=49bfda2c07da11a4b0ee01dffc4e9698; sessionid=49bfda2c07da11a4b0ee01dffc4e9698; sessionid_ss=49bfda2c07da11a4b0ee01dffc4e9698; sid_ucp_v1=1.0.0-KDc5YmQ4YjJmM2JjYjZjZDJkNTgzYWMyMGZlN2YwNGU4Zjc1YjdmMzYKFwi-9LGO0IzYBRCWrYOMBhj6EzgBQOsHGgJsZiIgNDliZmRhMmMwN2RhMTFhNGIwZWUwMWRmZmM0ZTk2OTg; ssid_ucp_v1=1.0.0-KDc5YmQ4YjJmM2JjYjZjZDJkNTgzYWMyMGZlN2YwNGU4Zjc1YjdmMzYKFwi-9LGO0IzYBRCWrYOMBhj6EzgBQOsHGgJsZiIgNDliZmRhMmMwN2RhMTFhNGIwZWUwMWRmZmM0ZTk2OTg; sid_guard=49bfda2c07da11a4b0ee01dffc4e9698%7C1635833494%7C5183999%7CSat%2C+01-Jan-2022+06%3A11%3A33+GMT; star_sessionid=445abe56daced3671e38bf0364632c21; gftoken=NDliZmRhMmMwN3wxNjM1ODMzNDk1MDB8fDAGBgYGBgY'
login_cookies = 'gfsitesid=ODk4ZmE1M2UzM3wxNjM1ODQ0MzI4NTZ8fDExMDc5MzE5MzczODM0NjMHBwcHBwcH; MONITOR_DEVICE_ID=b41ac1f1-d772-46a9-8e56-bf7fe84c83a2; passport_csrf_token_default=06e4d69d12ba0cb1d9cc92387614622e; passport_csrf_token=06e4d69d12ba0cb1d9cc92387614622e; csrftoken=YuBHRfD78oVMBRrMvdt0OCmbUhomidcx; tt_webid=7017627710985897485; ttcid=60e6648a5db04577b285838bb28be7a484; _tea_utm_cache_2018=undefined; MONITOR_WEB_ID=477f7f7f-f12d-4a1f-9e04-0b0151e920b6; tt_scid=QVcFpfhtwtIL0H6EYl4hFuvw6wU-6zFmmsbD8MCaHiIew3qwZoBdHYaaQKeyxggP4161; s_v_web_id=verify_c2e04b9200aafa3e4da978179530e4f5; uid_tt=5d73de77536e6c95af24a74b6515c376; uid_tt_ss=5d73de77536e6c95af24a74b6515c376; sid_tt=898fa53e331bf7833edcf282a7b71e11; sessionid=898fa53e331bf7833edcf282a7b71e11; sessionid_ss=898fa53e331bf7833edcf282a7b71e11; sid_ucp_v1=1.0.0-KDVlM2I0ZDdiMDAxN2QyYWI2Y2ZjOTBlN2YyYzM3NzNmNzRiOGI3MTgKFwinyMCMiPX7ARDngYSMBhj6EzgBQOsHGgJsZiIgODk4ZmE1M2UzMzFiZjc4MzNlZGNmMjgyYTdiNzFlMTE; ssid_ucp_v1=1.0.0-KDVlM2I0ZDdiMDAxN2QyYWI2Y2ZjOTBlN2YyYzM3NzNmNzRiOGI3MTgKFwinyMCMiPX7ARDngYSMBhj6EzgBQOsHGgJsZiIgODk4ZmE1M2UzMzFiZjc4MzNlZGNmMjgyYTdiNzFlMTE; sid_guard=898fa53e331bf7833edcf282a7b71e11%7C1635844327%7C5184000%7CSat%2C+01-Jan-2022+09%3A12%3A07+GMT; star_sessionid=2c882f0d1c9911e9ae7eb01e13e8e69c; gftoken=ODk4ZmE1M2UzM3wxNjM1ODQ0MzI4NTZ8fDAGBgYGBgY'




def search(_id, userId):
    # 搜索账号列表
    author_id = ""
    sessAct.url = f"https://www.xingtu.cn/v/api/demand/author_list/?limit=20&need_detail=true&page=1&platform_source=1" \
                  f"&key={userId}&task_category=1&order_by=score&disable_replace_keyword=false&only_nick_name=false&marketing_target=1&is_filter=true"
    sessAct.headers = BaseAct.format_copy(init_header)
    sessAct.headers.update({
        "Host": "www.xingtu.cn",
        "Accept": "application/json, text/plain, */*",
        "x-login-source": "1",
        "X-CSRFToken": csrftoken,
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://www.xingtu.cn/ad/creator/market?platform_source=1",
        "Cookie": login_cookies
    })
    sessAct.get_response("get")
    if sessAct.get_page("json"):
        pass

    authors_gen = JsonAct.parse_json(sessAct.page, "$.data.authors")
    authors, authors_gen = BaseAct.parse_generator(authors_gen)
    if isinstance(authors, list):
        for i in authors:
            user_gen = JsonAct.parse_json(i, "$.core_user_id")
            user_id, user_gen = BaseAct.parse_generator(user_gen)
            if str(user_id) == userId:
                id_gen = JsonAct.parse_json(i, "$.id")
                author_id, id_gen = BaseAct.parse_generator(id_gen)
    if isinstance(authors, dict):
        user_gen = JsonAct.parse_json(authors, "$.core_user_id")
        user_id, user_gen = BaseAct.parse_generator(user_gen)
        if str(user_id) == userId:
            id_gen = JsonAct.parse_json(authors, "$.id")
            author_id, id_gen = BaseAct.parse_generator(id_gen)

    # 搜索的二次请求
    sessAct.url = f"https://www.xingtu.cn/v/api/demand/author_list_under_limit/?key={userId}&task_category=1"
    sessAct.get_response("get")
    if sessAct.get_page("json"):
        pass

    if not author_id:
        logger.info("==========================二次搜索获取数据==========================")
        authors_gen = JsonAct.parse_json(sessAct.page, "$.data.author")
        authors, authors_gen = BaseAct.parse_generator(authors_gen)
        if isinstance(authors, list):
            for i in authors:
                user_gen = JsonAct.parse_json(i, "$.core_user_id")
                user_id, user_gen = BaseAct.parse_generator(user_gen)
                if str(user_id) == userId:
                    id_gen = JsonAct.parse_json(i, "$.id")
                    author_id, id_gen = BaseAct.parse_generator(id_gen)
        if isinstance(authors, dict):
            user_gen = JsonAct.parse_json(authors, "$.core_user_id")
            user_id, user_gen = BaseAct.parse_generator(user_gen)
            if str(user_id) == userId:
                id_gen = JsonAct.parse_json(authors, "$.id")
                author_id, id_gen = BaseAct.parse_generator(id_gen)

    seAct.url = f"http://127.0.0.1:18081/api/return/check?id={_id}&author={author_id}"
    seAct.headers = {}
    seAct.get_response("get")
    if seAct.get_page("json"):
        pass
    
    # @@..! must sleep 30s above
    TimeAct.format_sleep(30)
    return True


def main_run():
    
    seAct.url = "http://127.0.0.1:18081/api/get/check/0/500/"
    seAct.headers = {}
    seAct.get_response("get")
    if not seAct.get_page("json"):
        return False
    account_list = seAct.page
    for i in account_list:
        if not search(i['_id'], i['userId']):
            continue


async def brush_value():
    seAct.url = "http://127.0.0.1:18081/api/get/scrape/0/500/"
    seAct.headers = {}
    seAct.get_response("get")
    if seAct.get_page("json"):
        pass
    ids = seAct.page
    number = 0

    if login_cookies:
        cookies = login_cookies.split("; ")
        cookies_list = []
        for i in cookies:
            gen = StrAct.parse_regex(i, "^[^=]*(?==)")
            name, gen = BaseAct.parse_generator(gen)
            gen = StrAct.parse_regex(i, "=(.*)")
            value, gen = BaseAct.parse_generator(gen)

            cookies_list.append({"name": name, "value": value, 
                                 "domain": "www.xingtu.cn", "path": "/"})

        # @@..! 不能最小化和无头
        if error := await auto.set_browser(False):
            logger.info(error)
            return False
        if error := await auto.set_clear():
            logger.info(error)
            return False
        if error := await auto.set_intercept(True):
            logger.info(error)
            return False
        if error := auto.set_capture('request', intercept_img):
            logger.info(error)
            return False
        if error := auto.set_capture('response', intercept_response):
            logger.info(error)
            return False
        if error := await auto.set_cookies(cookies_list):
            logger.info(error)
            return False
        if error := await auto.set_url("https://www.xingtu.cn/ad/creator/market?platform_source=1"):
            logger.info(error)
            return False
        await asyncio.sleep(10)

        for i in ids:
            number += 1
            logger.info(number)
            get_id = i['_id']
            author_id = i['authorId']
            if error := await auto.set_url(
                    f"https://www.xingtu.cn/ad/creator/author/douyin/"
                    f"{author_id}/1?recommend=false&version=v2"):
                
                logger.info(error)
                continue
            await asyncio.sleep(10)
            if error := await auto.set_click('#tab-\\"author_analysis\\"'):
                logger.info(error)
            else:
                await asyncio.sleep(5)
                if error := await auto.set_click('#tab-\\"fans\\"'):
                    logger.info(error)

            await asyncio.sleep(5)
            seAct.url = f"http://127.0.0.1:18081/api/return/scrape?id={get_id}"
            seAct.headers = {}
            seAct.get_response("get")
                

        if error := await auto.set_quit():
            logger.info(error)
            return False


async def intercept_img(request):
    if request.resourceType in ['image', 'media']:
        await request.abort()
    else:
        await request.continue_()


async def intercept_response(response):
    """响应过滤"""
    pool = PoolAct()
    pool.logger = logger
    pool.init_app()
    xingtu = pool.init_mongo("mongodb://127.0.0.1:27017/xingtu")
    
    author_id = ""
    
    resourceType = response.request.resourceType
    if resourceType in ['xhr', 'fetch']:
        if "service_method=GetAuthor" in response.url:
            url_head, url_domain, url_path, url_dict = UrlAct.parse_url(response.url)
            for k, v in url_dict.items():
                if "author_id" in k:
                    author_id = v[0]
            content = await response.text()
            content = JsonAct.format_json(content)
            content_gen = JsonAct.parse_json(content, "$.data")
            content_dict, content_gen = BaseAct.parse_generator(content_gen)

            if author_id and content_dict:
                try:
                    if "GetAuthorBaseInfo" in response.url:
                        pool.update_mongo(
                            xingtu, "base_info",
                            {"_id": author_id}, {"$set": content_dict}, True
                        )
                    elif "GetAuthorPlatformChannelInfoV2" in response.url:
                        pool.update_mongo(
                            xingtu, "base_info",
                            {"_id": author_id}, {"$set": content_dict}, True
                        )
                    elif "GetAuthorMarketingInfo" in response.url:
                        pool.update_mongo(
                            xingtu, "base_info",
                            {"_id": author_id}, {"$set": content_dict}, True
                        )
                    elif "GetAuthorStatInfo" in response.url:
                        order_complete_rate = content_dict.get("order_complete_rate")
                        if order_complete_rate:
                            order_complete_gen = StrAct.parse_decimal(order_complete_rate, 8)
                            order_complete_rate, order_complete_gen = BaseAct.parse_generator(order_complete_gen)
                            content_dict.update({"order_complete_rate": order_complete_rate})
                        pool.update_mongo(
                            xingtu, "stat_info",
                            {"_id": author_id}, {"$set": content_dict}, True
                        )
                    elif "GetAuthorSpreadInfo" in response.url:
                        pool.update_mongo(
                            xingtu, "stat_info",
                            {"_id": author_id}, {"$set": content_dict}, True
                        )
                    elif "GetAuthorFansDistributionV3" in response.url:
                        pool.update_mongo(
                            xingtu, "fans_dist",
                            {"_id": author_id}, {"$set": content_dict}, True
                        )
                    elif "GetAuthorHotCommentTokens" in response.url:
                        pool.update_mongo(
                            xingtu, "fans_dist",
                            {"_id": author_id}, {"$set": content_dict}, True
                        )             

                    # elif "GetAuthorDailyFansV2" in response.url:
                    #     pool.update_mongo(
                    #         xingtu, "daily_fans",
                    #         {"_id": author_id}, {"$set": content_dict}, True
                    #     )
                    # elif "GetAuthorLatestItems" in response.url:
                    #     pool.update_mongo(
                    #         xingtu, "latest_items",
                    #         {"_id": author_id}, {"$set": content_dict}, True
                    #     )
                    # elif "GetAuthorShowItems" in response.url and "only_ecom_live" not in response.url:
                    #     data_description = content_dict.get("data_description")
                    #     if data_description:
                    #         for kk, vv in data_description.items():
                    #             compare_avg = vv.get('compare_avg')
                    #             if compare_avg:
                    #                 compare_gen = StrAct.parse_decimal(compare_avg, 8)
                    #                 compare_avg, compare_gen = BaseAct.parse_generator(compare_gen)
                    #                 vv['compare_avg'] = compare_avg
                    #         content_dict.update({"data_description": data_description})
                    #     pool.update_mongo(
                    #         xingtu, "show_items",
                    #         {"_id": author_id}, {"$set": content_dict}, True
                    #     )
                    # elif "GetAuthorShowItems" in response.url and "only_ecom_live" in response.url:
                    #     data_description = content_dict.get("data_description")
                    #     if data_description:
                    #         for kk, vv in data_description.items():
                    #             compare_avg = vv.get('compare_avg')
                    #             if compare_avg:
                    #                 compare_gen = StrAct.parse_decimal(compare_avg, 8)
                    #                 compare_avg, compare_gen = BaseAct.parse_generator(compare_gen)
                    #                 vv['compare_avg'] = compare_avg
                    #         content_dict.update({"data_description": data_description})
                    #     pool.update_mongo(
                    #         xingtu, "live_items",
                    #         {"_id": author_id}, {"$set": content_dict}, True
                    #     )
                    # elif "GetAuthorWatchedDistribution" in response.url:
                    #     pool.update_mongo(
                    #         xingtu, "watched_dist",
                    #         {"_id": author_id}, {"$set": content_dict}, True
                    #     )
                    # elif "GetAuthorSellScore" in response.url:
                    #     pool.update_mongo(
                    #         xingtu, "sell_score",
                    #         {"_id": author_id}, {"$set": content_dict}, True
                    #     )                 
                except Exception as ex:
                    logger.info(ex)
                    logger.info(author_id)


def get_account():
    
    # sync update profileBase
    # mongoexport -d source -c update -f profileBase -q '{platId:1,isUse:1}' -o update.json
    pool = PoolAct()
    pool.logger = logger
    pool.init_app()
    xingtu = pool.init_mongo("mongodb://127.0.0.1:27017/xingtu")    

    try:
        result_gen = pool.query_mongo(
            xingtu, "update",
            {},
            {"userId": "$profileBase.userId", "matchUid": "$profileBase.matchUid"},
            []
        )
        # update userId and matchUid
        for i in result_gen:
            userId = i.get("userId")
            if userId:
                pool.update_mongo(
                    xingtu, "account", {"_id": i['_id']},
                    {"$set": {"userId": i["userId"], "matchUid": i["matchUid"]}},
                    True
                )
        # update isCheck
        pool.update_mongo(
            xingtu, "account", {"isCheck": {"$exists": False}},
            {"$set": {"isCheck": 0, "isScrape": 0}},
            False, True
        )
    except Exception as ex:
        logger.info(ex)
    finally:
        pool.close_mongo(xingtu)


def make_xingtu():
    try:
        pool = PoolAct()
        pool.logger = logger
        pool.init_app()
        xingtu = pool.init_mongo("mongodb://127.0.0.1:27017/xingtu")
        source = pool.init_mongo("mongodb://127.0.0.1:27017/source")

        result_gen = pool.query_mongo(
            xingtu, "account", {"isScrape": 1}, {}, [])
        for i in result_gen:
            taskId = i.get("_id")
            authorId = i.get("authorId")
            matchUid = i.get("matchUid", "")
            
            gender = 0
            area = ""
            video20 = 0
            video60 = 0
            fansCity = ""
            fansProperties = ""
            field = ""
            humanRatio = ""
            reportAge = []
            reportCity = []
            reportFans = []
            reportActive = []
            reportDevice = []
            areaTop = ""
            ageRange = ""

            info_gen = pool.query_mongo(xingtu, "base_info", {"_id": authorId}, {}, [])
            for j in info_gen:
                tags = j.get("tags", "")
                tags = JsonAct.format_json(tags)
                field = ",".join(tags)
                gender = j.get("gender", 0)
                city = j.get("city", "")
                province = j.get("province", "")
                if province:
                    area += province
                    if city:
                        area += ("," + city)
                else:
                    if city:
                        area += city
                
                price_info = j.get("price_info")
                if price_info:
                    for k in price_info:
                        desc = k.get("desc")
                        price = k.get("price")
                        if desc and price:
                            if "1-20" in desc:
                                video20 = price
                            elif "21-60" in desc:
                                video60 = price

            info_gen = pool.query_mongo(xingtu, "fans_dist", {"_id": authorId}, {}, [])
            for j in info_gen:
                distributions = j.get("distributions")
                images = []
                if distributions:
                    for k in distributions:
                        dis_type = k.get("type_display", "")
                        dis_value = k.get("distribution_list", [])
                        
                        if "年龄分布" in dis_type and dis_value:
                            age_sum = 0
                            for m in dis_value:
                                age_sum += m.get("distribution_value")
                            if age_sum:
                                for m in dis_value:
                                    name = m.get("distribution_key")
                                    value = m.get("distribution_value") / age_sum
                                    value = StrAct.parse_decimal(value, 4)
                                    value, gen = BaseAct.parse_generator(value)
                                    if "+" in name:
                                        reportAge.append({"name": ">50", "value": value})
                                    elif "-18" in name:
                                        reportAge.append({"name": "0-18", "value": value})
                                    elif "50-" in name:
                                        reportAge.append({"name": ">50", "value": value})
                                    else:
                                        reportAge.append({"name": name, "value": value})
                            
                                reportAge.sort(key=lambda n: n.get("name"))
                            
                                age_list = BaseAct.format_copy(reportAge)
                                age_list.sort(key=lambda n: n.get("value"), reverse=True)
                                a_name = age_list[0]['name']
                                a_value = age_list[0]['value'] * 100
                                a_value = StrAct.parse_decimal(a_value, 2)
                                a_value, gen = BaseAct.parse_generator(a_value)
                                ageRange = f"{a_name},{a_value}"
                            
                            dis_image = k.get("image", [])
                            images += dis_image
                            
                        elif "省份分布" in dis_type and dis_value:
                            city_sum = 0
                            for m in dis_value:
                                city_sum += m.get("distribution_value")
                            if city_sum:
                                for m in dis_value:
                                    name = m.get("distribution_key")
                                    value = m.get("distribution_value") / city_sum
                                    value = StrAct.parse_decimal(value, 4)
                                    value, gen = BaseAct.parse_generator(value)
                                    reportCity.append({"name": name, "value": value})
                
                                reportCity = reportCity[:10]
                                reportCity.sort(key=lambda n: n.get("value"), reverse=True)

                                top3_city = reportCity[:3]
                                top3_list = []
                                area3_list = []
                                for m in top3_city:
                                    name = m.get("name")
                                    value = m.get("value") * 100
                                    value = StrAct.parse_decimal(value, 2)
                                    value, gen = BaseAct.parse_generator(value)
                                    top3_list.append(name)
                                    area3_list.append(f'{name}{value}')
                                fansCity = ",".join(top3_list)
                                areaTop = ",".join(area3_list)
                        
                        elif "性别分布" in dis_type and dis_value:
                            sex_sum = 0
                            for m in dis_value:
                                sex_sum += m.get("distribution_value")
                            if sex_sum:
                                for m in dis_value:
                                    name = m.get("distribution_key")
                                    value = m.get("distribution_value") / sex_sum
                                    value = StrAct.parse_decimal(value, 4)
                                    value, gen = BaseAct.parse_generator(value)
                                    if "未知" in name:
                                        continue
                                    elif "female" in name:
                                        reportFans.append({"name": "女", "value": value})            
                                    else:
                                        reportFans.append({"name": "男", "value": value})
                            
                                reportFans.sort(key=lambda n: n.get("name"), reverse=True)
                                h_value = reportFans[0]['value'] * 100
                                h_value = StrAct.parse_integer(h_value)
                                h_value, gen = BaseAct.parse_generator(h_value)
                                humanRatio = f"{h_value}:"
                                h_value = reportFans[1]['value'] * 100
                                h_value = StrAct.parse_integer(h_value)
                                h_value, gen = BaseAct.parse_generator(h_value)
                                humanRatio += str(h_value)
                                
                            dis_image = k.get("image", [])
                            images += dis_image
                
                        elif "设备品牌分布" in dis_type and dis_value:
                            device_sum = 0
                            for m in dis_value:
                                device_sum += m.get("distribution_value")
                            if device_sum:
                                for m in dis_value:
                                    name = m.get("distribution_key")
                                    value = m.get("distribution_value") / device_sum
                                    value = StrAct.parse_decimal(value, 4)
                                    value, gen = BaseAct.parse_generator(value)
                                    
                                    reportDevice.append({"name": name, "value": value})

                            dis_image = k.get("image", [])
                            images += dis_image
                
                        elif "活跃度分布" in dis_type and dis_value:
                            active_sum = 0
                            for m in dis_value:
                                active_sum += m.get("distribution_value")
                            if active_sum:
                                for m in dis_value:
                                    name = m.get("distribution_key")
                                    value = m.get("distribution_value") / active_sum
                                    value = StrAct.parse_decimal(value, 4)
                                    value, gen = BaseAct.parse_generator(value)
                                    
                                    reportActive.append({"name": name, "value": value})
                            
                            # dis_image = k.get("image", [])
                            # images += dis_image
                
                images = images[:3]
                fansProperties = ",".join(images)
                
            result_dict = {
                "gender": gender, "area": area, "video20": video20, "video60": video60, "fansCity": fansCity,
                "fansPreference": "", "fansProperties": fansProperties, "field": field,
                "humanRatio": humanRatio, "matchUid": matchUid, "platId": 1, "fansActiveTime": "",
                "reportAge": reportAge, "reportCity": reportCity, "reportFans": reportFans,
                "reportActive": reportActive, "reportDevice": reportDevice,
                "areaTop": areaTop, "ageRange": ageRange}
                
            pool.update_mongo(
                xingtu, "update_match", {"_id": taskId}, {"$set": result_dict}, True
            )

        logger.info("运行完毕，over")
    except Exception as ex:
        logger.info(f"{ex}")
    finally:
        pool.close_mongo(xingtu)
        pool.close_mongo(source)
        return False


def test():
    try:
        pool = PoolAct()
        pool.logger = logger
        pool.init_app()
        
        source_db = pool.init_mongo("mongodb://127.0.0.1:27017/source")
        # source_db = pool.init_mongo("mongodb://mongodb:27017/source")
        api_start = 0
        while 1:
            result_gen = pool.query_mongo(
                source_db, "account",
                {"envMap.api": {"$elemMatch": {"id": {"$gt": api_start, "$lte": api_start + 50}}}},
                {"envMap.api": 1, "_id": 0},
                []
            )
            # update userId and matchUid
            aa = list(result_gen)
            if len(aa) == 0:
                break
            for i in aa:
                ids = i.get("envMap").get("api")
                for j in ids:
                    iddd = j.get("id")
                    if api_start < iddd <= api_start + 50:
                        print(iddd)

            api_start += 50

        logger.info("[测试test]运行完毕，over")
    except Exception as ex:
        logger.info(f"[测试test]运行存在错误{ex}")
    finally:
        pool.close_mongo(source_db)
        return False



if __name__ == "__main__":
    
    # test()
    
    # main_run()
    asyncio.get_event_loop().run_until_complete(brush_value())


    # get_account()
    # make_xingtu()
