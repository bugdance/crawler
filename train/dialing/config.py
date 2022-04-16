#! /usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
    written by pyleo
"""
# # # 接口程序配置
SOCKET_TIMEOUT = 30                     # 全局socket超时设置

QUEUE_HOST = "101.236.21.223"           # redis队列地址
QUEUE_PORT = 36379                      # redis队列端口
QUEUE_PASS = "gogo2019redis"            # redis队列密码

RESULT_HOST = "101.236.51.179"          # redis结果地址
RESULT_PORT = 36379                     # redis结果端口
RESULT_PASS = "gogo2019redis"           # redis结果密码

MACHINE_HOST = "101.236.57.75"          # redis机器地址
MACHINE_PORT = 36379                    # redis机器端口
MACHINE_PASS = "gogo2019redis"          # redis机器密码

MACHINE_QUEUE = "machine_leisure"       # 机器队列名称
PROXY_CHECK = "proxy_check"             # 代理队列检查是否可用名称
PROXY_LEISURE = "proxy_leisure"         # 代理队列空闲可用名称
PROXY_DIALING = "proxy_dialing"         # 代理队列需要拨号名称
REDIS_TIMEOUT = 5                       # redis超时时间

CHECK_THREAD = 10                       # 代理检查线程数
DIALING_THREAD = 10                     # 代理拨号线程数
GET_THREAD = 10                         # 代理上线到队列服务线程数

