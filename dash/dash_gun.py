#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> dash gun
@@..> package interface
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> import current path
import sys
sys.path.append('..')
# @@..! linux only patch
from gevent import monkey
monkey.patch_all()
# @@..> base import
import multiprocessing
#######################################################################################
# @@..> args
bind = '0.0.0.0:8000'
debug = False
worker_class = 'gevent'
workers = multiprocessing.cpu_count() * 2 + 1
worker_connections = 1000
threads = 100
backlog = 2048
proc_name = 'gunicorn.proc'
errorlog = 'gunicorn.log'
