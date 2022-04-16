#! /usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
    written by pyleo
"""
# # # 接口程序配置
QUEUE_HOST = "101.236.21.223"        # redis队列地址
QUEUE_PORT = 36379                  # redis队列端口
QUEUE_PASS = "gogo2019redis"        # redis队列密码

RESULT_HOST = "101.236.51.179"       # redis结果地址
RESULT_PORT = 36379                 # redis结果端口
RESULT_PASS = "gogo2019redis"       # redis结果密码

MACHINE_HOST = "101.236.57.75"      # redis机器地址
MACHINE_PORT = 36379                # redis机器端口
MACHINE_PASS = "gogo2019redis"      # redis机器密码

MACHINE_QUEUE = "machines"          # 机器队列名称
REDIS_TIMEOUT = 5                   # redis超时时间

MAX_NUM = 600                       # 最大循环时间，单位秒


