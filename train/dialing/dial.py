#! /usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
    written by pyleo
"""
import sys                                                      # 导入环境当前目录
sys.path.append('..')
from dialing import config
from concurrent.futures import ThreadPoolExecutor
import paramiko
import redis
import time
import logging
import re


# # # 连接redis队列库
redis_queue = redis.StrictRedis(
    connection_pool=redis.ConnectionPool(
        host=config.QUEUE_HOST, port=config.QUEUE_PORT, password=config.QUEUE_PASS,
        decode_responses=True, socket_connect_timeout=config.REDIS_TIMEOUT, socket_timeout=config.REDIS_TIMEOUT))
# # # 连接redis机器库
redis_machine = redis.StrictRedis(
    connection_pool=redis.ConnectionPool(
        host=config.MACHINE_HOST, port=config.MACHINE_PORT, password=config.MACHINE_PASS,
        decode_responses=True, socket_connect_timeout=config.REDIS_TIMEOUT, socket_timeout=config.REDIS_TIMEOUT))
# # # 日志
logger = logging.getLogger("dial")
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter('【%(asctime)s】%(message)s')
# handler = logging.StreamHandler()
handler = logging.FileHandler("dial.log")
handler.setFormatter(formatter)
logger.addHandler(handler)


def dial_proxy() -> None:
    """
    代理拨号
    :return: None
    """
    try:
        # # # 获取待拨号地址
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        host = redis_queue.rpop(config.PROXY_DIALING)
        # # # 解析代理地址和数据
        if host:
            data = redis_machine.hgetall(host)
            if data:
                host_list = host.split("@")
                # # # 连接登陆并拨号
                ssh_client.connect(hostname=host_list[0], port=int(host_list[1]), username=data.get('proxy_user', ''),
                                   password=data.get('proxy_password', ''), look_for_keys=False, allow_agent=False,
                                   timeout=5, auth_timeout=5, banner_timeout=5)
                ssh_client.exec_command("kill -9 `ps -ef | grep pppoe | awk '{print $2}' `")
                ssh_client.exec_command("adsl-stop;adsl-start")
                # # # 休息10秒再获取代理状态
                time.sleep(10)
                std_in, std_out, std_err = ssh_client.exec_command("pppoe-status")
                results = std_out.read().decode('utf-8')
                result = re.sub("\r|\n|\\s|\t", "", results)
                # # # 根据状态判断，如果没有则放回待拨号队列
                if "running" not in result:
                    logger.info(f"匹配状态失败(*>﹏<*)【{host}】")
                    ssh_client.exec_command("kill -9 `ps -ef | grep pppoe | awk '{print $2}' `")
                    redis_queue.lpush(config.PROXY_DIALING, host)
                else:
                    re_ip = re.search(r"pppinet\d+.\d+.\d+.\d+", result)
                    if not re_ip:
                        logger.info(f"代理匹配失败(*>﹏<*)【{host}】【{result}】")
                        ssh_client.exec_command("kill -9 `ps -ef | grep pppoe | awk '{print $2}' `")
                        redis_queue.lpush(config.PROXY_DIALING, host)
                    else:
                        std_in, std_out, std_err = ssh_client.exec_command("ping -w2 -c1 kyfw.12306.cn")
                        results = std_out.read().decode('utf-8')
                        result = re.sub("\r|\n|\\s|\t", "", results)
                        if "100%packetloss" in result:
                            logger.info(f"代理请求不通(*>﹏<*)【{host}】【{result}】")
                            ssh_client.exec_command("kill -9 `ps -ef | grep pppoe | awk '{print $2}' `")
                            redis_queue.lpush(config.PROXY_DIALING, host)
                        else:
                            ip = re_ip[0].replace("pppinet", "")
                            result_data = {"proxy_server": f"http://{ip}:3138", "proxy_user": data.get('proxy_user', ''),
                                           "proxy_password": data.get('proxy_password', ''), "proxy_auth": data.get('proxy_auth', '')}
                            redis_machine.hmset(host, result_data)
                            redis_queue.lpush(config.PROXY_CHECK, host)
                            logger.info(f"添加全新代理(*^__^*)【{host}】")
                ssh_client.exec_command("echo 3 > /proc/sys/vm/drop_caches")
                ssh_client.close()
    except Exception as ex:
        logger.info(f"程序执行失败(*>﹏<*)【{ex}】")


def run(n) -> None:
    """
    循环拨号
    :param n: 线程数,未使用
    :return: None
    """
    while True:
        dial_proxy()


if __name__ == '__main__':
    num = config.DIALING_THREAD                                 # 获取线程数
    n_value = ""                                                # 生成相应空的列表参数
    n_list = [n_value for i in range(num)]
    with ThreadPoolExecutor(max_workers=num) as executor:
        executor.map(run, n_list)
