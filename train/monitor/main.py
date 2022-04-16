#! /usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
    written by pyleo
"""
import sys
sys.path.append('..')  # 导入环境当前目录
from monitor import config
from flask import Flask, render_template
from monitor.query import Query
from flask_bootstrap import Bootstrap
import pymongo
import logging
import redis


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 字符
Bootstrap(app)

# # # 日志格式化
logger = logging.getLogger("flask")
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter('【%(asctime)s】%(message)s')
handler = logging.FileHandler("monitor.log")  # 日志存放地址
# handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
app.logger.addHandler(handler)
mongo_client = pymongo.MongoClient("mongodb://172.16.188.42:27017/")  # mongo统计
redis_queue = redis.StrictRedis(
    connection_pool=redis.ConnectionPool(
        host=config.QUEUE_HOST, port=config.QUEUE_PORT, password=config.QUEUE_PASS,
        decode_responses=True, socket_connect_timeout=config.REDIS_TIMEOUT, socket_timeout=config.REDIS_TIMEOUT))  # redis队列


@app.route('/')
def index():
    query = Query()
    query.mongo_client = mongo_client
    query.redis_queue = redis_queue
    query.logger = app.logger
    query.main()
    return render_template('home.html', sum_count=query.sum_count, tickets_count=query.tickets_count, success_count=query.success_count,
                           failure_count=query.failure_count, tickets_rate=query.tickets_rate, success_rate=query.success_rate,
                           failure_rate=query.failure_rate, is_more=query.is_more, average_time=query.average_time,
                           none_count=query.none_count, none_rate=query.none_rate, wait_count=query.wait_count, wait_rate=query.wait_rate,
                           verification_count=query.verification_count, verification_rate=query.verification_rate,
                           conflict_count=query.conflict_count, conflict_rate=query.conflict_rate, restrict_count=query.restrict_count,
                           restrict_rate=query.restrict_rate, init_count=query.init_count, init_rate=query.init_rate,
                           comparison_count=query.comparison_count, comparison_rate=query.comparison_rate, timeout_count=query.timeout_count,
                           timeout_rate=query.timeout_rate, all_times=query.all_times, all_sum=query.all_sum, all_tickets=query.all_tickets,
                           all_rate=query.all_rate, machine_count=query.machines, proxy_count=query.proxies)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=False)
