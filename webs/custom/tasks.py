#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> tasks
@@..> package webs.custom
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# # @@..> import current path
import sys
sys.path.append('../..')
# @@..> base import
from celery import shared_task
from concurrent.futures import ThreadPoolExecutor
# @@..> import utils
from utils.base_tools import BaseAct, LogAct
from utils.net_tools import NetAct
from utils.json_tools import JsonAct
from utils.pool_tools import PoolAct
from utils.str_tools import StrAct, UrlAct, EncryptAct
from utils.num_tools import NumAct, TimeAct
import math


logger, handler = LogAct.init_log("tasks.log", False)
# logger, handler = LogAct.init_log("tasks.log")
TimeAct.logger = logger
NumAct.logger = logger
JsonAct.logger = logger
StrAct.logger = logger
UrlAct.logger = logger
EncryptAct.logger = logger


@shared_task
def sync_thread(sync_type):
    if not isinstance(sync_type, int):
        sync_type = 1
    # define app
    thread_pool = PoolAct()
    thread_pool.logger = logger
    thread_pool.init_app()
    # thread_pool.init_mysql(
    #     "mysql://root:root@127.0.0.1:3306/manager?charset=utf8mb4")
    thread_pool.init_mysql(
        "mysql://root:root@mariadb:3306/manager?charset=utf8mb4")
    # [sync_type, 1审核/2作品/3快速/4账号]
    sql = f"select * from mcn_sync where sync_active = 1 and sync_type = {sync_type}"
    result_gen = thread_pool.query_mysql(sql)
    all_args = []
    for i in result_gen:
        all_args.append([i.sync_identity, i.sync_url, i.sync_limit, sync_type])
    if all_args:
        with ThreadPoolExecutor(max_workers=len(all_args)) as t:
            all_task = [t.submit(sync_account, args) for args in all_args]
    # close
    thread_pool.close_mysql()


def sync_account(args: list) -> bool:
    try:
        # define app and net
        pool = PoolAct()
        pool.logger = logger
        pool.init_app()
        # source_db = pool.init_mongo("mongodb://127.0.0.1:27017/source")
        source_db = pool.init_mongo("mongodb://mongodb:27017/source")
        net = NetAct()
        net.logger = logger
        net.set_session()
        net.timeout = 10
        net.headers = {'Connection': 'close'}
        start_time = TimeAct.format_timestamp()
        # take args
        sync_identity = args[0]
        sync_url = args[1]
        sync_limit = args[2]
        sync_type = args[3]
        # make choice
        if sync_type == 1:
            source_name = "certify"
        elif sync_type == 2:
            source_name = "work"
        elif sync_type == 3:
            source_name = "quick"
        elif sync_type == 4:
            source_name = "account"
        else:
            logger.info(f"[同步{sync_identity}/类型{sync_type}]类型不受支持")
            net.set_close()
            return False
        # start id
        api_start = 0
        # if account type check sum and reset api_start
        if sync_type == 4:
            count_gen = pool.aggregate_mongo(
                source_db, source_name,
                [{"$unwind": "$envMap"},
                 {"$group": {"_id": "$envMap.name", "count": {"$sum": 1}}}]
            )
            for i in count_gen:
                if i.get("_id") == sync_identity:
                    api_start = i.get("count", 0)
            api_start = int(api_start * 0.75)
            logger.info(f"[同步{sync_identity}/类型{sync_type}]起始ID{api_start}")
        else:
            # check first number
            net.url = f"{sync_url}?startId=0&limit=1"
            if not net.get_response("get"):
                pass
            if not net.get_page("json", is_log=False):
                pass
            data_gen = JsonAct.parse_json(net.page, "$.data.list[0].id")
            data_value, data_gen = BaseAct.parse_generator(data_gen)
            if data_value:
                data_gen = StrAct.parse_integer(data_value)
                api_start, data_gen = BaseAct.parse_generator(data_gen)
                if api_start:
                    # take first number
                    api_start -= 1
        # scrape loop
        net_status = True
        while 1:
            net.url = f"{sync_url}?startId={api_start}&limit={sync_limit}"
            if not net.get_response("get"):
                net_status = False
                break
            if not net.get_page("json", is_log=False):
                net_status = False
                break
            data_gen = JsonAct.parse_json(net.page, "$.data.list.*")
            data_value, data_gen = BaseAct.parse_generator(data_gen)
            # if value is null then stop
            if not data_value:
                break
            # add limit and parse data
            api_start += sync_limit
            for i in data_gen:
                id_gen = StrAct.parse_integer(i.get("id"))
                env_id, id_gen = BaseAct.parse_generator(id_gen)
                plat_gen = StrAct.parse_integer(i.get("plantId"))
                plat_id, plat_gen = BaseAct.parse_generator(plat_gen)
                account_url = i.get('url', "")
                nickname = i.get('nickname', "")
                account_id = i.get('accountId', "")
                # if quick type then reset account_id
                if sync_type == 3:
                    account_id = i.get('plantUid', "")
                # if weixin then reset account_url
                if plat_id == 6:
                    account_url = f"https://weixin.sogou.com/weixin?type=1" \
                                  f"&s_from=input&query={account_id}&ie=utf8" \
                                  f"&_sug_=n&_sug_type_="
                # if not account_url the set default
                url_head, url_domain, url_path, url_dict = UrlAct.parse_url(account_url)
                if not url_domain:
                    account_url = "xxxxx"
                unique_id = EncryptAct.format_md5(account_url)
                # if account type set the unique_id
                if sync_type == 4:
                    pool.update_mongo(
                        source_db, source_name, {'_id': unique_id},
                        {"$set":
                            {"platId": plat_id, "aid": account_id,
                             "originUrl": account_url, "originDomain": url_domain,
                             "scrapeUrl": account_url, "nickname": nickname,
                             "updateTime": start_time},
                         "$addToSet":
                            {"envMap": {"name": sync_identity, "id": env_id}}},
                        True
                    )
                else:
                    pool.update_mongo(
                        source_db, source_name, {'_id': f"{sync_identity}{env_id}"},
                        {'$set':
                            {"syncName": sync_identity, "envId": env_id,
                             "platId": plat_id, "aid": account_id,
                             "originUrl": account_url, "originDomain": url_domain,
                             "scrapeUrl": account_url, "nickname": nickname,
                             "updateTime": start_time}},
                        True
                    )
            # sleep
            TimeAct.format_sleep(3)

        # check net_status
        if not net_status:
            logger.info(f"[同步{sync_identity}/类型{sync_type}]接口服务错误")
            net.set_close()
            return False

    except Exception as ex:
        logger.info(f"[同步{sync_identity}/类型{sync_type}]运行存在错误{ex}")
    finally:
        pool.close_mongo(source_db)
        net.set_close()
        return True


