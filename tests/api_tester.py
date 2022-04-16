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
app = pool.app

CORS(app, supports_credentials=True)
Compress(app)
api = Api(app)


parser = reqparse.RequestParser()
parser.add_argument('startId', type=int, required=True, location='args')
parser.add_argument('limit', type=int, required=True, location='args')


# 抖音筛选星图
class GetAccount(Resource):
    def get(self) -> dict:
        """ [post method]

        Returns:
            dict: [{"status": 1}]
        """
        
        req = parser.parse_args(strict=True)
        get_id = req.get("startId")
        
        if get_id > 5:
            return_dict = {
                "status":"ok","message":"","code":0,
                "data":{
                    "list":[],
                "total":"12"
                },
            }
            return jsonify(return_dict)
        
        return_dict = {
            "status":"ok","message":"","code":0,
            "data":{
                "list":[
                    {"id":"2","url":"https://v.douyin.com/JaaUvg4/","plantId":"1","nickname":"","accountId":""},
                    {"id":"3","url":"https://v.douyin.com/JaapprU/","plantId":"1","nickname":"","accountId":""},
                    {"id":"4","url":"https://v.douyin.com/cbdFNN/","plantId":"1","nickname":"","accountId":""},
                    {"id":"5","url":"https://v.douyin.com/cbJfRN/","plantId":"1","nickname":"","accountId":""},
                    {"id":"6","url":"https://v.douyin.com/cqK8a4/","plantId":"1","nickname":"","accountId":""},
                    
                    {"id":"12","url":"https://space.bilibili.com/377920013","plantId":"3","nickname":"","accountId":""},
                    {"id":"13","url":"https://space.bilibili.com/43636152/#/","plantId":"3","nickname":"","accountId":""},
                    {"id":"14","url":"https://space.bilibili.com/3647169","plantId":"3","nickname":"","accountId":""},
                    {"id":"15","url":"https://space.bilibili.com/193482959","plantId":"3","nickname":"","accountId":""},
                    {"id":"16","url":"https://space.bilibili.com/95411213","plantId":"3","nickname":"","accountId":""},
                    ],
            "total":"12"
            },
        }
        
        return jsonify(return_dict)


api.add_resource(GetAccount, '/api/get/account')


# 抖音筛选星图
class GetCertify(Resource):
    def get(self) -> dict:
        """ [post method]

        Returns:
            dict: [{"status": 1}]
        """
        req = parser.parse_args(strict=True)
        get_id = req.get("startId")
        
        if get_id > 5:
            return_dict = {
                "status":"ok","message":"","code":0,
                "data":{
                    "list":[],
                "total":"12"
                },
            }
            return jsonify(return_dict)
        
        return_dict = {
            "status":"ok","message":"","code":0,
            "data":{
                "list":[
                    {"id":"2","url":"https://v.douyin.com/JaaUvg4/","plantId":"1","nickname":"","accountId":""},
                    {"id":"3","url":"https://v.douyin.com/JaapprU/","plantId":"1","nickname":"","accountId":""},
                    {"id":"4","url":"https://v.douyin.com/cbdFNN/","plantId":"1","nickname":"","accountId":""},
                    {"id":"5","url":"https://v.douyin.com/cbJfRN/","plantId":"1","nickname":"","accountId":""},
                    {"id":"6","url":"https://v.douyin.com/cqK8a4/","plantId":"1","nickname":"","accountId":""},
                    
                    {"id":"12","url":"https://space.bilibili.com/377920013","plantId":"3","nickname":"","accountId":""},
                    {"id":"13","url":"https://space.bilibili.com/43636152/#/","plantId":"3","nickname":"","accountId":""},
                    {"id":"14","url":"https://space.bilibili.com/3647169","plantId":"3","nickname":"","accountId":""},
                    {"id":"15","url":"https://space.bilibili.com/193482959","plantId":"3","nickname":"","accountId":""},
                    {"id":"16","url":"https://space.bilibili.com/95411213","plantId":"3","nickname":"","accountId":""},
                    ],
            "total":"12"
            },
        }
        
        return jsonify(return_dict)


api.add_resource(GetCertify, '/api/get/certify')

