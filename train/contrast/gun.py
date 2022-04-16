#! /usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
    written by pyleo
"""
# # # linux使用，独角兽配置不要和程序配置相混
from gevent import monkey
monkey.patch_all()
import sys
sys.path.append('..')  # 导入环境当前目录

bind = '0.0.0.0:80'  # 绑定地址
debug = False
workers = 2  # 进程数
threads = 100  # 线程数
worker_class = 'gevent'
backlog = 2048
proc_name = 'gunicorn.proc'
