# -*- coding: utf-8 -*-
"""
  █████▒█    ██  ▄████▄   ██ ▄█▀       ██████╗ ██╗   ██╗ ██████╗
▓██   ▒ ██  ▓██▒▒██▀ ▀█   ██▄█▒        ██╔══██╗██║   ██║██╔════╝
▒████ ░▓██  ▒██░▒▓█    ▄ ▓███▄░        ██████╔╝██║   ██║██║  ███╗
░▓█▒  ░▓▓█  ░██░▒▓▓▄ ▄██▒▓██ █▄        ██╔══██╗██║   ██║██║   ██║
░▒█░   ▒▒█████▓ ▒ ▓███▀ ░▒██▒ █▄       ██████╔╝╚██████╔╝╚██████╔╝
 ▒ ░   ░▒▓▒ ▒ ▒ ░ ░▒ ▒  ░▒ ▒▒ ▓▒       ╚═════╝  ╚═════╝  ╚═════╝
 ░     ░░▒░ ░ ░   ░  ▒   ░ ░▒ ▒░
 ░ ░    ░░░ ░ ░ ░        ░ ░░ ░
          ░     ░ ░      ░  ░
-------------------------------------------------
   File Name：     search_douyin_mod
   Description :
   Author :       92159
   date：          2020/7/17
-------------------------------------------------
   Change Activity:
                   2020/7/17:
-------------------------------------------------
"""
__author__ = '92159'
import time
import requests
from test import get_X_gorgon, get_X_SS_STUB


COOKIES = 'passport_csrf_token_default=54278c62e15adf1c88bcadfc8697c2ad; d_ticket=cf42ecee3fbcd6b307de5485590173f2b2453; odin_tt=bf074285eb2caa4b6f4b06cf79d10843d9058aad42fca94bc885c20920196d183528b303649c9b5c0008a4e2287f4a68c798a084d5ac7b743f3e4e8ce6b6fcd8; n_mh=ifHfdOse8u9fAK_x2qRh4FodX5daL8LL7Wyux1c10pE; sid_guard=a8a69cb41433ba2f7e76dce3d4f31e0c%7C1612167825%7C5184000%7CFri%2C+02-Apr-2021+08%3A23%3A45+GMT; uid_tt=ab192465ee88b435887226e3f0418a7a; sid_tt=a8a69cb41433ba2f7e76dce3d4f31e0c; sessionid=a8a69cb41433ba2f7e76dce3d4f31e0c'


def search(dy_id):
    """
    传入要查询的抖音ID,返回查询的账户信息,COOKIES使用多个可以有效保证搜索接口的可用性,搜索接口失效一般只需要更改cookie即可.
    """
    # 抖音的两个时间戳参数
    _rticket = int(str(time.time() * 1000).split('.')[0])
    ts = str(int(_rticket / 1000))

    # 搜索接口的URL
    URL = f"https://aweme.snssdk.com/aweme/v1/general/search/single/?manifest_version_code=700&_rticket={str(_rticket)}&app_type=normal&iid=2252218494104424&channel=wandoujia_aweme1&device_type=Redmi%20Note%208&language=zh&uuid=864202051562566&resolution=1080*2130&openudid=c700081bdd14ab2e&update_version_code=7002&os_api=28&dpi=440&ac=wifi&device_id=1600527877544045&mcc_mnc=46000&os_version=9&version_code=700&app_name=aweme&version_name=7.0.0&js_sdk_version=1.18.2.5&device_brand=xiaomi&ssmix=a&device_platform=android&aid=1128&ts={str(ts)}"
    URL = f"https://aweme-eagle.snssdk.com/aweme/v1/user/?sec_user_id=MS4wLjABAAAAObLdbYYOUIT671uIvJQc2AnwuKO3WawgbljgxtwMiMQ&retry_type=no_retry&iid=2252218494104424&device_id=1600527877544045&ac=wifi&channel=wandoujia_aweme1&aid=1128&app_name=aweme&version_code=700&version_name=7.0.0&device_platform=android&ssmix=a&device_type=Redmi+Note+8&device_brand=xiaomi&language=zh&os_api=28&os_version=9&uuid=864202051562566&openudid=c700081bdd14ab2e&manifest_version_code=700&resolution=1080*2130&dpi=440&update_version_code=7002&_rticket={str(_rticket)}&app_type=normal&js_sdk_version=1.18.2.5&mcc_mnc=46000&ts={str(ts)}"

    # 账号COOKIES
    # 请求参数
    POST_DATA = {
        'offset': 0,  # 请求页数
        'keyword': dy_id,  # 请求参数
        'count': 10,  # 数量
        'hot_search': 0,  # 热搜数量
        'is_pull_refresh': 0,
        'type': 1,
        'search_source': 'normal_search',
        'search_id': '',
        'query_correct_type': 1
    }
    # url参数
    URL_PARAMS = f'offset=0&keyword={dy_id}&count=10&type=1&is_pull_refresh=0&hot_search=0&search_source=normal_search&search_id=&query_correct_type=1'
    # 获取STUB
    X_SS_STUB = get_X_SS_STUB(URL_PARAMS)
    # 获取gorgon
    X_gorgon = get_X_gorgon(URL, COOKIES, ts)
    # 构建请求头
    HEADER = {
        'X-SS-STUB': X_SS_STUB,
        'Accept-Encoding': 'gzip',
        'X-SS-REQ-TICKET': str(_rticket),
        'sdk-version': '1',
        'Cookie': COOKIES,
        # 'x-tt-token': '0038e5a2d2d1b832fde4667e5bea5a1367afa4666acd0187c159bcfcfd843ef126165db8251a4a9f83b566192380d6ebab15',
        'X-Gorgon': X_gorgon,
        'X-Khronos': ts,
        "X-Pods": "",
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # 'Content-Length': '138',
        'Host': 'aweme.snssdk.com',
        'Connection': 'Keep-Alive',
        'User-Agent': 'com.ss.android.ugc.aweme/700 (Linux; U; Android 9; zh_CN; Redmi Note 8; Build/PKQ1.190616.001; Cronet/58.0.2991.0)',
    }



    HEADER = {
        # 'X-SS-STUB': X_SS_STUB,
        'Accept-Encoding': 'gzip',
        'X-SS-REQ-TICKET': str(_rticket),
        'sdk-version': '1',
        'Cookie': COOKIES,
        # 'x-tt-token': '0038e5a2d2d1b832fde4667e5bea5a1367afa4666acd0187c159bcfcfd843ef126165db8251a4a9f83b566192380d6ebab15',
        'X-Gorgon': X_gorgon,
        'X-Khronos': ts,
        "X-Pods": "",
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        # 'Content-Length': '138',
        'Host': 'aweme-eagle.snssdk.com',
        'Connection': 'Keep-Alive',
        'User-Agent': 'com.ss.android.ugc.aweme/700 (Linux; U; Android 9; zh_CN; Redmi Note 8; Build/PKQ1.190616.001; Cronet/58.0.2991.0)',
    }

    res = requests.get(url=URL, headers=HEADER).json()
    print(res)



if __name__ == '__main__':
    if not COOKIES:
        print(
            """
            !!!!!!
            请添加COOKIE.
            !!!!!!
            """
        )
    else:
        dy_id = input("Please enter your search account name:")
        result = search(dy_id)
        print(result)