@shared_task
def queue_thread(flow_type: int = 1, queue_type: int = 1,
                 sync_identity: str = "tapi"):
    # [flow_type=1] [profile页queue_type, 1审核/2快速/3账号/4更新(profile+work)]
    # [flow_type=2] [work页queue_type, 1审核/2快速]
    if not isinstance(flow_type, int):
        flow_type = 1
    if not isinstance(queue_type, int):
        queue_type = 1
    if not isinstance(sync_identity, str):
        sync_identity = "tapi"
    # define app
    thread_pool = PoolAct()
    thread_pool.logger = logger
    thread_pool.init_app()
    # thread_pool.init_mysql(
    #     "mysql://root:root@127.0.0.1:3306/manager?charset=utf8mb4")
    thread_pool.init_mysql(
        "mysql://root:root@mariadb:3306/manager?charset=utf8mb4")
    # sql check
    sql = "select * from mcn_plat"
    result_gen = thread_pool.query_mysql(sql)
    all_args = []
    for i in result_gen:
        all_args.append([i.id, i.plat_name, flow_type, queue_type, sync_identity])
    if all_args:
        with ThreadPoolExecutor(max_workers=len(all_args)) as t:
            all_task = [t.submit(task_queue, url) for url in all_args] 
    # close
    thread_pool.close_mysql()


