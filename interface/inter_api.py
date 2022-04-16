#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> inter api
@@..> package interface
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> import current path
import sys
sys.path.append('..')
# @@..> base import
# from concurrent.futures import ThreadPoolExecutor
# from werkzeug.middleware.proxy_fix import ProxyFix
from flask import jsonify
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
from flask_compress import Compress
# @@..> import utils
from utils.base_tools import BaseAct, LogAct
from utils.num_tools import TimeAct
from utils.pool_tools import PoolAct
from utils.str_tools import StrAct


logger, handler = LogAct.init_log("inter_api.log", False)
# logger, handler = LogAct.init_log("inter_api.log")
StrAct.logger = logger
TimeAct.logger = logger
pool = PoolAct()
pool.logger = logger
pool.init_app()
app = pool.app
# dashboard_db = pool.init_mongo("mongodb://127.0.0.1:27017/dashboard")
dashboard_db = pool.init_mongo("mongodb://mongodb:27017/dashboard")
CORS(app, supports_credentials=True)
Compress(app)
api = Api(app)


#######################################################################################
def filter_result(col: str = None, pid: int = 0, cid: int = 0, fid: int = 0,
                  isDay: bool = True, startDate: int = 0, endDate: int = 0):

    query_dict = {"dayTime": {"$gte": startDate, "$lte": endDate}}
    if pid == -1:
        query_dict.update({"pid": {"$ne": 0}})
    else:
        query_dict.update({"pid": pid})

    if cid == -1:
        query_dict.update({"cid": {"$ne": 0}})
    else:
        query_dict.update({"cid": cid})

    if fid == -1:
        query_dict.update({"fid": {"$ne": 0}})
    else:
        query_dict.update({"fid": fid})

    if isDay:
        result_gen = pool.query_mongo(
            dashboard_db, col, query_dict, {"_id": 0}, []
        )
    else:
        result_gen = pool.query_mongo(
            dashboard_db, col, query_dict, {"_id": 0, "dayTime": 0}, []
        )
    return result_gen


def get_base():
    result_gen = pool.query_mongo(
        dashboard_db, "system_class", {"pid": 1},
        {"_id": 0, "platMap": 1, "mediumMap": 1, "parentMap": 1,
         "childMap": 1, "categoryMap": 1, "organizationMap": 1,
         "advertMap": 1}, [] 
    )
    result_dict, result_gen = BaseAct.parse_generator(result_gen)
    if result_dict:
        return jsonify({"status": "ok", "message": "", "data": result_dict})
    else:
        return jsonify({"status": "error", "message": "查无此信息", "data": {}})


class Base(Resource):
    def get(self):
        return get_base()


api.add_resource(Base, '/api/base')


date_parser = reqparse.RequestParser()
date_parser.add_argument('startDate', type=str, required=True, location='args')
date_parser.add_argument('endDate', type=str, required=True, location='args')
date_parser.add_argument('pid', type=int, required=False, location='args')
date_parser.add_argument('cid', type=int, required=False, location='args')
date_parser.add_argument('fid', type=int, required=False, location='args')


