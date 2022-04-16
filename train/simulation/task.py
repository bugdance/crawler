#! /usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
    written by pyleo
"""
import sys
sys.path.append('..')  # 导入环境当前目录
from simulation import config
from simulation.source.util import Base
from simulation.source.order import Order  # 下单
from simulation.source.pay import Pay  # 下单
from simulation.source.audit import Audit  # 下单
import logging
import time
import redis
import socket
socket.setdefaulttimeout(config.SOCKET_TIMEOUT)


class Task:
    """
    任务启动的方法类
    """
    def __init__(self):
        self.logger = logging.getLogger("simulation")  # 基础日志
        self.formatter = logging.Formatter('【%(asctime)s】%(message)s')  # 日志格式
        self.redis_queue = redis.StrictRedis(
            connection_pool=redis.ConnectionPool(
                host=config.QUEUE_HOST, port=config.QUEUE_PORT, password=config.QUEUE_PASS,
                decode_responses=True, socket_connect_timeout=config.REDIS_TIMEOUT, socket_timeout=config.REDIS_TIMEOUT))  # redis队列
        self.redis_result = redis.StrictRedis(
            connection_pool=redis.ConnectionPool(
                host=config.RESULT_HOST, port=config.RESULT_PORT, password=config.RESULT_PASS,
                decode_responses=True, socket_connect_timeout=config.REDIS_TIMEOUT, socket_timeout=config.REDIS_TIMEOUT))  # redis结果
        self.redis_machine = redis.StrictRedis(
            connection_pool=redis.ConnectionPool(
                host=config.MACHINE_HOST, port=config.MACHINE_PORT, password=config.MACHINE_PASS,
                decode_responses=True, socket_connect_timeout=config.REDIS_TIMEOUT, socket_timeout=config.REDIS_TIMEOUT))  # redis机器
        self.base = Base()  # 基础类
        self.machine_addr = ""
        self.key_label = ""  # 标识键
        self.key_data = ""  # 数据键
    
    def main_run(self):
        self.logger.setLevel(level=logging.INFO)  # 日志级别
        handler = logging.FileHandler(config.LOG_DIR)  # 日志地址
        # handler = logging.StreamHandler()  # 日志流
        handler.setFormatter(self.formatter)  # 日志格式化
        self.logger.addHandler(handler)  # 加载日志
        self.base.logger = self.logger
        self.machine_addr = self.base.get_addr()  # 获取地址
        if self.machine_addr:
            self.logger.removeHandler(handler)
            return True
        else:
            self.logger.removeHandler(handler)
            return False
    
    def check_data(self) -> bool:
        self.logger.setLevel(level=logging.INFO)  # 日志级别
        handler = logging.FileHandler(config.LOG_DIR)  # 日志地址
        # handler = logging.StreamHandler()  # 日志流
        handler.setFormatter(self.formatter)  # 日志格式化
        self.logger.addHandler(handler)  # 加载日志
        try:
            get_data = self.redis_machine.hgetall(self.machine_addr)  # 获取消息
        except Exception as ex:
            self.logger.info(f"从机器拿数据失败(*>﹏<*)【{ex}】")
            self.logger.removeHandler(handler)
            return False
        else:
            if get_data:
                self.key_label = get_data.get('key_label', '')  # 消息标识
                self.key_data = get_data.get('key_data', "")  # 消息数据
                if self.key_label and self.key_data:
                    self.key_data = eval(self.key_data)
                    self.logger.info(f"从机器拿数据成功(*^__^*)【{self.key_label}】")
                    self.logger.removeHandler(handler)
                    return True
                else:
                    self.logger.removeHandler(handler)
                    return False
            else:
                self.logger.removeHandler(handler)
                return False
        
    def switch_task(self) -> None:
        """
        选择任务启动函数
        :return: None
        """
        self.logger.setLevel(level=logging.INFO)  # 日志级别
        handler = logging.FileHandler(f"log/{self.key_label}.log")  # 日志地址
        # handler = logging.StreamHandler()  # 日志流
        handler.setFormatter(self.formatter)  # 日志格式化
        self.logger.addHandler(handler)  # 加载日志
        self.base.logger = self.logger
        if "order" in self.key_label and self.key_data:  # 如果走下单
            order = Order()  # 声明下单类
            order.base = self.base
            order.logger = self.logger  # 日志赋值
            order.redis_queue, order.redis_result, order.redis_machine = self.redis_queue, self.redis_result, self.redis_machine
            order.circulation_failure, order.proxy_failure = config.CIRCULATION_FAILURE, config.PROXY_FAILURE
            order.machine_addr = self.machine_addr
            order.key_label = self.key_label
            order.execute_process(self.key_data)
            del order
        elif "pay" in self.key_label and self.key_data:  # 如果走下单
            pay = Pay()  # 声明下单类
            pay.base = self.base
            pay.logger = self.logger  # 日志赋值
            pay.redis_queue, pay.redis_result, pay.redis_machine = self.redis_queue, self.redis_result, self.redis_machine
            pay.proxy_failure = config.PROXY_FAILURE
            pay.machine_addr = self.machine_addr
            pay.key_label = self.key_label
            pay.execute_process(self.key_data)
            del pay
        elif "audit" in self.key_label and self.key_data:  # 如果走下单
            audit = Audit()  # 声明下单类
            audit.base = self.base
            audit.logger = self.logger  # 日志赋值
            audit.redis_queue, audit.redis_result, audit.redis_machine = self.redis_queue, self.redis_result, self.redis_machine
            audit.proxy_failure = config.PROXY_FAILURE
            audit.machine_addr = self.machine_addr
            audit.key_label = self.key_label
            audit.execute_process(self.key_data)
            del audit
        self.key_label = ""  # 标识键
        self.key_data = ""  # 数据键
        self.redis_machine.hmset(self.machine_addr, {"key_label": "", "key_data": ""})  # 获取消息
        self.logger.removeHandler(handler)

        
if __name__ == '__main__':
    task = Task()
    if task.main_run():
        while True:
            time.sleep(1)
            if task.check_data():
                task.switch_task()

