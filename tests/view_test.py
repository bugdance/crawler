#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> view test
@@..> package tests
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> import current path
import sys
sys.path.append('..')
# @@..> base import
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import random
# @@..> import utils
from utils.auto_tools import AutoAct
from utils.base_tools import BaseAct, LogAct
# from utils.data_tools import DataAct
from utils.json_tools import JsonAct
from utils.net_tools import NetAct
from utils.pool_tools import AppAct, PoolAct
from utils.num_tools import NumAct, TimeAct
from utils.str_tools import StrAct, UrlAct, DomAct, EncryptAct


logger, handler = LogAct.init_log()
TimeAct.logger = logger


async def test():
    """
    [Set to Chrome]
    """
    auto = AutoAct()
    auto.logger = logger
    
    if error := await auto.set_browser(False):
        logger.info(error)
        return False
    if error := await auto.set_clear():
        logger.info(error)
        return False
    if error := await auto.set_intercept(True):
        logger.info(error)
        return False
    if error := auto.set_capture('request', intercept_img):
        logger.info(error)
        return False
    # if error := await auto.set_capture('response', intercept_response):
    #     logger.info(error)
    #     return False

    hongshu_cookie = ""
    hongshu = [
        "https://www.xiaohongshu.com/user/profile/57e73e7f5e87e734c2209530",
        "https://www.xiaohongshu.com/user/profile/5840ee5782ec390b6afa573e",
        "https://www.xiaohongshu.com/user/profile/5ad940b411be105c406bf6a8",
        "https://www.xiaohongshu.com/user/profile/5b0184a711be1055f3c22f27",
        "https://www.xiaohongshu.com/user/profile/5aeb0bfb4eacab276f62bcf9",
        "https://www.xiaohongshu.com/user/profile/58cd59bb50c4b42d2e7d8073",
        "https://www.xiaohongshu.com/user/profile/584cbbae50c4b445ab6eecfc",
        "https://www.xiaohongshu.com/user/profile/5aa5096ce8ac2b3947ee481d",
        "https://www.xiaohongshu.com/user/profile/58fea24e5e87e7149ae8d116",
        "https://www.xiaohongshu.com/user/profile/5b149b1ce8ac2b3671a245c6",
    ]
    url = random.choice(hongshu)
    if error := await auto.set_url(url):
        logger.info(error)
        return False

    await asyncio.sleep(10)
    cookies = await auto.get_cookies()
    for i in cookies:
        if i.get("name") == "timestamp2":
            hongshu_cookie = i.get("value")
            print(hongshu_cookie)
            
    if error := await auto.set_quit():
        logger.info(error)
        return False


async def intercept_img(request):
    if request.resourceType in ['image', 'media', 'eventsource', 'websocket']:
        await request.abort()
    else:
        await request.continue_()


async def intercept_request(request):
    """请求过滤"""
    if "/user/profile" in request.url:
        pass
        # resp = await request.text()
        # headers = request.headers
    await request.continue_()


async def intercept_response(response):
    """响应过滤"""
    resourceType = response.request.resourceType
    if resourceType in ['xhr', 'fetch']:
        # resp = await response.text()
        # resp = response.url
        pass


if __name__ == "__main__":
    # 定时运行
    # now = timeAct.parse_timestamp([])

    # scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")
    # scheduler.add_job(
    #     func=brush_value, trigger='interval', minutes=20, next_run_time=now)
    # scheduler.start()
    # asyncio.get_event_loop().run_forever()

    asyncio.get_event_loop().run_until_complete(test())