def get_overview():

    req = date_parser.parse_args(strict=True)
    start_date = req.get("startDate")
    end_date = req.get("endDate")
    pid = req.get("pid")
    cid = req.get("cid")
    fid = req.get("fid")
    try:
        start_date = StrAct.parse_replace(start_date, "-", "")
        end_date = StrAct.parse_replace(end_date, "-", "")
        days_gen = TimeAct.format_datelist(start_date, end_date, 1, "%Y%m%d")
        days_list = list(days_gen)

        start_int = StrAct.parse_integer(start_date)
        end_int = StrAct.parse_integer(end_date)
        start_int, int_gen = BaseAct.parse_generator(start_int)
        end_int, int_gen = BaseAct.parse_generator(end_int)

        platMap = {}
        mediumMap = {}
        categoryMap = {}

        result_gen = pool.query_mongo(
            dashboard_db, "system_class", {"pid": 1},
            {"_id": 0, "platMap": 1, "mediumMap": 1, "categoryMap": 1}, [] 
        )
        for r in result_gen:
            platMap = r["platMap"]
            mediumMap = r["mediumMap"]
            categoryMap = r["categoryMap"]
            pids_list = [i for i in platMap.keys()]
            mids_list = [i for i in mediumMap.keys()]
            cids_list = [i for i in categoryMap.keys()]

        sum_total = {}
        source_total = {}
        plat_total = {}
        medium_total = {}
        organization_total = {}
        advert_total = {}
        cate_total = {}
        parent_total = {}
        child_total = {}

        account_list = [
            "allAccount", "medAccount", "appAccount", "perAccount",
            "orgAccount", "putAccount", "livAccount", "notAccount",
        ]
        media_list = [
            "regMedia", "setMedia", "perMedia", "orgMedia",
        ]
        immedia_list = [
            "cmcIMMedia", "useIMMedia", "msgIMMedia", "urmIMMedia",
            "stcIMMedia", "stmIMMedia",
        ]
        acmedia_list = [
            "actMedia", "sltMedia", "losMedia", "bakMedia", "awkMedia",
            "enlMedia", "cprMedia", "secMedia", "thdMedia", "aorMedia",
        ]
        im_list = ["cmcIM", "cusIM", "msgIM", "urmIM", ]

        advert_list = [
            "regAdvert", "setAdvert", "brdAdvert", "agtAdvert",
            "cmcIMAdvert", "useIMAdvert", "stcIMAdvert", "staIMAdvert",
            "msgIMAdvert", "urmIMAdvert",
        ]

        task_list = [
            "allTask", "ivtTask", "recTask", "prgTask", "endTask", "wtaTask",
            "excTask", "pubTask", "cmpTask", "clsTask", "padTask",
            "onsTask", "offTask",

            "renTask", "cmsTask", "prdGood",
            "pitTask", "sbsTask", "cosTask", "quoTask",
            "pitPrice", "sbsPrice", "cosPrice", "quoPrice",

            "ivtOrder", "prgOrder", "wtaOrder",
            "excOrder", "pubOrder", "cmpOrder", "clsOrder",
        ]

        organization_list = ["allAccount", "smfAccount", "avfAccount"]
        
        # 建立数据结构
        for i in account_list + media_list + immedia_list + acmedia_list \
                + im_list + advert_list + task_list:
            sum_total[i] = {"sum": 0, "list": {}}
            for j in days_list:
                sum_total[i]["list"][j] = 0

        # 查询并赋值
        result_gen = filter_result("medium_class", 0, 0, 0, True, start_int, end_int)
        for i in result_gen:
            dayTime = str(i['dayTime'])
            for k, v in sum_total.items():
                check = i.get(k)
                if check:
                    v["list"][dayTime] = i[k]

        # 查询并赋值
        result_gen = filter_result("child_class", 0, 0, 0, True, start_int, end_int)
        for i in result_gen:
            dayTime = str(i['dayTime'])
            for k, v in sum_total.items():
                check = i.get(k)
                if check:
                    v["list"][dayTime] = i[k]

        # 赋值sum数据
        for k, v in sum_total.items():
            k_sum = 0
            # 判断是不是活跃列表
            if k in acmedia_list:
                for kk, vv in v["list"].items():
                    if str(kk) == end_date:
                        k_sum = vv
                sum_total[k]["sum"] = k_sum
            else:
                for kk, vv in v["list"].items():
                    k_sum = round(k_sum + vv, 2)
                sum_total[k]["sum"] = k_sum

        # 根据赋值重构
        for k, v in sum_total.items():
            k_list = []
            for kk, vv in v["list"].items():
                k_list.append(vv)

            sum_total[k]['list'] = k_list
        
        # 建立source数据结构
        for i in acmedia_list + media_list:
            source_total[i] = {}
            for s in ["1", "2"]:
                source_total[i][s] = {"sum": 0, "list": {}}
                for j in days_list:
                    source_total[i][s]["list"][j] = 0

        # 查询并赋值
        result_gen = filter_result("source_class", 0, -1, 0, True, start_int, end_int)
        for i in result_gen:
            dayTime = str(i['dayTime'])
            cid = str(i['cid'])
            for k, v in source_total.items():
                check = i.get(k)
                if check:
                    if k in media_list:
                        source_total[k][cid]["list"][dayTime] = i[k]
                        source_total[k][cid]['sum'] += i[k]
                    else:
                        source_total[k][cid]["list"][dayTime] = i[k]
                        if dayTime == end_date:
                            source_total[k][cid]['sum'] = i[k]

        # 根据赋值重构
        for k, v in source_total.items():
            for s in ["1", "2"]:
                k_list = []
                for kk, vv in source_total[k][s]["list"].items():
                    k_list.append(vv)

                source_total[k][s]['list'] = k_list

        # 分平台建立数据结构
        for i in account_list + media_list + immedia_list + acmedia_list + task_list:
            plat_total[i] = {}
            for j in pids_list:
                plat_total[i][j] = 0

        # 查询并赋值
        result_gen = filter_result("medium_class", -1, 0, 0, True, start_int, end_int)
        for i in result_gen:
            dayTime = i['dayTime']
            single_pid = str(i['pid'])
            for k, v in plat_total.items():
                check = v.get(single_pid)
                if check is not None:
                    if k in acmedia_list:
                        if dayTime == int(end_date):
                            v[single_pid] = i.get(k, 0)
                    else:
                        v[single_pid] += i.get(k, 0)

        # 查询并赋值
        result_gen = filter_result("fans_class", -1, 0, 0, False, start_int, end_int)
        for i in result_gen:
            single_pid = str(i['pid'])
            for k, v in plat_total.items():
                check = v.get(single_pid)
                if check is not None:
                    v[single_pid] = round(check + i.get(k, 0), 2)
        # 分媒介建立数据结构
        for i in account_list + media_list + immedia_list + acmedia_list:
            medium_total[i] = {}
            for j in mids_list:
                medium_total[i][j] = 0
        # 查询并赋值
        result_gen = filter_result("medium_class", 0, -1, 0, True, start_int, end_int)
        for i in result_gen:
            dayTime = i['dayTime']
            single_cid = str(i['cid'])
            for k, v in medium_total.items():
                check = v.get(single_cid)
                if check is not None:
                    if k in acmedia_list:
                        if dayTime == int(end_date): 
                            v[single_cid] = i.get(k, 0)
                    else:
                        v[single_cid] += i.get(k, 0)
        
        # 机构建立数据结构
        for i in organization_list:
            organization_total[i] = {}
        # 查询并赋值
        result_gen = filter_result("role_class", 1, -1, 0, False, start_int, end_int)
        for i in result_gen:
            single_cid = i['cid']
            for k, v in organization_total.items():
                check = v.get(single_cid)
                if check is None:
                    v[single_cid] = i.get(k, 0)
                else:
                    v[single_cid] = round(check + i.get(k, 0), 2)

        # 前20
        for k, v in organization_total.items():
            sorted_tuple = sorted(v.items(), key=lambda x: x[1], reverse=True)
            organization_total[k] = sorted_tuple[:20]
        
        # 广告主建立数据结构
        for i in task_list:
            advert_total[i] = {}
        # 查询并赋值
        result_gen = filter_result("role_class", 2, -1, 0, False, start_int, end_int)
        for i in result_gen:
            single_cid = i['cid']
            for k, v in advert_total.items():
                check = v.get(single_cid)
                if check is None:
                    v[single_cid] = i.get(k, 0)
                else:
                    v[single_cid] = round(check + i.get(k, 0), 2)

        # 前20
        for k, v in advert_total.items():
            sorted_tuple = sorted(v.items(), key=lambda x: x[1], reverse=True)
            advert_total[k] = sorted_tuple[:20]
        
        # 领域建立数据结构
        for i in account_list + task_list:
            cate_total[i] = {}
        # 查询并赋值
        result_gen = filter_result("medium_class", 0, 0, -1, False, start_int, end_int)
        for i in result_gen:
            single_fid = i['fid']
            for k, v in cate_total.items():
                check = v.get(single_fid)
                if check is None:
                    v[single_fid] = i.get(k, 0)
                else:
                    v[single_fid] += i.get(k, 0)
        # 查询并赋值
        result_gen = filter_result("child_class", 0, 0, -1, False, start_int, end_int)
        for i in result_gen:
            single_fid = i['fid']
            for k, v in cate_total.items():
                check = v.get(single_fid)
                if check is None:
                    v[single_fid] = i.get(k, 0)
                else:
                    v[single_fid] = round(check + i.get(k, 0), 2)
        
        # 前20
        for k, v in cate_total.items():
            sorted_tuple = sorted(v.items(), key=lambda x: x[1], reverse=True)
            cate_total[k] = sorted_tuple[:20]

        # 行业建立数据结构
        for i in advert_list + task_list:
            parent_total[i] = {}
            child_total[i] = {}
        # 查询并赋值
        result_gen = filter_result("child_class", -1, 0, 0, False, start_int, end_int)
        for i in result_gen:
            single_pid = i['pid']
            for k, v in parent_total.items():
                check = v.get(single_pid)
                if check is None:
                    v[single_pid] = i.get(k, 0)
                else:
                    v[single_pid] = round(check + i.get(k, 0), 2)

        # 前20
        for k, v in parent_total.items():
            sorted_tuple = sorted(v.items(), key=lambda x: x[1], reverse=True)
            parent_total[k] = sorted_tuple[:20]

        # 查询并赋值
        result_gen = filter_result("child_class", -1, -1, 0, False, start_int, end_int)
        for i in result_gen:
            single_cid = i['cid']
            for k, v in child_total.items():
                check = v.get(single_cid)
                if check is None:
                    v[single_cid] = i.get(k, 0)
                else:
                    v[single_cid] = round(check + i.get(k, 0), 2)

        # 前20
        for k, v in child_total.items():
            sorted_tuple = sorted(v.items(), key=lambda x: x[1], reverse=True)
            child_total[k] = sorted_tuple[:20]
            
        return_dict = {
            "platMap": platMap, "mediumMap": mediumMap, "categoryMap": categoryMap,
            "daysList": days_list, "sumTotal": sum_total, "sourceTotal": source_total,
            "platTotal": plat_total, "mediumTotal": medium_total,
            "cateTotal": cate_total, "parentTotal": parent_total,
            "childTotal": child_total,
            "organizationTotal": organization_total, "advertTotal": advert_total
        }

        return jsonify({"status": "ok", "message": "", "data": return_dict})
    except Exception as ex:
        logger.info("数据库问题")
        logger.info(ex)
        return jsonify({"status": "error", "message": "连接超时", "data": {}})


