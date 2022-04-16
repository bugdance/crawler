#! /usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
    written by pyleo
"""
import sys                                                      # 导入环境当前目录
sys.path.append('..')
from simulation import config
from concurrent.futures import ThreadPoolExecutor
import paramiko
import redis
import logging
import re
import xlrd


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
logger = logging.getLogger("machine")
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter('【%(asctime)s】%(message)s')
handler = logging.StreamHandler()
# handler = logging.FileHandler("machines.log")
handler.setFormatter(formatter)
logger.addHandler(handler)

vps = []                        # 读取excel存放的数据


def read_excel(n) -> bool:
    """
    读取excel根据线程数分割数据
    :param n: 线程数
    :return: bool
    """
    try:
        with xlrd.open_workbook(r'machine.xlsx') as x:              # 打开excel
            table = x.sheets()[0]
        table_rows = table.nrows                                    # 获取行数
        if table_rows:
            modulo = table_rows % n                                 # 总行数取模
            remainder = 0
            if modulo:
                remainder = n - modulo                              # 取线程数余数
            for i in range(0, table_rows - modulo, n):              # 循环线程数整数个行
                thread_list = []                                    # 线程数列表
                for j in range(n):                                  # 线程数一组
                    excel_data = table.row_values(i + j)
                    excel_server = excel_data[0]
                    excel_port = int(excel_data[1])
                    excel_username = excel_data[2]
                    excel_password = excel_data[3]
                    thread_list.append([excel_server, excel_port, excel_username, excel_password])
                vps.append(thread_list)
            remainder_list = []                                         # 余数列表
            for i in range(table_rows - modulo, table_rows):            # 循环余数行
                excel_data = table.row_values(i)
                excel_server = excel_data[0]
                excel_port = int(excel_data[1])
                excel_username = excel_data[2]
                excel_password = excel_data[3]
                remainder_list.append([excel_server, excel_port, excel_username, excel_password])
            if remainder:
                for i in range(remainder):                              # 补全余数行数据
                    remainder_list.append([])
                vps.append(remainder_list)
    except Exception as ex:
        logger.info(f"读取列表失败(*>﹏<*)【{ex}】")
        return False
    else:
        return True


def remove_queue() -> bool:
    """
    删除代理队列
    :return: bool
    """
    try:
        redis_queue.delete(config.MACHINE_QUEUE)
    except Exception as ex:
        logger.info(f"程序执行失败(*>﹏<*)【{ex}】")
        return False
    else:
        return True
    

def connect_proxy(server_list=None):
    """
    连接远程vps服务器
    :return: None
    """
    try:
        if not server_list:
            server_list = []
        if server_list:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # # # ssh连接
            ssh_client.connect(hostname=server_list[0], port=server_list[1], username=server_list[2], password=server_list[3],
                               look_for_keys=False, allow_agent=False, timeout=5, auth_timeout=5, banner_timeout=5)
            # # # 获取代理状态
            std_in, std_out, std_err = ssh_client.exec_command('(cd /root/simulation; ./start.sh)')
            results = std_err.read().decode('utf-8')
            result = re.sub("\r|\n|\\s|\t", "", results)
            logger.info(result)
            redis_queue.lpush("machines", server_list[0])
            ssh_client.close()
    except Exception as ex:
        logger.info(f"程序执行失败（╯＾╰）【{server_list[0]}@{server_list[1]}】【{ex}】")


if __name__ == '__main__':
    num = config.MACHINE_THREAD                                                             # 获取线程数
    if remove_queue():
        if read_excel(num):                                                                 # 读取excel根据线程数分割数据
            for v in vps:
                with ThreadPoolExecutor(max_workers=num) as executor:
                    executor.map(connect_proxy, v)