def task_queue(args):
    try:
        # define app
        pool = PoolAct()
        pool.logger = logger
        pool.init_app()
        # pool.init_redis("redis://127.0.0.1:6379/1")
        # source_db = pool.init_mongo("mongodb://127.0.0.1:27017/source")
        pool.init_redis("redis://redis:6379/1")
        source_db = pool.init_mongo("mongodb://mongodb:27017/source")
        # take args
        plat_id = args[0]
        plat_name = args[1]
        flow_type = args[2]
        queue_type = args[3]
        sync_identity = args[4]
        # check flow type
        if flow_type != 1 and flow_type != 2:
            logger.info(f"[队列{plat_name}/环境{sync_identity}/flow{flow_type}]类型不受支持")
            return False
        # make choice
        if queue_type == 1:
            col_name = "certify"
            redis_name = "certify"
            if flow_type == 2:
                col_name = "work"
                redis_name = "work"
        elif queue_type == 2:
            col_name = "quick"
            redis_name = "quick"
        elif queue_type == 3:
            # only profile
            col_name = "account"
            redis_name = "account"
        elif queue_type == 4:
            # profile + work
            col_name = "update"
            redis_name = "update"
        else:
            logger.info(f"[队列{plat_name}/环境{sync_identity}/tool{queue_type}]类型不受支持")
            return False
        # if redis queue is None then add
        redis_count = pool.query_redis(f'{redis_name}_{plat_id}')
        if not redis_count:
            # profile data
            if flow_type == 1:
                # @@..! if cerity/quick type, check isScrape
                if queue_type == 1 or queue_type == 2:
                    result_gen = pool.query_mongo(
                        source_db, col_name,
                        {"isScrape": {"$exists": False}, "syncName": sync_identity,
                         "platId": plat_id},
                        {"scrapeUrl": 1}, []
                    )
                    for i in result_gen:
                        i.update({"toolType": queue_type, "flowType": flow_type})
                        insert_data = JsonAct.format_string(i)
                        pool.push_redis(f'{redis_name}_{plat_id}', insert_data)
                # @@..! if account type, check isScrape
                elif queue_type == 3:
                    result_gen = pool.query_mongo(
                        source_db, col_name,
                        {"isScrape": {"$exists": False}, "platId": plat_id,
                         "envMap": {"$elemMatch": {"name": sync_identity}}},
                        {"envMap": 1, "scrapeUrl": 1}, []
                    )
                    # add queue
                    for i in result_gen:
                        i.update({"toolType": queue_type, "flowType": flow_type})
                        insert_data = JsonAct.format_string(i)
                        pool.push_redis(f'{redis_name}_{plat_id}', insert_data)
                # @@..! if update type and sort envMap id, must profile + work
                elif queue_type == 4:
                    # @@..! check isUse and updateDate
                    time_now = TimeAct.format_now()
                    today_string = str(time_now.date())
                    result_gen = pool.query_mongo(
                        source_db, col_name,
                        {"isUse": 1, "platId": plat_id,
                         "envMap": {"$elemMatch": {"name": sync_identity}},
                         "updateDate": {"$ne": today_string}},
                        {"envMap": 1, "scrapeUrl": 1,
                         "isUrls": 1, "workUrls": 1},
                        [("envMap.id", -1)]
                    )
                    for i in result_gen:
                        taskId = i.get("_id")
                        isUrls = i.get("isUrls")
                        envMap = i.get("envMap")
                        scrapeUrl = i.get("scrapeUrl")
                        workUrls = i.get("workUrls", [])
                        workLast, workGen = BaseAct.parse_generator(workUrls, True)
                        # add profile queue and set isLast is 0
                        insert_data = {
                            "_id": taskId, "envMap": envMap, "toolType": queue_type,
                            "flowType": flow_type, "scrapeUrl": scrapeUrl}
                        insert_data = JsonAct.format_string(insert_data)
                        pool.push_redis(f'{redis_name}_{plat_id}', insert_data)
                        # @@..! check isUrls
                        if isUrls:
                            for j in workGen:
                                scrapeUrl = j
                                isLast = 0
                                if j == workLast:
                                    isLast = 1
                                # @@..! set flow type is 2
                                insert_data = {
                                    "_id": taskId, "toolType": queue_type,
                                    "flowType": 2, "scrapeUrl": scrapeUrl,
                                    "isLast": isLast}
                                insert_data = JsonAct.format_string(insert_data)
                                pool.push_redis(f'{redis_name}_{plat_id}', insert_data)
            # work data
            elif flow_type == 2:
                # @@..! if work type, check isScrape
                if queue_type == 1:
                    result_gen = pool.query_mongo(
                        source_db, col_name,
                        {"isScrape": {"$exists": False}, "syncName": sync_identity,
                         "platId": plat_id},
                        {"scrapeUrl": 1}, []
                    )
                    for i in result_gen:
                        i.update({"toolType": queue_type, "flowType": flow_type})
                        insert_data = JsonAct.format_string(i)
                        pool.push_redis(f'{redis_name}_{plat_id}', insert_data)
                # @@..! if quick type, check isScrape/isUrls/isUse
                # @@..! must isScrape set 1 and isUrls set 1
                elif queue_type == 2:
                    result_gen = pool.query_mongo(
                        source_db, col_name,
                        {"isScrape": 1, "isUrls": 1, "isUse": 1,
                         "syncName": sync_identity, "platId": plat_id},
                        {"workUrls": 1}, []
                    )
                    # parse data
                    for i in result_gen:
                        taskId = i.get("_id")
                        workUrls = i.get("workUrls", [])
                        workLast, workGen = BaseAct.parse_generator(workUrls, True)
                        for j in workGen:
                            scrapeUrl = j
                            isLast = 0
                            if j == workLast:
                                isLast = 1
                            insert_data = {
                                "_id": taskId, "toolType": queue_type,
                                "flowType": flow_type, "scrapeUrl": scrapeUrl,
                                "isLast": isLast}
                            insert_data = JsonAct.format_string(insert_data)
                            pool.push_redis(f'{redis_name}_{plat_id}', insert_data)
                        # @@..! must set isUrls to 0
                        pool.update_mongo(
                            source_db, col_name, {'_id': taskId},
                            {'$set': {"isUrls": 0}}
                        )
                else:
                    logger.info(f"[队列{plat_name}/环境{sync_identity}/"
                                f"tool{queue_type}的flow{flow_type}]类型不受支持")
                    return False

    except Exception as ex:
        logger.info(f"[队列{plat_name}/环境{sync_identity}/"
                    f"tool{queue_type}的flow{flow_type}]运行存在错误{ex}")
    finally:
        pool.close_redis()
        pool.close_mongo(source_db)
        return False


@shared_task
def send_thread(plat_id: int = 1):
    if not isinstance(plat_id, int):
        plat_id = 1
    # define app
    thread_pool = PoolAct()
    thread_pool.logger = logger
    thread_pool.init_app()
    # thread_pool.init_mysql(
    #     "mysql://root:root@127.0.0.1:3306/manager?charset=utf8mb4")
    thread_pool.init_mysql(
        "mysql://root:root@mariadb:3306/manager?charset=utf8mb4")
    # check sql
    sql = f"select mm.machine_name,mm.machine_host,ma.mcn_plat_id,mp.plat_identity," \
          f"ma.account_identity,ma.username,ma.password,ma.cookies from mcn_run " \
          f"as mr left join mcn_machine as mm on mm.id=mr.mcn_machine_id left join " \
          f"mcn_account as ma on ma.id=mr.mcn_account_id left join mcn_plat as mp " \
          f"on mp.id=ma.mcn_plat_id where mr.active=1 and ma.mcn_plat_id={plat_id}"
    result_gen = thread_pool.query_mysql(sql)
    all_args = []
    for i in result_gen:
        all_args.append([
            i.machine_name, i.machine_host, i.mcn_plat_id,
            i.plat_identity, i.account_identity,
            i.username, i.password, i.cookies])
    if all_args:
        with ThreadPoolExecutor(max_workers=len(all_args)) as t:
            all_task = [t.submit(send_tasks, (url)) for url in all_args]
    # close
    thread_pool.close_mysql()


