#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> mcn api
@@..> package services
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> import current path
import sys
sys.path.append('..')
# @@..> base import
from concurrent.futures import ThreadPoolExecutor
# from werkzeug.middleware.proxy_fix import ProxyFix
from flask import request, jsonify
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
from flask_compress import Compress
# @@..> import utils
from utils.base_tools import BaseAct, LogAct
from utils.num_tools import TimeAct
from utils.pool_tools import PoolAct
from utils.json_tools import JsonAct
from utils.str_tools import StrAct


logger, handler = LogAct.init_log("mcn_api.log", False)
# logger, handler = LogAct.init_log("mcn_api.log")
TimeAct.logger = logger
StrAct.logger = logger
JsonAct.logger = logger
pool = PoolAct()
pool.logger = logger
pool.init_app()
# define app outside gun
app = pool.app
# source_db = pool.init_mongo("mongodb://127.0.0.1:27017/source")
source_db = pool.init_mongo("mongodb://mongodb:27017/source")
CORS(app, supports_credentials=True)
Compress(app)
api = Api(app)


class PushMcn(Resource):
    def post(self) -> dict:
        """ [post method]

        Returns:
            dict: [{"status": 1}]
        """
        executor = ThreadPoolExecutor(1)
        executor.submit(self.make_api, request.data)
        return jsonify({"status": 1})

    def make_api(self, source_data: bytes = b"") -> None:
        """ [main process]

        Args:
            source_data (bytes, optional): [gzip data]. Defaults to b"".

        Returns:
            None: [None]
        """
        source_data = StrAct.parse_gzip(source_data)
        get_dict = JsonAct.format_json(source_data)
        try:
            # parse data
            taskId = get_dict['_id']
            envMap = get_dict['envMap']
            toolType = get_dict['toolType']
            flowType = get_dict['flowType']
            isUrls = get_dict['isUrls']
            isLast = get_dict['isLast']
            isUse = get_dict['isUse']
            platId = get_dict['platId']
            homeUrl = get_dict['homeUrl']
            scrapeUrl = get_dict['scrapeUrl']
            updateDate = get_dict['updateDate']
            profileBase = get_dict['profileBase']
            profileCounts = get_dict['profileCounts']
            workBase = get_dict['workBase']
            workList = get_dict['workList']
            workUrls = get_dict['workUrls']
#######################################################################################
            # @@..! if certify type
            if toolType == 1:
                if flowType == 1:
                    if profileCounts:
                        pool.update_mongo(
                            source_db, 'certify', {'_id': taskId},
                            {'$set': {"profileCounts": profileCounts,
                                      "status": 1, 'isScrape': 1}},
                            True
                        )
                    else:
                        pool.update_mongo(
                            source_db, 'certify', {'_id': taskId},
                            {'$set': {"profileCounts": {},
                                      "status": 0, 'isScrape': 1}},
                            True
                        )
                elif flowType == 2:
                    if workBase:
                        pool.update_mongo(
                            source_db, 'work', {'_id': taskId},
                            {'$set': {"workBase": workBase,
                                      "status": 1, 'isScrape': 1}},
                            True
                        )
                    else:
                        pool.update_mongo(
                            source_db, 'work', {'_id': taskId},
                            {'$set': {"workBase": {}, "status": 0, 'isScrape': 1}},
                            True
                        )
#######################################################################################
            # @@..! if quick type
            elif toolType == 2:
                if flowType == 1:
                    # @@..! db.quick.ensureIndex({"envId":1,"syncName":1,"isScrape":1})
                    if not isUse or (profileBase and profileCounts):
                        pool.update_mongo(
                            source_db, 'quick', {'_id': taskId},
                            {'$set': {"profileBase": profileBase,
                                      "profileCounts": profileCounts,
                                      "workUrls": workUrls, "workList": workList,
                                      "isUrls": isUrls, "isLast": isLast,
                                      "isUse": isUse, "isScrape": 1}},
                            True
                        )
                elif flowType == 2:
                    if workBase:
                        pool.update_mongo(
                            source_db, 'quick', {'_id': taskId},
                            {"$set": {"isLast": isLast},
                             '$addToSet': {"workList": workBase}},
                            True
                        )