class Overview(Resource):
    def get(self):
        return get_overview()


api.add_resource(Overview, '/api/overview')


def get_medium():

    req = date_parser.parse_args(strict=True)
    start_date = req.get("startDate")
    end_date = req.get("endDate")
    pid = req.get("pid")
    cid = req.get("cid")
    fid = req.get("fid")
    try:
        start_date = StrAct.parse_replace(start_date, "-", "")
        end_date = StrAct.parse_replace(end_date, "-", "")
        days_gen = TimeAct.format_datelist(start_date, end_date, 1, "%Y%m%d")
        days_list = list(days_gen)

        start_int = StrAct.parse_integer(start_date)
        end_int = StrAct.parse_integer(end_date)
        start_int, int_gen = BaseAct.parse_generator(start_int)
        end_int, int_gen = BaseAct.parse_generator(end_int)

        platAllMap = {"1": "dysAccount", "2": "kssAccount", "3": "blsAccount",
                      "4": "hssAccount", "5": "wbsAccount", "6": "wxsAccount",
                      "7": "zhsAccount", "8": "ttsAccount"}

        platMap = {}
        mediumMap = {}
        categoryMap = {}
        result_gen = pool.query_mongo(
            dashboard_db, "system_class", {"pid": 1},
            {"_id": 0, "platMap": 1, "mediumMap": 1, "categoryMap": 1}, []
        )
        for r in result_gen:
            platMap = r["platMap"]
            mediumMap = r["mediumMap"]
            categoryMap = r["categoryMap"]
            pids_list = [i for i in platMap.keys()]
            mids_list = [i for i in mediumMap.keys()]
            cids_list = [i for i in categoryMap.keys()]

        medium_total = {}
        medium_plat = {}
        medium_category = {}
        category_all = {}
        category_plat = {}

        account_list = [
            "allAccount", "medAccount", "appAccount", "perAccount",
            "orgAccount", "putAccount", "livAccount", "notAccount",
        ]
        media_list = [
            "regMedia", "setMedia", "perMedia", "orgMedia",
            "cmcIMMedia", "useIMMedia", "msgIMMedia", "urmIMMedia",
            "stcIMMedia", "stmIMMedia",
        ]
        active_list = [
            "actMedia", "sltMedia", "losMedia", "bakMedia", "awkMedia",
            "enlMedia", "cprMedia", "secMedia", "thdMedia", "aorMedia",
        ]

        # 媒介个人总数
        for i in account_list:
            medium_total[i] = {"sum": 0}
        # 查询并赋值
        result_gen = filter_result(
            "medium_class", 0, cid, 0, False, start_int, end_int)
        for i in result_gen:
            for k, v in medium_total.items():
                medium_total[k]['sum'] += i.get(k, 0)

        # 媒介分平台
        for i in account_list + media_list + active_list:
            medium_plat[i] = {"pids": {}}
            for j in pids_list:
                medium_plat[i]['pids'][j] = 0

        result_gen = filter_result(
            "medium_class", -1, cid, 0, True, start_int, end_int)
        for i in result_gen:
            dayTime = str(i['dayTime'])
            single_pid = str(i['pid'])
            for k, v in medium_plat.items():
                check = v['pids'].get(single_pid)
                if check is not None:
                    if k in active_list:
                        if dayTime == end_date:
                            v['pids'][single_pid] = i.get(k, 0)
                    else:
                        v['pids'][single_pid] += i.get(k, 0)

        # 媒介平台分领域
        for i in account_list + media_list + active_list:
            medium_category[i] = {"fids": {}}
            for j in cids_list:
                medium_category[i]['fids'][j] = 0

        result_gen = filter_result(
            "medium_class", pid, cid, -1, True, start_int, end_int)
        for i in result_gen:
            dayTime = str(i['dayTime'])
            single_cid = str(i['fid'])
            for k, v in medium_category.items():
                check = v['fids'].get(single_cid)
                if check is not None:
                    if k in active_list:
                        if dayTime == end_date:
                            v['fids'][single_cid] = i.get(k, 0)
                    else:
                        v['fids'][single_cid] += i.get(k, 0)

        # 领域分平台
        for i in account_list + media_list + active_list:
            category_all[i] = {"fids": {}}
            for j in cids_list:
                category_all[i]['fids'][j] = 0

        result_gen = filter_result(
            "medium_class", 0, cid, -1, False, start_int, end_int)
        for i in result_gen:
            for k, v in category_all.items():
                single_cid = str(i['fid'])
                check = v['fids'].get(single_cid)
                if check is not None:
                    v['fids'][single_cid] += i.get(k, 0)

        for i in pids_list:
            category_plat[i] = {"fids": {}}
            for j in cids_list:
                category_plat[i]['fids'][j] = 0

        result_gen = filter_result(
            "medium_class", -1, cid, -1, False, start_int, end_int)
        for i in result_gen:
            for k, v in category_plat.items():
                single_pid = str(i['pid'])
                single_cid = str(i['fid'])
                if k == single_pid:
                    check = v['fids'].get(single_cid)
                    if check is not None:
                        v['fids'][single_cid] += i.get("allAccount", 0)

        for k, v in platAllMap.items():
            for kk in category_plat.keys():
                if kk == k:
                    category_all[v] = category_plat[kk] 
                    # category_plat[v] = category_plat.pop(kk)

        # category_plat.update(category_all)

        return_dict = {
            "platMap": platMap, "mediumMap": mediumMap, "categoryMap": categoryMap,
            "mediumTotal": medium_total, "mediumPlat": medium_plat,
            "mediumCategory": medium_category, "categoryPlat": category_all}
        return jsonify({"status": "ok", "message": "", "data": return_dict})
    except Exception as ex:
        logger.info("数据库问题")
        logger.info(ex)
        return jsonify({"status": "error", "message": "连接超时", "data": {}})