def send_tasks(args):
    try:
        # define app
        pool = PoolAct()
        pool.logger = logger
        pool.init_app()
        # pool.init_redis("redis://127.0.0.1:6379/1")
        pool.init_redis("redis://redis:6379/1")
        net = NetAct()
        net.logger = logger
        net.set_session()
        net.timeout = 10
        net.headers = {'Connection': 'close'}
        # take args
        machine_name = args[0]
        machine_host = args[1]
        plat_id = args[2]
        plat_identity = args[3]
        account_identity = args[4]
        username = args[5]
        password = args[6]
        cookies = args[7]
        # queue sort
        queue_list = [f'certify_{plat_id}', f'quick_{plat_id}', f'work_{plat_id}',
                      f'account_{plat_id}', f'update_{plat_id}']
        result_data = pool.pop_redis(queue_list, 5)
        if result_data:
            result_dict = JsonAct.format_json(result_data)
            cookies = JsonAct.format_json(cookies)
            result_dict.update(
                {"platIdentity": plat_identity, "accountIdentity": account_identity,
                 "username": username, "password": password, "cookies": cookies})

            gzip_data = JsonAct.format_string(result_dict)
            net.posts = StrAct.format_gzip(gzip_data)
            net_status = True
            net.url = f"http://{machine_host}/api/worker/"
            if not net.get_response("post", "data"):
                net_status = False
            if not net.get_page("json", is_log=False):
                net_status = False
            if not net_status:
                logger.info(f"[机器{machine_name}/平台{plat_identity}]发送数据失败")
    except Exception as ex:
        logger.info(f"[机器{machine_name}/平台{plat_identity}]运行存在错误{ex}")
    finally:
        pool.close_redis()
        net.set_close()
        return False   


@shared_task
def quick_thread():
    # plat ids
    all_args = []
    for i in [1, 2, 3, 4, 5, 6, 7, 8]:
        all_args.append([i])
    if all_args:
        with ThreadPoolExecutor(max_workers=len(all_args)) as t:
            all_task = [t.submit(make_quick, (url)) for url in all_args]


def make_quick(args):
    try:
        # define app
        pool = PoolAct()
        pool.logger = logger
        pool.init_app()
        # source_db = pool.init_mongo("mongodb://127.0.0.1:27017/source")
        source_db = pool.init_mongo("mongodb://mongodb:27017/source")
        # take args
        plat_id = args[0]
        # query quick
        result_gen = pool.query_mongo(
            source_db, "quick",
            {"status": {"$exists": False}, "platId": plat_id}, 
            {"platId": 1, "matchUid": "$profileBase.matchUid",
             "workList": 1, "isUse": 1, "isLast": 1}, []
        )
        for i in result_gen:
            taskId = i.get("_id")
            matchUid = i.get("matchUid")
            isUse = i.get("isUse")
            isLast = i.get("isLast")
            if taskId and matchUid:
                if isUse == 0:
                    pool.update_mongo(
                        source_db, 'quick', {'_id': taskId},
                        {"$set": {"status": 1}}
                    )
                elif isUse == 1:
                    if isLast == 1:
                        humanRatio = ""
                        ageRange = ""
                        areaTop = ""
                        match_gen = pool.query_mongo(
                            source_db, "update_match",
                            {"platId": plat_id, "matchUid": matchUid},
                            {"_id": 0, "humanRatio": 1,
                             "ageRange": 1, "areaTop": 1}, []
                        )
                        for j in match_gen:
                            humanRatio = j.get("humanRatio", "")
                            ageRange = j.get("ageRange", "")
                            areaTop = j.get("areaTop", "")
                        # make work list and avg
                        workList = i.get("workList")
                        num_list = ["likeNum", "commentNum", "shareNum", "forwardNum",
                                    "collectNum", "playNum", "viewNum", "rewardNum", "danmakuNum"]
                        num_dict = {w: [] for w in num_list}
                        list_dict = {}
                        avg_dict = {}
                        if workList:
                            for j in workList:
                                for k, v in j.items():
                                    if k in num_list:
                                        num_dict[k].append(v)
                        for k, v in num_dict.items():
                            if v:
                                name = k.replace("Num", "")
                                list_dict[f"{name}List"] = v
                        if list_dict:
                            for k, v in list_dict.items():
                                name = k.replace("List", "Avg")
                                avg = NumAct.parse_average(v)
                                avg_dict[name] = avg

                        add_dict = {"humanRatio": humanRatio, "ageRange": ageRange,
                                    "areaTop": areaTop, "status": 1}
                        avg_dict = avg_dict | add_dict

                        pool.update_mongo(
                            source_db, 'quick', {'_id': taskId},
                            {"$set": avg_dict} 
                        )
    except Exception as ex:
        logger.info(f"[快速{plat_id}]运行存在错误{ex}")
    finally:
        pool.close_mongo(source_db)
        return False


@shared_task
def count_thread():

    all_args = []
    for i in [1, 2, 3, 4, 5, 7, 8]:
        all_args.append([i])
    if all_args:
        with ThreadPoolExecutor(max_workers=len(all_args)) as t:
            all_task = [t.submit(make_count, (url)) for url in all_args]