#######################################################################################
            # @@..! if account type, don't have flow type 2
            elif toolType == 3:
                if flowType == 1:
                    # @@..! db.update.ensureIndex({"envMap.name":1,"envMap.id":1})
                    # @@..! db.update.ensureIndex({"platId":1,"isUse":1,"isLast":1})
                    if not isUse or (profileBase and profileCounts):
                        pool.update_mongo(
                            source_db, 'update', {'_id': taskId},
                            {'$set': {
                                "envMap": envMap, "platId": platId,
                                "homeUrl": homeUrl, "scrapeUrl": scrapeUrl,
                                "updateDate": updateDate, "profileBase": profileBase,
                                "profileCounts": profileCounts,
                                "workUrls": workUrls, "workList": workList,
                                "isUse": isUse, "isUrls": isUrls, "isLast": isLast}},
                            True
                        )
                        pool.update_mongo(
                            source_db, 'account', {'_id': taskId},
                            {'$set': {'isScrape': 1}}
                        )
#######################################################################################
            # @@..! if update type
            elif toolType == 4:
                if flowType == 1:
                    # @@..! 覆盖
                    if not isUse or (profileBase and profileCounts):
                        pool.update_mongo(
                            source_db, 'update', {'_id': taskId},
                            {'$set': {
                                "envMap": envMap, "platId": platId,
                                "homeUrl": homeUrl, "scrapeUrl": scrapeUrl,
                                "updateDate": updateDate,
                                "profileBase": profileBase,
                                "profileCounts": profileCounts,
                                "workUrls": workUrls, "workList": workList,
                                "isUse": isUse, "isUrls": isUrls, "isLast": isLast}}
                        )
                elif flowType == 2:
                    if workBase:
                        pool.update_mongo(
                            source_db, 'update', {'_id': taskId},
                            {"$set": {"isLast": isLast},
                             '$addToSet': {"workList": workBase}}
                        )
        except Exception as ex:
            logger.info(f"入库data数据失败(*>﹏<*)【{ex}】")


api.add_resource(PushMcn, '/api/receiver/')


account_parser = reqparse.RequestParser()
account_parser.add_argument('id', type=int, required=True, location='args')


#######################################################################################
def get_detail(sync_identity):
    # @@..! db.result.ensureIndex({"envMap.name":1,"envMap.id":1})
    # @@..! db.result.ensureIndex({"plantId":1, "status": 1, "dataLevel": 1})
    req = account_parser.parse_args(strict=True)
    get_id = req.get("id")
    result_gen = pool.query_mongo(
        source_db, "result",
        {"envName": sync_identity, "id": get_id},
        {"_id": 0}, []
    )
    return_dict, result_gen = BaseAct.parse_generator(result_gen)
    if return_dict:
        return jsonify({"status": "ok", "message": "", "data": return_dict})
    else:
        return jsonify({"status": "error", "message": "查无此信息", "data": {}})


class ApiDetail(Resource):
    def get(self):
        return get_detail("api")


class PreDetail(Resource):
    def get(self):
        return get_detail("preapi")


class TestDetail(Resource):
    def get(self):
        return get_detail("tapi")


class DevDetail(Resource):
    def get(self):
        return get_detail("dapi")


api.add_resource(ApiDetail, '/api/api/detail')
api.add_resource(PreDetail, '/preapi/api/detail')
api.add_resource(TestDetail, '/tapi/api/detail')
api.add_resource(DevDetail, '/dapi/api/detail')


list_parser = reqparse.RequestParser()
list_parser.add_argument('startId', type=int, required=True, location='args')
list_parser.add_argument('limit', type=int, required=True, location='args')


