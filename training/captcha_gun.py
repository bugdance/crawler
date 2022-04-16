#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""Gunicorn.

written by pyLeo.
"""
# # # linux使用，独角兽配置不要和程序配置相混。
from gevent import monkey

monkey.patch_all()
# # # Import current path.
import sys

sys.path.append('..')
import multiprocessing

# # # 具体参数。
bind = '0.0.0.0:18080'
debug = False
worker_class = 'gevent'
workers = multiprocessing.cpu_count() * 2 + 1
worker_connections = 1000
threads = 100
backlog = 2048
proc_name = 'gunicorn.proc'
errorlog = 'gunicorn.log'
