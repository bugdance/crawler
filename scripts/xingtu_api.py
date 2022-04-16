#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> xingtu api
@@..> package scripts
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> import current path
import sys
sys.path.append('..')
# @@..> base import
# from concurrent.futures import ThreadPoolExecutor
from flask import jsonify
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
from flask_compress import Compress
# @@..> import utils
from utils.base_tools import LogAct
from utils.num_tools import TimeAct
from utils.pool_tools import PoolAct


# # # Logger
logger, handler = LogAct.init_log("xingtu_api.log")
TimeAct.logger = logger
pool = PoolAct()
pool.logger = logger
pool.init_app()
xingtu = pool.init_mongo("mongodb://127.0.0.1:27017/xingtu")

CORS(pool.app, supports_credentials=True)
Compress(pool.app)
api = Api(pool.app)


parser = reqparse.RequestParser()
parser.add_argument('id', type=str, required=True, location='args')
parser.add_argument('author', type=str, required=False, location='args')


# 抖音筛选星图
class GetCheck(Resource):
    def get(self, check_skip, check_limit) -> dict:
        """ [post method]

        Returns:
            dict: [{"status": 1}]
        """
        return self.make_api(check_skip, check_limit)

    def make_api(self, check_skip, check_limit) -> dict:
        """ [main process]

        Args:
            source_data (bytes, optional): [gzip data]. Defaults to b"".

        Returns:
            None: [None]
        """
        try:
            result_gen = pool.query_mongo(
                xingtu, "account", {"isCheck": 0}, {"userId": 1}, [],
                int(check_skip), int(check_limit)
            )
            id_result = list(result_gen)
            if id_result:
                return jsonify(id_result)
            else:
                return jsonify({"status": 1})
        except Exception as ex:
            logger.info(ex)
            return jsonify({"status": 1})


class ReturnCheck(Resource):
    def get(self) -> dict:
        """ [post method]

        Returns:
            dict: [{"status": 1}]
        """
        return self.make_api()

    def make_api(self) -> dict:
        """ [main process]

        Args:
            source_data (bytes, optional): [gzip data]. Defaults to b"".

        Returns:
            None: [None]
        """
        req = parser.parse_args(strict=True)
        get_id = req.get("id")
        get_author = req.get("author")
        pool.update_mongo(
            xingtu, "account", {"_id": get_id},
            {"$set": {"isCheck": 1, "authorId": get_author}}
        )
        return jsonify({"status": 1})


# 抖音抓取星图
class GetScrape(Resource):
    def get(self, check_skip, check_limit) -> dict:
        """ [post method]

        Returns:
            dict: [{"status": 1}]
        """
        return self.make_api(check_skip, check_limit)

    def make_api(self, check_skip, check_limit) -> dict:
        """ [main process]

        Args:
            source_data (bytes, optional): [gzip data]. Defaults to b"".

        Returns:
            None: [None]
        """
        try:
            result_gen = pool.query_mongo(
                xingtu, "account",
                {"authorId": {"$exists": True, "$ne": ""}, "isScrape": 0},
                {"authorId": 1}, [],
                int(check_skip), int(check_limit)
            )
            id_result = list(result_gen)
            if id_result:
                return jsonify(id_result)
            else:
                return jsonify({"status": 1})
        except Exception as ex:
            msg = "读取缓存数据有问题"
            logger.info(msg)
            logger.info(ex)
            return jsonify({"status": 1})


class ReturnScrape(Resource):
    def get(self) -> dict:
        """ [post method]

        Returns:
            dict: [{"status": 1}]
        """
        return self.make_api()

    def make_api(self) -> dict:
        """ [main process]

        Args:
            source_data (bytes, optional): [gzip data]. Defaults to b"".

        Returns:
            None: [None]
        """
        req = parser.parse_args(strict=True)
        get_id = req.get("id")
        pool.update_mongo(
            xingtu, "account", {"_id": get_id},
            {"$set": {"isScrape": 1}}
        )
        return jsonify({"status": 1})


api.add_resource(GetCheck, '/api/get/check/<check_skip>/<check_limit>/')
api.add_resource(ReturnCheck, '/api/return/check')
api.add_resource(GetScrape, '/api/get/scrape/<check_skip>/<check_limit>/')
api.add_resource(ReturnScrape, '/api/return/scrape')


if __name__ == "__main__":

    pool.app.run(debug=False, host='0.0.0.0', port=18081)