#######################################################################################
def get_list(sync_identity):

    # req_ip = request.headers['X-Forwarded-For']
    req = list_parser.parse_args(strict=True)
    start_id = req.get("startId")
    limit = req.get("limit")
    try:
        return_list = []
        result_gen = pool.query_mongo(
            source_db, "result",
            {"envName": sync_identity, "id": {"$gt": start_id}},
            {"_id": 0, "id": 1, "plantId": 1,
             "accountId": 1, "nickname": 1, "avatar": 1,
             "gender": 1, "age": 1, "area": 1, "desc": 1,
             "isAuth": 1, "isMember": 1, "worksNum": 1,
             "followNum": 1, "fansNum": 1, "blogs": 1, "videos": 1,
             "expectPlayNum": 1, "expectCommentNum": 1, 
             "expectPraiseNum": 1, "expectShareNum": 1,
             "expectForwardNum": 1,
             "dataLevel": 1, "status": 1,
             "video20": 1, "video60": 1
             }, [], 0, limit
        )
        for i in result_gen:
            plantId = i.get("plantId", 0)
            result_dict = {
                "id": i.get("id", 0), "plantId": plantId,
                "accountId": i.get("accountId", ""),
                "nickname": i.get("nickname", ""),
                "avatar": i.get("avatar", ""), "gender": i.get("gender", 0),
                "age": i.get("age", 0), "area": i.get("area", ""),
                "desc": i.get("desc", ""), "followNum": i.get("followNum", 0),
                "fansNum": i.get("fansNum", 0), "isAuth": i.get("isAuth", 0),
                "isMember": i.get("isMember", 0), "blogs": i.get("blogs", 0),
                "videos": i.get("videos", 0), "status": i.get("status", 1),
                "dataLevel": i.get("dataLevel", 0),
                "expectPlayNum": i.get("expectPlayNum", 0),
                "expectCommentNum": i.get("expectCommentNum", 0),
                "expectPraiseNum": i.get("expectPraiseNum", 0),
                "expectShareNum": i.get("expectShareNum", 0),
                "expectForwardNum": i.get("expectForwardNum", 0)
            }
            # # douyin update price
            if plantId == 1:
                price = {}
                video20 = i.get("video20")
                video60 = i.get("video60")
                if video20:
                    price["video20"] = video20
                if video60:
                    price["video60"] = video60
                result_dict.update(price)
            # take
            return_list.append(result_dict)

        return jsonify({"error_code": 0, "message": "",
                        "total": 0, "data": return_list})
    except Exception as ex:
        logger.info(f"出库account数据失败(*>﹏<*)【{ex}】")
        return jsonify({"error_code": 1, "message": "连接超时",
                        "total": 0, "data": []})


class ApiList(Resource):
    def get(self):
        return get_list("api")


class PreList(Resource):
    def get(self):
        return get_list("preapi")


class TestList(Resource):
    def get(self):
        return get_list("tapi")


class DevList(Resource):
    def get(self):
        return get_list("dapi")


api.add_resource(ApiList, '/api/api/account-list')
api.add_resource(PreList, '/preapi/api/account-list')
api.add_resource(TestList, '/tapi/api/account-list')
api.add_resource(DevList, '/dapi/api/account-list')


certify_parser = reqparse.RequestParser()
certify_parser.add_argument('ids', type=str, required=True, location='json')


#######################################################################################
def get_certify(sync_identity):
    # get ids
    req = certify_parser.parse_args(strict=True)
    ids = req.get("ids")
    return_list = []
    ids = ids.split(",")
    ids = [int(i) for i in ids]
    result_gen = pool.query_mongo(
        source_db, "certify",
        {"syncName": sync_identity, "isScrape": 1, "envId": {"$in": ids}},
        {"_id": 0, "id": "$envId", "fansNum": "$profileCounts.fansNum",
         "status": "$status"}, []
    )
    # take data and return
    for i in result_gen:
        return_list.append(i)
    return jsonify({"error_code": 0, "message": "", "data": return_list})


class ApiCertify(Resource):
    def post(self):
        return get_certify("api")


class PreCertify(Resource):
    def post(self):
        return get_certify("preapi")


class TestCertify(Resource):
    def post(self):
        return get_certify("tapi")


class DevCertify(Resource):
    def post(self):
        return get_certify("dapi")


#######################################################################################
def get_quick(sync_identity):
    # get ids
    req = certify_parser.parse_args(strict=True)
    ids = req.get("ids")
    return_dict = {}
    ids = ids.split(",")
    ids = [int(i) for i in ids]

    result_gen = pool.query_mongo(
        source_db, "quick",
        {"syncName": sync_identity, "isLast": 1, "envId": {"$in": ids}},
        {"_id": 0, "id": "$envId", "plantId": "$platId",
         "nickname": "$profileBase.nickname", "accountId": "$profileBase.accountId",
         "fansNum": "$profileCounts.fansNum", "likeNum": "$profileCounts.likeNum",
         "worksNum": "$profileBase.worksNum", "avgComment": "$commentAvg",
         "avgLike": "$likeAvg", "avgForward": "$forwardAvg",
         "avgShare": "$shareAvg", "humanRatio": 1,
         "ageRange": 1, "areaTop": 1, "status": 1},
        []
    )
    # take data and return
    for i in result_gen:
        unique_id = i.get("id")
        status = i.get("status")
        if status is not None:
            # @@..! if status then update
            return_dict[unique_id] = i
    return jsonify({"error_code": 0, "message": "", "data": return_dict})


class ApiQuick(Resource):
    def post(self):
        return get_quick("api")


class PreQuick(Resource):
    def post(self):
        return get_quick("preapi")


class TestQuick(Resource):
    def post(self):
        return get_quick("tapi")


class DevQuick(Resource):
    def post(self):
        return get_quick("dapi")