def make_count(args):
    try:
        # define app
        pool = PoolAct()
        pool.logger = logger
        pool.init_app()
        # pool.init_mysql(
        #     "mysql://root:root@127.0.0.1:3306/manager?charset=utf8mb4")
        # source_db = pool.init_mongo("mongodb://127.0.0.1:27017/source")
        pool.init_mysql(
            "mysql://root:root@mariadb:3306/manager?charset=utf8mb4")
        source_db = pool.init_mongo("mongodb://mongodb:27017/source")
        # take args
        plat_id = args[0]
        start_time = TimeAct.format_timestamp()
        time_now = TimeAct.format_now()
        # query isUse
        result_gen = pool.query_mongo(
            source_db, "update",
            {"isUse": 1, "platId": plat_id}, 
            {"platId": 1, "matchUid": "$profileBase.matchUid",
             "profileCounts": 1, "workList": 1, "updateDate": 1},
            []
        )
        for i in result_gen:
            taskId = i.get("_id")
            platId = i.get("platId")
            matchUid = i.get("matchUid")
            updateDate = i.get("updateDate")
            profileCounts = i.get("profileCounts")
            if taskId and platId and matchUid and updateDate and profileCounts:
                # make work list and avg
                workList = i.get("workList")
                num_list = ["likeNum", "commentNum", "shareNum", "forwardNum",
                            "collectNum", "playNum", "viewNum", "rewardNum", "danmakuNum"]
                num_dict = {w: [] for w in num_list}
                list_dict = {}
                avg_dict = {}
                if workList:
                    for j in workList:
                        for k, v in j.items():
                            if k in num_list:
                                num_dict[k].append(v)
                for k, v in num_dict.items():
                    if v:
                        name = k.replace("Num", "")
                        list_dict[f"{name}List"] = v
                if list_dict:
                    for k, v in list_dict.items():
                        name = k.replace("List", "Avg")
                        avg = NumAct.parse_average(v)
                        avg_dict[name] = avg
                # query showSum and showCounts
                showSum = 0
                showCounts = {}
                result_gen = pool.query_mongo(
                    source_db, "update_count",
                    {'_id': taskId}, {"showSum": 1, "showCounts": 1}, []
                )
                for j in result_gen:
                    showSum = j.get("showSum", 0)
                    showCounts = j.get("showCounts", {})
                
                list_dict = list_dict | avg_dict
                avg_dict = avg_dict | profileCounts
                # if < 10 is add
                if showSum < 10:
                    addNum = True
                    if showCounts:
                        for k in showCounts.keys():
                            if k == updateDate:
                                addNum = False
                    if addNum:
                        # if add showSum + 1
                        pool.update_mongo(
                            source_db, 'update_count', {'_id': taskId},
                            {'$inc': {"showSum": 1},
                             "$set": {"platId": platId, "matchUid": matchUid,
                                      f"showCounts.{updateDate}": avg_dict,
                                      f"saveCounts.{updateDate}": avg_dict,
                                      "indexCounts": list_dict}},
                            True
                        )
                    else:
                        # if update then update
                        pool.update_mongo(
                            source_db, 'update_count', {'_id': taskId},
                            {"$set": {"platId": platId, "matchUid": matchUid,
                                      f"showCounts.{updateDate}": avg_dict,
                                      f"saveCounts.{updateDate}": avg_dict,
                                      "indexCounts": list_dict}},
                            True
                        )
                else:
                    # if >= 10
                    popNum = True
                    minDate = updateDate
                    if showCounts:
                        for k in showCounts.keys():
                            if minDate > k:
                                minDate = k
                            if k == updateDate:
                                popNum = False
                    if not popNum:
                        pool.update_mongo(
                            source_db, 'update_count', {'_id': taskId},
                            {"$set": {f"showCounts.{updateDate}": avg_dict,
                                      f"saveCounts.{updateDate}": avg_dict,
                                      "indexCounts": list_dict}}
                        )
                    else:
                        # pop min date
                        if updateDate > minDate:
                            pool.update_mongo(
                                source_db, 'update_count', {'_id': taskId},
                                {"$unset": {f"showCounts.{minDate}": ""}}
                            )
                            pool.update_mongo(
                                source_db, 'update_count', {'_id': taskId},
                                {"$set": {f"showCounts.{updateDate}": avg_dict,
                                          f"saveCounts.{updateDate}": avg_dict,
                                          "indexCounts": list_dict}},
                                True
                            )

        end_time = TimeAct.format_timestamp() - start_time
        sql = f"insert ignore into mcn_result (result_name,result_desc," \
              f"result_date,active) values ('[计数{plat_id}]" \
              f"运行完毕{end_time}','','{time_now}',1);"
        pool.execute_mysql(sql)
        pool.execute_mysql("", True)
    except Exception as ex:
        logger.info(f"[计数{plat_id}]运行存在错误{ex}")
    finally:
        pool.close_mysql()
        pool.close_mongo(source_db)
        return False


@shared_task
def result_thread():

    all_args = []
    for i in [1, 2, 3, 4, 5, 6, 7, 8]:
        all_args.append([i])
    if all_args:
        with ThreadPoolExecutor(max_workers=len(all_args)) as t:
            all_task = [t.submit(make_result, (url)) for url in all_args]


