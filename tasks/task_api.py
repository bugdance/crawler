#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> task api
@@..> package tasks
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> import current path
import sys
sys.path.append('..')
# @@..> base import
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS
from flask_compress import Compress
# @@..> import utils
from utils.base_tools import LogAct
from utils.num_tools import TimeAct
from utils.net_tools import NetAct
from utils.str_tools import StrAct
from utils.json_tools import JsonAct
# @@..> import rulers
from rules.persdy_ruler import PersDYWorker
from rules.persks_ruler import PersKSWorker
from rules.persbl_ruler import PersBLWorker
from rules.pershs_ruler import PersHSWorker
from rules.perswb_ruler import PersWBWorker
from rules.perswx_ruler import PersWXWorker
from rules.perszh_ruler import PersZHWorker
from rules.perstt_ruler import PersTTWorker


logger, handler = LogAct.init_log("task_api.log", False)
# logger, handler = LogAct.init_log("task_api.log")
app = Flask(__name__)
CORS(app, supports_credentials=True)
Compress(app)
api = Api(app)


class TaskApi(Resource):
    """
    [Restful define]
    """
    def post(self) -> None:
        """
        [post method]

        Returns:
            dict: [{"status": 1}]
        """
        executor = ThreadPoolExecutor(1)
        executor.submit(self.make_api, request.data)
        return jsonify({"status": 1})

    def make_api(self, source_data: bytes = b"") -> None:
        """
        [main process]

        Args:
            source_data (bytes, optional): [gzip data]. Defaults to b"".

        Returns:
            None: [None]
        """
        net = NetAct()
        net.logger = logger
        TimeAct.logger = logger
        JsonAct.logger = logger
        StrAct.logger = logger

        start_time = TimeAct.format_timestamp()
        source_data = StrAct.parse_gzip(source_data)
        get_dict = JsonAct.format_json(source_data)
        try:
            task_id = get_dict['_id']
            plant_identity = get_dict["platIdentity"]
            account_identity = get_dict["accountIdentity"]
            # # # define class
            create_var = globals()
            worker = create_var[
                account_identity.capitalize() + plant_identity.upper() + "Worker"]()
            result_data = worker.process_main(get_dict)
            if result_data:
                net.set_session()
                header_version, user_agent, init_header = net.set_header("flask")
                net.timeout = 10
                net.url = "http://api.lolqq.xyz/receiver/"
                # net.url = "http://127.0.0.1:18081/api/receiver/"
                net.headers = init_header
                result_data = JsonAct.format_string(result_data)
                net.posts = StrAct.format_gzip(result_data)
                net.get_response("post", "data")
                if net.get_page("json", is_log=False):
                    end_time = (TimeAct.format_timestamp() - start_time)
                    msg = f"【{plant_identity}请求成功】" \
                          f"【{task_id}】【{end_time}】"
                    logger.info(msg)
                else:
                    end_time = (TimeAct.format_timestamp() - start_time)
                    msg = f"【{plant_identity}传输失败】" \
                          f"【{task_id}】【{end_time}】"
                    logger.info(msg)
            else:
                end_time = (TimeAct.format_timestamp() - start_time)
                msg = f"【{plant_identity}请求失败】" \
                      f"【{task_id}】【{end_time}】"
                logger.info(msg)

        except Exception as ex:
            logger.info(f"接口本地未知错误【{ex}】")
            logger.info(f"{get_dict}")


api.add_resource(TaskApi, '/api/worker/')


if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=18082, threaded=True)
