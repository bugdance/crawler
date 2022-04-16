# -*- coding: utf-8 -*-
# =============================================================================
# Copyright (c) 2018-, pyLeo Developer. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================
"""The receiver is use for receive the data."""
# # # Import current path.
import sys

sys.path.append('..')
# # # Base package.
from flask import Flask, request, jsonify
import logging
from logging import handlers
import time
import configparser
# # # Packages.
from train.captcha_run import CaptchaRun


# # # App instances. App实例。
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
# # # 日志格式化。
app.logger = logging.getLogger('flask')
app.logger.setLevel(level=logging.INFO)
app.formatter = logging.Formatter('[%(asctime)s]%(message)s')
app.handler = handlers.TimedRotatingFileHandler(
	"captcha.log", when='h', backupCount=6, encoding='utf-8')
# app.handler = logging.StreamHandler()
app.handler.setFormatter(app.formatter)
app.logger.addHandler(app.handler)


# # # 接口请求地址，http://x.x.x.x:18088/captcha/ko/。
@app.route('/captcha/weiboyi/', methods=['POST'])
def captcha_training() -> str:
	# # # 开始计时，回调声明。
	start_time = time.time()
	# # # 解析数据并获取日志任务号。
	try:
		if not request.get_data():
			app.logger.info("没有请求数据")
			# return jsonify({"message": "没有请求数据"})
			return "没有请求数据"
		
		content = request.get_data()
		# app.logger.info(content)
		
		CR = CaptchaRun()
		pre_text = CR.captcha2text(content, 'model/')
		CR.tf.compat.v1.reset_default_graph()

		
		if not pre_text:
			app.logger.info("没有返回结果")
			# return jsonify({"message": "没有返回结果"})
			return "没有返回结果"
		
		end_time = time.time() - start_time
		
		app.logger.info(f"返回正常:{pre_text}, {end_time.__round__(2)}")
		# return jsonify({"result": pre_text[0]})
		return pre_text[0]
	except Exception as ex:
		app.logger.info(ex)
		# return jsonify({"message": "error"})
		return "error"



if __name__ == "__main__":
	app.run(debug=False, host='127.0.0.1', port=18082)