#######################################################################################
def get_work(sync_identity):
    # get ids
    req = certify_parser.parse_args(strict=True)
    ids = req.get("ids")
    return_dict = {}
    ids = ids.split(",")
    ids = [int(i) for i in ids]

    result_gen = pool.query_mongo(
        source_db, "work",
        {"syncName": sync_identity, "isScrape": 1, "envId": {"$in": ids}},
        {"_id": 0, "id": "$envId", "plantId": "$platId",
         "url": "$workBase.url", "title": "$workBase.title",
         "likeNum": "$workBase.likeNum", "commentNum": "$workBase.commentNum",
         "shareNum": "$workBase.shareNum", "forwardNum": "$workBase.forwardNum",
         "collectNum": "$workBase.collectNum", "playNum": "$workBase.playNum",
         "viewNum": "$workBase.viewNum",
         "rewardNum": "$workBase.rewardNum", "danmakuNum": "$workBase.danmakuNum", 
         "status": "$status"}, []
    )
    # take data and return
    for i in result_gen:
        unique_id = i.get("id")
        if unique_id:
            return_dict[unique_id] = i
    return jsonify({"error_code": 0, "message": "", "data": return_dict})


class ApiWork(Resource):
    def post(self):
        return get_work("api")


class PreWork(Resource):
    def post(self):
        return get_work("preapi")


class TestWork(Resource):
    def post(self):
        return get_work("tapi")


class DevWork(Resource):
    def post(self):
        return get_work("dapi")


api.add_resource(ApiCertify, '/api/api/certify-list')
api.add_resource(PreCertify, '/preapi/api/certify-list')
api.add_resource(TestCertify, '/tapi/api/certify-list')
api.add_resource(DevCertify, '/dapi/api/certify-list')

api.add_resource(ApiQuick, '/api/api/tool-list')
api.add_resource(PreQuick, '/preapi/api/tool-list')
api.add_resource(TestQuick, '/tapi/api/tool-list')
api.add_resource(DevQuick, '/dapi/api/tool-list')

api.add_resource(ApiWork, '/api/api/work-list')
api.add_resource(PreWork, '/preapi/api/work-list')
api.add_resource(TestWork, '/tapi/api/work-list')
api.add_resource(DevWork, '/dapi/api/work-list')


# class PushCookie(Resource):
#     def post(self) -> dict:
#         """ [post method]

#         Returns:
#             dict: [{"status": 1}]
#         """
#         executor = ThreadPoolExecutor(1)
#         executor.submit(self.make_api, request.data)
#         return jsonify({"status": 1})

#     def make_api(self, source_data: bytes = b"") -> None:
#         """ [main process]

#         Args:
#             source_data (bytes, optional): [gzip data]. Defaults to b"".

#         Returns:
#             None: [None]
#         """
#         source_data = StrAct.parse_gzip(source_data)
#         get_dict = JsonAct.format_json(source_data)
#         updateTime = get_dict.get("updateTime")
#         if updateTime:
#             pool.update_mongo(
#                 source_db, 'mcn_cookie', {'_id': updateTime},
#                 {'$set': get_dict}, True
#             )
#         else:
#             logger.info(f"入库cookie数据失败(*>﹏<*)【{updateTime}】")


# class PullCookie(Resource):
#     def get(self) -> dict:
#         """ [post method]

#         Returns:
#             dict: [{"status": 1}]
#         """
#         return self.make_api()

#     def make_api(self) -> dict:
#         """ [main process]

#         Args:
#             source_data (bytes, optional): [gzip data]. Defaults to b"".

#         Returns:
#             None: [None]
#         """
#         now = TimeAct.format_now()
#         last_tow = TimeAct.parse_custom(now, hours=-24)
#         now = TimeAct.parse_datetime(now)
#         last_tow = TimeAct.parse_datetime(last_tow)
#         result_gen = pool.aggregate_mongo(
#             source_db, "mcn_cookie",
#             [{"$match": {"updateTime": {"$gt": last_tow, "$lt": now}}},
#              {"$project": {"timestamp2": 1}},
#              {"$sample": {"size": 1}}]
#         )
#         result_dict, result_gen = BaseAct.parse_generator(result_gen)
#         if result_dict:
#             return jsonify(result_dict)
#         else:
#             logger.info(f"出库cookie数据失败(*>﹏<*)【{result_dict}】")
#             return jsonify({"status": 1})

# api.add_resource(PushCookie, '/api/cookie/')
# api.add_resource(PullCookie, '/api/api/device/')




if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=18081)