def make_result(args):
    try:
        # define app
        pool = PoolAct()
        pool.logger = logger
        pool.init_app()
        # pool.init_mysql(
        #     "mysql://root:root@127.0.0.1:3306/manager?charset=utf8mb4")
        # source_db = pool.init_mongo("mongodb://127.0.0.1:27017/source")
        pool.init_mysql(
            "mysql://root:root@mariadb:3306/manager?charset=utf8mb4")
        source_db = pool.init_mongo("mongodb://mongodb:27017/source")
        # take args
        plat_id = args[0]
        start_time = TimeAct.format_timestamp()
        time_now = TimeAct.format_now()
        # query
        default_gen = pool.query_mongo(
            source_db, "update_count", {"platId": plat_id}, {}, []
        )
#######################################################################################
        # 粉丝最小平均增量和平均比重
        minIncrement = 0
        minProportion = 0
        default_gen, copy_gen = BaseAct.format_generator(default_gen)
        for i in copy_gen:
            showCounts = i.get("showCounts", {})
            showSum = i.get("showSum", 0)
            if showSum > 1:
                show_list = sorted([(k, v) for k, v in showCounts.items()],
                                   reverse=True)
                first_tuple = show_list[0]
                last_tuple = show_list[-1]
                first_date = first_tuple[0]
                last_date = last_tuple[0]
                first_date = TimeAct.parse_timestring(first_date, "%Y-%m-%d")
                last_date = TimeAct.parse_timestring(last_date, "%Y-%m-%d")
                days = (first_date - last_date).days
                first_fans = first_tuple[1].get("fansNum", 0)
                last_fans = last_tuple[1].get("fansNum", 0)
                if first_fans != 0:
                    avgIncrement = (first_fans - last_fans) / days
                    avgProportion = avgIncrement / first_fans
                    if abs(avgProportion) <= 0.1:
                        if avgIncrement < minIncrement:
                            minIncrement = avgIncrement
                        if avgProportion < minProportion:
                            minProportion = avgProportion
#######################################################################################
        # 粉丝 最大平均增量和平均比重  作品最大平均值
        maxIncrement = 0
        maxProportion = 0
        maxWorks = {}
        default_gen, copy_gen = BaseAct.format_generator(default_gen)
        for i in copy_gen:
            indexCounts = i.get("indexCounts", {})
            showCounts = i.get("showCounts", 0)
            showSum = i.get("showSum", 0)
            if showSum > 1:
                show_list = sorted([(k, v) for k, v in showCounts.items()],
                                   reverse=True)
                first_tuple = show_list[0]
                last_tuple = show_list[-1]
                first_date = first_tuple[0]
                last_date = last_tuple[0]
                first_date = TimeAct.parse_timestring(first_date, "%Y-%m-%d")
                last_date = TimeAct.parse_timestring(last_date, "%Y-%m-%d")
                days = (first_date - last_date).days
                first_fans = first_tuple[1].get("fansNum", 0)
                last_fans = last_tuple[1].get("fansNum", 0)
                if first_fans != 0:
                    avgIncrement = (first_fans - last_fans) / days
                    avgProportion = avgIncrement / first_fans
                    if abs(avgProportion) <= 0.1:                        
                        avgIncrement = 1.4 * (avgIncrement + abs(minIncrement))
                        avgProportion = 1.4 * (avgProportion + abs(minProportion))
                        if avgIncrement > maxIncrement:
                            maxIncrement = avgIncrement
                        if avgProportion > maxProportion:
                            maxProportion = avgProportion
            # work
            for k, v in indexCounts.items():
                if "List" in k:
                    if len(v) > 1:
                        average = NumAct.parse_average(v, 2, 10)
                        square_datas = []
                        for i in v:
                            square_datas.append((i - average) * (i - average))
                        variance = sum(square_datas) / (len(square_datas) - 1)
                        standard = math.sqrt(variance)
                        for s in v:
                            if average - standard * 3 > s > average + standard * 3:
                                v.remove(s)
                        average = NumAct.parse_average(v, 2, 10)
                        k = k.replace("List", "Max")
                        maxAvg = maxWorks.get(k, 0)
                        if average >= maxAvg:
                            maxWorks[k] = average