# 抖音筛选星图
class GetQuick(Resource):
    def get(self) -> dict:
        """ [post method]

        Returns:
            dict: [{"status": 1}]
        """
        req = parser.parse_args(strict=True)
        get_id = req.get("startId")
        
        if get_id > 5:
            return_dict = {
                "status":"ok","message":"","code":0,
                "data":{
                    "list":[],
                "total":"12"
                },
            }
            return jsonify(return_dict)
        
        return_dict = {
            "status":"ok","message":"","code":0,
            "data":{
                "list":[
                    {"id":"2","url":"https://v.douyin.com/JaaUvg4/","plantId":"1","nickname":"","accountId":""},
                    {"id":"3","url":"https://v.douyin.com/JaapprU/","plantId":"1","nickname":"","accountId":""},
                    {"id":"4","url":"https://v.douyin.com/cbdFNN/","plantId":"1","nickname":"","accountId":""},
                    {"id":"5","url":"https://v.douyin.com/cbJfRN/","plantId":"1","nickname":"","accountId":""},
                    {"id":"6","url":"https://v.douyin.com/cqK8a4/","plantId":"1","nickname":"","accountId":""},
                    
                    {"id":"12","url":"https://space.bilibili.com/377920013","plantId":"3","nickname":"","accountId":""},
                    {"id":"13","url":"https://space.bilibili.com/43636152/#/","plantId":"3","nickname":"","accountId":""},
                    {"id":"14","url":"https://space.bilibili.com/3647169","plantId":"3","nickname":"","accountId":""},
                    {"id":"15","url":"https://space.bilibili.com/193482959","plantId":"3","nickname":"","accountId":""},
                    {"id":"16","url":"https://space.bilibili.com/95411213","plantId":"3","nickname":"","accountId":""},
                    ],
            "total":"12"
            },
        }
        
        return jsonify(return_dict)


api.add_resource(GetQuick, '/api/get/quick')


# 抖音筛选星图
class GetWork(Resource):
    def get(self) -> dict:
        """ [post method]

        Returns:
            dict: [{"status": 1}]
        """
        req = parser.parse_args(strict=True)
        get_id = req.get("startId")
        
        if get_id > 5:
            return_dict = {
                "status":"ok","message":"","code":0,
                "data":{
                    "list":[],
                "total":"12"
                },
            }
            return jsonify(return_dict)
        
        return_dict = {
            "status":"ok","message":"","code":0,
            "data":{
                "list":[
                    {"id":"2","url":"https://www.douyin.com/video/6984725099660315917?previous_page=main_page","plantId":"1","nickname":"","accountId":""},
                    {"id":"3","url":"https://www.douyin.com/video/6984741847264480525?previous_page=video_detail","plantId":"1","nickname":"","accountId":""},
                    {"id":"4","url":"https://www.douyin.com/video/6983634629420944651?pre_vid=6984741847264480525&previous_page=video_detail","plantId":"1","nickname":"","accountId":""},
                    {"id":"5","url":"https://www.douyin.com/video/6988383393910115592?previous_page=video_detail","plantId":"1","nickname":"","accountId":""},
                    {"id":"6","url":"https://v.douyin.com/cqK8a4/","plantId":"1","nickname":"","accountId":""},
                    
                    {"id":"12","url":"https://www.bilibili.com/video/BV14t41117PP","plantId":"3","nickname":"","accountId":""},
                    {"id":"13","url":"https://www.bilibili.com/video/BV1YV41147Px/?spm_id_from=333.788.recommend_more_video.-1","plantId":"3","nickname":"","accountId":""},
                    {"id":"14","url":"https://www.bilibili.com/video/BV1eg411G78U/?spm_id_from=333.788.recommend_more_video.0","plantId":"3","nickname":"","accountId":""},
                    {"id":"15","url":"https://space.bilibili.com/193482959","plantId":"3","nickname":"","accountId":""},
                    {"id":"16","url":"https://www.bilibili.com/video/BV1254y1G7oV/?spm_id_from=333.788.recommend_more_video.5","plantId":"3","nickname":"","accountId":""},
                    ],
            "total":"12"
            },
        }
        
        return jsonify(return_dict)


api.add_resource(GetWork, '/api/get/work')


if __name__ == "__main__":
 
    app.run(debug=False, host='0.0.0.0', port=8888)