class Medium(Resource):
    def get(self):
        return get_medium()


api.add_resource(Medium, '/api/medium')


def get_plat():

    req = date_parser.parse_args(strict=True)
    start_date = req.get("startDate")
    end_date = req.get("endDate")
    pid = req.get("pid")
    cid = req.get("cid")
    fid = req.get("fid")
    try:
        start_date = StrAct.parse_replace(start_date, "-", "")
        end_date = StrAct.parse_replace(end_date, "-", "")
        days_gen = TimeAct.format_datelist(start_date, end_date, 1, "%Y%m%d")
        days_list = list(days_gen)
        
        start_int = StrAct.parse_integer(start_date)
        end_int = StrAct.parse_integer(end_date)
        start_int, int_gen = BaseAct.parse_generator(start_int)
        end_int, int_gen = BaseAct.parse_generator(end_int)

        platMap = {}
        mediumMap = {}
        categoryMap = {}
        result_gen = pool.query_mongo(
            dashboard_db, "system_class", {"pid": 1},
            {"_id": 0, "platMap": 1, "mediumMap": 1, "categoryMap": 1}, []
        )
        for r in result_gen:
            platMap = r["platMap"]
            mediumMap = r["mediumMap"]
            categoryMap = r["categoryMap"]
            pids_list = [i for i in platMap.keys()]
            mids_list = [i for i in mediumMap.keys()]
            fids_list = [i for i in categoryMap.keys()]
            fans_list = [i for i in range(1, 7)]

        all_total = {}
        sum_total = {}
        fans_total = {}
        cate_total = {}
        fans_cate = {}

        account_list = [
            "allAccount", "medAccount", "appAccount", "perAccount",
            "orgAccount", "putAccount", "livAccount", "notAccount",
        ]
        avg_list = [
            "allFans", "medFans", "appFans", "perFans",
            "orgFans", "putFans", "livFans", "notFans",
            "a20Fans", "a60Fans", "aviFans", "avcFans", "aodFans",
            "apdFans", "avdFans", "awtFans", "attFans", "aztFans"
        ]
        media_list = [
            "regMedia", "setMedia", "perMedia", "orgMedia",
        ]
        immedia_list = [
            "cmcIMMedia", "useIMMedia", "msgIMMedia", "urmIMMedia",
            "stcIMMedia", "stmIMMedia",
        ]
        acmedia_list = [
            "actMedia", "sltMedia", "losMedia", "bakMedia", "awkMedia",
            "enlMedia", "cprMedia", "secMedia", "thdMedia", "aorMedia",
        ]
        task_list = [
            "allTask", "ivtTask", "recTask", "prgTask", "endTask", "wtaTask",
            "excTask", "pubTask", "cmpTask", "clsTask", "padTask",
            "onsTask", "offTask",

            "renTask", "cmsTask", "prdGood",
            "pitTask", "sbsTask", "cosTask", "quoTask",
            "pitPrice", "sbsPrice", "cosPrice", "quoPrice",

            "ivtOrder", "prgOrder", "wtaOrder",
            "excOrder", "pubOrder", "cmpOrder", "clsOrder",

            "avpGood", "avpPrice"
        ]

        # 建立不变总数结构
        for i in account_list + media_list:
            all_total[i] = 0
        # 查询并赋值
        result_gen = filter_result(
            "medium_class", pid, 0, 0, False, start_int, end_int)
        for i in result_gen:
            for k, v in all_total.items():
                all_total[k] = round(v + i.get(k, 0), 2)

        # 建立数据结构
        for i in account_list + media_list + immedia_list \
                + acmedia_list + task_list:
            sum_total[i] = {"sum": 0, "list": {}}
            for j in days_list:
                sum_total[i]["list"][j] = 0

        # 查询并赋值
        result_gen = filter_result(
            "medium_class", pid, 0, fid, True, start_int, end_int)
        for i in result_gen:
            dayTime = str(i['dayTime'])
            for k, v in sum_total.items():
                check = i.get(k)
                if check:
                    v["list"][dayTime] = i[k]

        # 查询并赋值
        result_gen = filter_result(
            "child_class", pid, 0, fid, True, start_int, end_int)
        for i in result_gen:
            dayTime = str(i['dayTime'])
            for k, v in sum_total.items():
                check = i.get(k)
                if check:
                    v["list"][dayTime] = i[k]

        # 赋值sum数据
        for k, v in sum_total.items():
            k_sum = 0
            # 判断是不是活跃列表
            if k in acmedia_list:
                for kk, vv in v["list"].items():
                    if str(kk) == end_date:
                        k_sum = vv
                sum_total[k]["sum"] = k_sum
            else:
                for kk, vv in v["list"].items():
                    k_sum = round(k_sum + vv, 2)
                sum_total[k]["sum"] = k_sum

        # 根据赋值重构
        for k, v in sum_total.items():
            k_list = []
            for kk, vv in v["list"].items():
                k_list.append(vv)

            sum_total[k]['list'] = k_list

        # 领域建立数据结构
        for i in account_list + task_list:
            cate_total[i] = {}
        # 查询并赋值
        result_gen = filter_result(
            "medium_class", pid, 0, -1, False, start_int, end_int)
        for i in result_gen:
            single_fid = i['fid']
            for k, v in cate_total.items():
                check = v.get(single_fid)
                if check is None:
                    v[single_fid] = i.get(k, 0)
                else:
                    v[single_fid] = round(check + i.get(k, 0), 2)
        # 查询并赋值
        result_gen = filter_result(
            "child_class", pid, 0, -1, False, start_int, end_int)
        for i in result_gen:
            single_fid = i['fid']
            for k, v in cate_total.items():
                check = v.get(single_fid)
                if check is None:
                    v[single_fid] = i.get(k, 0)
                else:
                    v[single_fid] = round(check + i.get(k, 0), 2)

        # 前20
        for k, v in cate_total.items():
            sorted_tuple = sorted(v.items(), key=lambda x: x[1], reverse=True)
            cate_total[k] = sorted_tuple[:20]

        # 粉丝分档
        for i in task_list + avg_list:
            fans_total[i] = {}
            for j in fans_list:
                fans_total[i].update({j: 0})

        result_gen = filter_result(
            "fans_class", pid, -1, 0, False, start_int, end_int)
        for i in result_gen:
            for k, v in fans_total.items():
                single_cid = i['cid']
                check = v.get(single_cid)
                if check is not None:
                    v[single_cid] = round(check + i.get(k, 0), 2)

        # 粉丝领域
        for i in task_list + avg_list:
            fans_cate[i] = {}
            for j in fans_list:
                fans_cate[i].update({str(j): {}})

        for i in fans_cate:
            for j in fans_list:
                for k in fids_list:
                    fans_cate[i][str(j)].update({k: 0})

        result_gen = filter_result(
            "fans_class", pid, -1, -1, False, start_int, end_int)
        for i in result_gen:
            single_cid = str(i['cid'])
            single_fid = str(i['fid'])
            for k, v in fans_cate.items():
                check = v.get(single_cid, {}).get(single_fid)
                if check is not None:
                    v[single_cid][single_fid] = round(check + i.get(k, 0), 2)

        return_dict = {
            "platMap": platMap, "mediumMap": mediumMap, "categoryMap": categoryMap,
            "daysList": days_list, "allTotal": all_total, "sumTotal": sum_total,
            "cateTotal": cate_total, "fansTotal": fans_total, "fansCate": fans_cate
        }
        return jsonify({"status": "ok", "message": "", "data": return_dict})
    except Exception as ex:
        logger.info("数据库问题")
        logger.info(ex)
        return jsonify({"status": "error", "message": "连接超时", "data": {}})