#######################################################################################
        # query final data
        result_gen = pool.query_mongo(
            source_db, "update",
            {"isLast": 1, "platId": plat_id},
            {"platId": 1, "matchUid": "$profileBase.matchUid",
             "envMap": 1, "homeUrl": 1, "profileBase": 1, "isUse": 1,
             "profileCounts": 1, "workList": 1}, []
        )
        for i in result_gen:
            taskId = i.get("_id")
            envMap = i.get("envMap")
            isUse = i.get("isUse")
            matchUid = i.get("matchUid")
            homeUrl = i.get("homeUrl")
            profileBase = i.get("profileBase", {})
            profileCounts = i.get("profileCounts", {})
            workList = i.get("workList", [])
            if not taskId or not profileBase:
                continue
            if isUse == 0:
                for e in envMap:
                    env_name = e.get("name")
                    env_id = e.get("id")
                    pool.update_mongo(
                        source_db, 'result', {'_id': f"{env_name}{env_id}"},
                        {"$set": {"envName": env_name, "id": env_id, "homeUrl": homeUrl,
                                  "dataLevel": 0, "status": 0}},
                        True
                    )
            elif isUse == 1:
                # index num
                powderNum = 60
                interactNum = 60
                performanceNum = 60
                trendData = {}
                expectData = {"expectPlayNum": 0, "expectCommentNum": 0,
                              "expectPraiseNum": 0, "expectShareNum": 0,
                              "expectForwardNum": 0}
                # query count data
                default_gen = pool.query_mongo(
                    source_db, "update_count", {"_id": taskId}, {}, []
                )
                for j in default_gen:
                    indexCounts = j.get("indexCounts")
                    showCounts = j.get("showCounts")
                    showSum = j.get("showSum")
                    show_list = []
                    if showSum > 1:
                        show_list = sorted([(k, v) for k, v in showCounts.items()],
                                           reverse=True)
                        first_tuple = show_list[0]
                        last_tuple = show_list[-1]
                        first_date = first_tuple[0]
                        last_date = last_tuple[0]
                        first_date = TimeAct.parse_timestring(first_date, "%Y-%m-%d")
                        last_date = TimeAct.parse_timestring(last_date, "%Y-%m-%d")
                        days = (first_date - last_date).days
                        first_fans = first_tuple[1].get("fansNum", 0)
                        last_fans = last_tuple[1].get("fansNum", 0)
                        if first_fans != 0:
                            avgIncrement = (first_fans - last_fans) / days
                            avgProportion = avgIncrement / first_fans
                            if abs(avgProportion) <= 0.1:
                                if maxIncrement != 0 and maxProportion != 0:
                                    avgIncrement = 1.4 * (avgIncrement + abs(minIncrement))
                                    avgProportion = 1.4 * (avgProportion + abs(minProportion))
                                    avgIncrement = math.log(avgIncrement + 1) / math.log(maxIncrement + 1)
                                    avgProportion = math.log(avgProportion + 1) / math.log(maxProportion + 1)
                                    avgIncrement = 1.2 * 100 / (1 + math.exp(-avgIncrement)) + 1
                                    avgProportion = 1.2 * 100 / (1 + math.exp(-avgProportion)) + 1
                                    powderNum = NumAct.parse_average([avgIncrement, avgProportion])
                                    powderNum = int(powderNum)
                                    if not powderNum:
                                        powderNum = 60
#######################################################################################
                    # 作品分析
                    interactList = []
                    if indexCounts:
                        for k, v in indexCounts.items():
                            if "Avg" in k:
                                if "playAvg" == k:
                                    expectData["expectPlayNum"] = round(v, 2)
                                elif "commentAvg" == k:
                                    expectData["expectCommentNum"] = round(v, 2)
                                elif "likeAvg" == k:
                                    expectData["expectPraiseNum"] = round(v, 2)
                                elif "shareAvg" == k:
                                    expectData["expectShareNum"] = round(v, 2)
                                elif "forwardAvg" == k:
                                    expectData["expectForwardNum"] = round(v, 2)
                            elif "List" in k:
                                if len(v) > 1:
                                    average = NumAct.parse_average(v, 2, 10)
                                    square_datas = []
                                    for i in v:
                                        square_datas.append((i - average) * (i - average))
                                    variance = sum(square_datas) / (len(square_datas) - 1)
                                    standard = math.sqrt(variance)
                                    for s in v:
                                        if average - standard * 3 > s > average + standard * 3:
                                            v.remove(s)
                                    average = NumAct.parse_average(v, 2, 10)
                                    
                                    k = k.replace("List", "Max")
                                    maxAvg = maxWorks.get(k, 0)
                                    if maxAvg != 0:
                                        average = math.log(average + 1) / math.log(maxAvg + 1)
                                        average = 1.2 * 100 / (1 + math.exp(-average)) + 1
                                        
                                        interactList.append(average)

                    interactNum = NumAct.parse_average(interactList, 2, 10)
                    interactNum = int(interactNum)
                    if not interactNum:
                        interactNum = 60
#######################################################################################
                    if show_list:
                        # 等于1 复制
                        if len(show_list) == 1:
                            add_item = show_list[0]
                            for s in range(9):
                                show_list.append(add_item)
                        elif len(show_list) < 10:
                            # 差数
                            add_num = 10 - len(show_list)
                            last_item = show_list[-1]
                            last_day = last_item[0]
                            last_value = last_item[1]

                            last_day = TimeAct.parse_timestring(last_day, "%Y-%m-%d")
                            # 扩展sort list
                            for s in range(1, add_num + 1):
                                custom_day = TimeAct.parse_custom(last_day, -1 * s)
                                custom_day = custom_day.strftime('%Y-%m-%d')
                                show_list.append((custom_day, last_value))

                        trendData["trendFans"] = []
                        trendData["trendComment"] = []
                        trendData["trendPraise"] = []
                        trendData["trendForward"] = []
                        trendData["trendShare"] = []
                        trendData["trendPlay"] = []
                        for s in reversed(show_list):
                            trendData["trendFans"].append(
                                {"name": s[0], "value": s[1].get("fansNum", 0)})
                            trendData["trendComment"].append(
                                {"name": s[0], "value": s[1].get("commentAvg", 0)})
                            trendData["trendPraise"].append(
                                {"name": s[0], "value": s[1].get("likeAvg", 0)})
                            trendData["trendForward"].append(
                                {"name": s[0], "value": s[1].get("forwardAvg", 0)})
                            trendData["trendShare"].append(
                                {"name": s[0], "value": s[1].get("shareAvg", 0)})
                            trendData["trendPlay"].append(
                                {"name": s[0], "value": s[1].get("playAvg", 0)})
