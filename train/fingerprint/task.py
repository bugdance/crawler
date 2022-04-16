#! /usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
    written by pyleo
"""
import sys
sys.path.append('..')  # 导入环境当前目录
from fingerprint import config
from fingerprint.browser import Browser
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timedelta
import redis
import logging
import time
import socket
socket.setdefaulttimeout(config.SOCKET_TIMEOUT)

redis_queue = redis.StrictRedis(
	connection_pool=redis.ConnectionPool(
		host=config.QUEUE_HOST, port=config.QUEUE_PORT, password=config.QUEUE_PASS,
		decode_responses=True, socket_connect_timeout=config.REDIS_TIMEOUT,
		socket_timeout=config.REDIS_TIMEOUT))  # redis队列


def main_run(thread):
	"""

	:return:
	"""
	logger = logging.getLogger(f"fingerprint{thread}")  # 基础日志
	formatter = logging.Formatter('【%(asctime)s】%(message)s')  # 日志格式
	logger.setLevel(level=logging.INFO)  # 日志级别
	handler = logging.FileHandler(f"fingerprint-{thread}.log")  # 日志地址
	# handler = logging.StreamHandler()  # 日志流
	handler.setFormatter(formatter)  # 日志格式化
	logger.addHandler(handler)  # 加载日志
	browser = Browser()
	browser.logger = logger
	time.sleep(thread * config.THREAD_INTERVAL)
	while True:
		try:
			switch = redis_queue.get("FingerSwitch")
			timeout = redis_queue.get("FingerTimeOut")
			if switch == "1":
				now = datetime.now()
				if now.hour is 5:
					if now.minute < 30:
						time.sleep(10)
					else:
						browser.set_headless("", 15)
						browser.set_url("https://www.12306.cn/index/index.html")
						time.sleep(10)
						device_id = browser.driver.get_cookie("RAIL_DEVICEID")
						expiration = browser.driver.get_cookie("RAIL_EXPIRATION")
						if device_id and expiration:
							deadline_time = int(time.time() * 1000) + int(timeout) * 60 * 1000  # 精确到毫秒
							send_data = {"deadlineTime": deadline_time,
										 "RAIL_DEVICEID": device_id['value'],
										 "RAIL_EXPIRATION": expiration['value']}
							redis_queue.lpush(config.QUEUE_NAME, str(send_data))
							logger.info(f"入库正常{expiration['value']}")
						browser.set_quit()
						browser.set_shell("./kill.sh")
						time.sleep(5)
				elif 5 < now.hour < 23:
					browser.set_headless("", 15)
					browser.set_url("https://www.12306.cn/index/index.html")
					time.sleep(10)
					device_id = browser.driver.get_cookie("RAIL_DEVICEID")
					expiration = browser.driver.get_cookie("RAIL_EXPIRATION")
					if device_id and expiration:
						deadline_time = int(time.time() * 1000) + int(timeout) * 60 * 1000		# 精确到毫秒
						send_data = {"deadlineTime": deadline_time,
									 "RAIL_DEVICEID": device_id['value'],
									 "RAIL_EXPIRATION": expiration['value']}
						redis_queue.lpush(config.QUEUE_NAME, str(send_data))
						logger.info(f"入库正常{expiration['value']}")
					browser.set_quit()
					browser.set_shell("./kill.sh")
					time.sleep(5)
				else:
					time.sleep(10)
			else:
				time.sleep(10)
		except Exception as ex:
			logger.info(f"程序出错{ex}")
			browser.set_quit()
			browser.set_shell("./kill.sh")
			time.sleep(5)
		else:
			pass

			
if __name__ == "__main__":
	num = config.THREAD  # 获取线程数
	thread_list = [i for i in range(num)]
	with ProcessPoolExecutor(max_workers=num) as executor:
		executor.map(main_run, thread_list)