class PlatCate(Resource):
    def get(self):
        return get_plat()


api.add_resource(PlatCate, '/api/plat')


def get_industry():

    req = date_parser.parse_args(strict=True)
    start_date = req.get("startDate")
    end_date = req.get("endDate")
    pid = req.get("pid")
    cid = req.get("cid")
    fid = req.get("fid")
    try:
        start_date = StrAct.parse_replace(start_date, "-", "")
        end_date = StrAct.parse_replace(end_date, "-", "")
        days_gen = TimeAct.format_datelist(start_date, end_date, 1, "%Y%m%d")
        days_list = list(days_gen)
        
        start_int = StrAct.parse_integer(start_date)
        end_int = StrAct.parse_integer(end_date)
        start_int, int_gen = BaseAct.parse_generator(start_int)
        end_int, int_gen = BaseAct.parse_generator(end_int)

        parentMap = {}
        childMap = {}
        categoryMap = {}
        result_gen = pool.query_mongo(
            dashboard_db, "system_class", {"pid": 1},
            {"_id": 0, "parentMap": 1, "childMap": 1, "categoryMap": 1}, []
        )
        for r in result_gen:
            parentMap = r["parentMap"]
            childMap = r["childMap"]
            categoryMap = r["categoryMap"]
            pids_list = [i for i in parentMap.keys()]
            cids_list = [i for i in childMap.keys()]
            fids_list = [i for i in categoryMap.keys()]

        sum_total = {}
        cate_total = {}
        indus_total = {}

        advert_list = [
            "regAdvert", "setAdvert", "brdAdvert", "agtAdvert",
            "cmcIMAdvert", "useIMAdvert", "stcIMAdvert", "staIMAdvert",
            "msgIMAdvert", "urmIMAdvert",
        ]

        task_list = [
            "allTask", "ivtTask", "recTask", "prgTask", "endTask", "wtaTask", 
            "excTask", "pubTask", "cmpTask", "clsTask", "padTask",
            "onsTask", "offTask",

            "renTask", "cmsTask", "prdGood",
            "pitTask", "sbsTask", "cosTask", "quoTask",
            "pitPrice", "sbsPrice", "cosPrice", "quoPrice",

            "ivtOrder", "prgOrder", "wtaOrder",
            "excOrder", "pubOrder", "cmpOrder", "clsOrder",
        ]

        # 建立数据结构
        for i in advert_list + task_list:
            sum_total[i] = {"sum": 0, "list": {}}
            for j in days_list:
                sum_total[i]["list"][j] = 0

        # 查询并赋值
        result_gen = filter_result(
            "child_class", pid, cid, 0, True, start_int, end_int)
        for i in result_gen:
            dayTime = str(i['dayTime'])
            for k, v in sum_total.items():
                check = i.get(k)
                if check:
                    v["list"][dayTime] = i[k]

        # 赋值sum数据
        for k, v in sum_total.items():
            k_sum = 0
            for kk, vv in v["list"].items():
                k_sum = round(k_sum + vv, 2)
            sum_total[k]["sum"] = k_sum

        # 根据赋值重构
        for k, v in sum_total.items():
            k_list = []
            for kk, vv in v["list"].items():
                k_list.append(vv)

            sum_total[k]['list'] = k_list

        # 领域建立数据结构
        for i in advert_list + task_list:
            cate_total[i] = {}
            for f in fids_list:
                cate_total[i][f] = 0

        # 查询并赋值
        result_gen = filter_result(
            "child_class", pid, cid, -1, False, start_int, end_int)
        for i in result_gen:
            for k, v in cate_total.items():
                single_cid = str(i['fid'])
                check = v.get(single_cid)
                if check is not None:
                    v[single_cid] = round(check + i.get(k, 0), 2)

        # 所有行业建立数据结构
        for i in advert_list + task_list:
            indus_total[i] = {}
            for c in cids_list:
                indus_total[i][c] = 0

        # 查询并赋值
        result_gen = filter_result(
            "child_class", -1, -1, 0, False, start_int, end_int)
        for i in result_gen:
            for k, v in indus_total.items():
                single_cid = str(i['cid'])
                check = v.get(single_cid)
                if check is not None:
                    v[single_cid] = round(check + i.get(k, 0), 2)

        return_dict = {
            "daysList": days_list, "sumTotal": sum_total,
            "cateTotal": cate_total, "indusTotal": indus_total,
        }
        return jsonify({"status": "ok", "message": "", "data": return_dict})
    except Exception as ex:
        logger.info("数据库问题")
        logger.info(ex)
        return jsonify({"status": "error", "message": "连接超时", "data": {}})


class Industry(Resource):
    def get(self):
        return get_industry()


api.add_resource(Industry, '/api/industry')


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=18082)