#######################################################################################  
                # must platId and workList for old name plantId and worksList
                return_dict = {"plantId": plat_id, "status": 1,
                               "dataLevel": 1, "homeUrl": homeUrl,
                               "worksList": workList, "powderNum": powderNum,
                               "interactNum": interactNum,
                               "performanceNum": performanceNum}
                return_dict = return_dict | profileBase | profileCounts | expectData | trendData
                # query match data
                # @@..! db.update_match.ensureIndex({"platId":1,"matchUid":1})
                if matchUid:
                    match_dict = {}
                    match_gen = pool.query_mongo(
                        source_db, "update_match",
                        {'platId': plat_id, 'matchUid': matchUid}, {}, []
                    )
                    for w in match_gen:
                        # except bilibili update field
                        if plat_id != 3:
                            match_dict['field'] = w.get("field", "")
                        # douyin price
                        if plat_id == 1:
                            return_dict['gender'] = w.get("gender", 0)
                            return_dict['area'] = w.get("area", "")
                            match_dict['video20'] = w.get("video20", 0)
                            match_dict['video60'] = w.get("video60", 0)

                        match_dict['fansActiveTime'] = w.get("fansActiveTime", "")
                        match_dict['fansCity'] = w.get("fansCity", "")
                        match_dict['fansProperties'] = w.get("fansProperties", "")
                        match_dict['fansPreference'] = w.get("fansPreference", "")
                        match_dict['reportAge'] = w.get("reportAge", [])
                        match_dict['reportCity'] = w.get("reportCity", [])
                        match_dict['reportFans'] = w.get("reportFans", [])
                        match_dict['reportActive'] = w.get("reportActive", [])
                        match_dict['reportDevice'] = w.get("reportDevice", [])
                        match_dict['dataLevel'] = 2
                    if match_dict:
                        return_dict = return_dict | match_dict
                        
                    for e in envMap:
                        env_name = e.get("name")
                        env_id = e.get("id")
                        return_dict.update({"envName": env_name, "id": env_id})
                        pool.update_mongo(
                            source_db, 'result', {'_id': f"{env_name}{env_id}"},
                            {"$set": return_dict}, True
                        )

        end_time = TimeAct.format_timestamp() - start_time
        sql = f"insert ignore into mcn_result (result_name,result_desc," \
              f"result_date,active) values ('[清洗{plat_id}]" \
              f"数据完毕{end_time}','','{time_now}',1);"
        pool.execute_mysql(sql)
        pool.execute_mysql("", True)

    except Exception as ex:
        logger.info(f"[清洗{plat_id}]运行存在错误{ex}")
    finally:
        pool.close_mysql()
        pool.close_mongo(source_db)
        return False


@shared_task
def clean_result():
    try:
        # define app
        pool = PoolAct()
        pool.logger = logger
        pool.init_app()
        # pool.init_mysql(
        #     "mysql://root:root@127.0.0.1:3306/manager?charset=utf8mb4")
        pool.init_mysql(
            "mysql://root:root@mariadb:3306/manager?charset=utf8mb4")
        now = TimeAct.format_now()
        yestoday = TimeAct.parse_custom(now, -1)
        sql = f"delete from mcn_result where result_date < '{yestoday}';"
        pool.execute_mysql(sql)
        pool.execute_mysql("", True)
    except Exception as ex:
        logger.info(f"[日志clean]运行存在错误{ex}")
    finally:
        pool.close_mysql()
        return False


@shared_task
def test():
    try:
        pool = PoolAct()
        pool.logger = logger
        pool.init_app()
        
        # source_db = pool.init_mongo("mongodb://127.0.0.1:27017/source")
        source_db = pool.init_mongo("mongodb://mongodb:27017/source")

        result_gen = pool.query_mongo(
            source_db, "update_count",
            {"platId": 5},
            {"saveCounts": 1, "showCounts": 1},
            []
        )
        # update userId and matchUid
        for i in result_gen:
            unique_id = i.get("_id")
            saveCounts = i.get("saveCounts", {})
            showCounts = i.get("showCounts", {})
            showSum = 0
            if saveCounts:
                if "2021-10-11" in saveCounts:
                    del saveCounts["2021-10-11"]
                if "2021-10-12" in saveCounts:
                    del saveCounts["2021-10-12"]
            if showCounts:
                if "2021-10-11" in showCounts:
                    del showCounts["2021-10-11"]
                if "2021-10-12" in showCounts:
                    del showCounts["2021-10-12"]
                showSum = len(showCounts)

            pool.update_mongo(
                source_db, "update_count",
                {"_id": unique_id},
                {"$set": {"saveCounts": saveCounts, "showCounts": showCounts, "showSum": showSum}}
            )

        logger.info("[测试test]运行完毕，over")
    except Exception as ex:
        logger.info(f"[测试test]运行存在错误{ex}")
    finally:
        pool.close_mongo(source_db)
        return False



if __name__ == "__main__":

    # sync_thread(4)
    # for i in [3, 4]:
    #     queue_thread(1, i, "tapi")
    # for i in [2]:
    #     queue_thread(2, i, "tapi")
    # for i in [1, 3]:
    #     send_thread(i)
    # quick_thread()
    # count_thread()
    # result_thread()
    # make_price()
    # clean_result()
    test()
