#! /usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
    written by pyleo
"""
import sys                                                          # 导入环境当前目录
sys.path.append('..')
from dialing import config
from concurrent.futures import ThreadPoolExecutor
import redis
import logging
import requests
import re
from datetime import timedelta, date

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
logger = logging.getLogger("check")
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter('【%(asctime)s】%(message)s')
# handler = logging.StreamHandler()
handler = logging.FileHandler("check.log")
handler.setFormatter(formatter)
logger.addHandler(handler)
# # # 声明请求session
session = requests.session()


def parse_header(get_dict=None) -> dict:
    """
    声明请求头部
    :param get_dict:
    :return: dict
    """
    if not get_dict:
        get_dict = {}
    headers = {'accept-language': 'zh-CN,zh;q=0.9', 'accept-encoding': 'gzip, deflate, br', 'upgrade-insecure-requests': '1',
               'connection': 'keep-alive',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
               }
    headers.update(get_dict)
    return headers


def check_proxy() -> None:
    """
    请求代理是否可用
    :return: None
    """
    try:
        proxy_addr = redis_queue.rpop(config.PROXY_CHECK)                                                   # 从检查队里拿代理服务器地址
    except Exception as ex:
        logger.info(f"程序执行失败(*>﹏<*)【{ex}】")
    else:
        if proxy_addr:
            try:
                proxy_data = redis_machine.hgetall(proxy_addr)                                              # 从机器库里取代理数据
            except Exception as ex:
                logger.info(f"程序执行失败(*>﹏<*)【{ex}】")
            else:
                if proxy_data:                                                                              # 取出代理按请求格式去12306查询页请求
                    proxy_server = proxy_data.get("proxy_server", "")
                    proxy_server = proxy_server[7:]
                    proxy_auth = proxy_data.get("proxy_auth", "")
                    if proxy_addr and proxy_auth:
                        headers = parse_header(
                            {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                             'host': 'kyfw.12306.cn'})
                        proxies = {
                            "http": f"http://{proxy_auth}@{proxy_server}",
                            "https": f"http://{proxy_auth}@{proxy_server}"
                        }
                        query_url = "https://kyfw.12306.cn/otn/leftTicket/init"
                        try:
                            response = session.get(query_url, headers=headers, proxies=proxies, timeout=5)
                        except Exception as ex:
                            logger.info(f"程序执行失败(*>﹏<*)【{ex}】")
                            redis_queue.lpush(config.PROXY_DIALING, proxy_addr)                             # 如果失败则放回拨号队列
                        else:
                            result = re.search("'leftTicket/.*?'", response.text, re.S)                     # 匹配查询页需要拼接的参数
                            if not result:
                                logger.info(f"匹配链接失败(*>﹏<*)")
                                redis_queue.lpush(config.PROXY_DIALING, proxy_addr)                         # 如果失败则放回拨号队列
                            else:
                                base = re.search("(?<=').*(?=')", result[0], re.S)                          # 匹配查询页需要拼接的参数
                                if not base:
                                    logger.info(f"匹配链接失败(*>﹏<*)")
                                    redis_queue.lpush(config.PROXY_DIALING, proxy_addr)                     # 如果失败则放回拨号队列
                                else:
                                    train_date = str(date.today() + timedelta(days=15))                     # 查询15天后的日期
                                    # # # 拼接二次查询查询数据
                                    final_url = f"https://kyfw.12306.cn/otn/{base[0]}?leftTicketDTO.train_date={train_date}&" \
                                        f"leftTicketDTO.from_station=BJP&leftTicketDTO.to_station=SHH&purpose_codes=ADULT"
                                    headers['accept'] = '*/*'
                                    headers['referer'] = query_url
                                    headers['x-requested-with'] = 'X-Requested-With'
                                    try:
                                        response = session.get(final_url, headers=headers, proxies=proxies, timeout=5)
                                        result = response.json()
                                    except Exception as ex:
                                        logger.info(f"程序执行失败(*>﹏<*)【{ex}】")
                                        redis_queue.lpush(config.PROXY_DIALING, proxy_addr)                 # 如果失败则放回拨号队列
                                    else:
                                        if result.get("httpstatus", "") == 200 and result.get('status', ""):
                                            logger.info("代理验证成功(*^__^*)【OK】")
                                            redis_queue.lpush(config.PROXY_LEISURE, proxy_addr)             # 如果成功则放回空闲可用队列
                                        else:
                                            logger.info(f"代理验证失败(*>﹏<*)【{result.get('status', '')}】")
                                            redis_queue.lpush(config.PROXY_DIALING, proxy_addr)             # 如果失败则放回拨号队列


def check(n) -> None:
    """
    循环检查
    :param n: 线程数,未使用
    :return: None
    """
    while True:
        check_proxy()


if __name__ == '__main__':
    num = config.CHECK_THREAD                                               # 获取线程数
    n_value = ""                                                            # 生成相应空的列表参数
    n_list = [n_value for i in range(num)]
    with ThreadPoolExecutor(max_workers=num) as executor:
        executor.map(check, n_list)
