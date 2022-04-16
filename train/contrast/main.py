#! /usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
    written by pyleo
"""
import sys
sys.path.append('..')  # 导入环境当前目录
from flask import Flask, render_template
from contrast.compare import Compare
from flask_bootstrap import Bootstrap
import pymongo
import logging

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False                                         # 格式化字符
Bootstrap(app)

# # # 日志标准输出
logger = logging.getLogger("flask")
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter('【%(asctime)s】%(message)s')
handler = logging.FileHandler("monitor.log")                                # 日志存放地址
# handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
app.logger.addHandler(handler)
mongo_client = pymongo.MongoClient(
    "mongodb://101.236.17.132:27017/", serverSelectionTimeoutMS=5)           # mongo数据库连接


@app.route('/')
def index():
    """
    主页,用来对比链接
    :return: None
    """
    compare = Compare()                                 # 声明类
    compare.mongo_client = mongo_client                 # 数据链接赋值
    compare.logger = app.logger                         # 日志赋值
    compare.compare_url()                               # 调用函数
    return render_template('home.html', title_name="Home", url_more=compare.url_more,
                           url_less=compare.url_less, new_time=compare.new_time, old_time=compare.old_time)


@app.route('/detail')
def detail():
    """
    细节页,用来对比参数
    :return: None
    """
    compare = Compare()
    compare.mongo_client = mongo_client
    compare.logger = app.logger
    compare.compare_args()
    return render_template('detail.html', title_name="Detail", all_content=compare.final_args,
                           new_time=compare.new_time, old_time=compare.old_time)


@app.route('/content')
def content():
    """
    内容页,用来对比内容
    :return: None
    """
    compare = Compare()
    compare.mongo_client = mongo_client
    compare.logger = app.logger
    compare.compare_content()
    return render_template('content.html', title_name="Content", all_url=compare.content_url,
                           new_time=compare.new_time, old_time=compare.old_time)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
