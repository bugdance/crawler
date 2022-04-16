#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> task test
@@..> package tests
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> import current path
import sys
sys.path.append('..')
# @@..> import utils
from utils.base_tools import BaseAct, LogAct
from utils.net_tools import NetAct
from utils.json_tools import JsonAct
from utils.str_tools import StrAct
# @@..> import rulers
from tasks.rules.persdy_ruler import PersDYWorker
from tasks.rules.persks_ruler import PersKSWorker
from tasks.rules.persbl_ruler import PersBLWorker
from tasks.rules.pershs_ruler import PersHSWorker
from tasks.rules.perswb_ruler import PersWBWorker
from tasks.rules.perswx_ruler import PersWXWorker
from tasks.rules.perszh_ruler import PersZHWorker
from tasks.rules.perstt_ruler import PersTTWorker
from tasks.rules.persws_ruler import PersWSWorker
from tasks.rules.persxg_ruler import PersXGWorker
from tasks.rules.corpte_ruler import CorpTEWorker
from tasks.rules.celekm_ruler import CeleKMWorker


logger, handler = LogAct.init_log()


def post_test():

    post_data = {
                 # '_id': '1ad0bd7fdf507d1fe26f7bd3c339ae97',
                 '_id': 'api53',
                 'envMap': '66d7da3e5e9d6e351998a2d21a663512',
                #   'scrapeUrl': 'https://space.bilibili.com/29285093',
                  'scrapeUrl': 'http://www.iesdouyin.com/share/user/71692120736?u_code=i77iiihf&sec_uid=MS4wLjABAAAARaTWR2PrDogrw372-2LDD4oBLSOrgtdMXJTCqbPA6Uk&utm_campaign=client_share&app=aweme&utm_medium=ios&tt_from=copy&utm_source=copy',
                #  'scrapeUrl': 'https://www.xiaohongshu.com/user/profile/5a13b53b4eacab190f3d0667',
                 # 'scrapeUrl': 'http://www.gifshow.com/s/9knHq1em',
                #  'scrapeUrl': 'https://v.kuaishou.com/972Obb',
                 'ruleType': 2, 'platIdentity': 'bl', 'accountIdentity': 'pers',
                 'username': 'chrome', 'password': '',
                "cookies": {
                    # 'kuaishou.live.bfb1s': '9b8f70844293bed778aade6e0a8f9942',
                    # 'did': 'web_ac5196a6ff3a4a8693d4b85f962da372',
                    # 'kpn': 'GAME_ZONE',
                    # 'userId': '2146724529',
                    # 'kuaishou.live.web_st': 'ChRrdWFpc2hvdS5saXZlLndlYi5zdBKgAWEhrrcAzfAOc7ApHmcLL3406pe1PJA2xaRD1xInuinXMOeU4g-F5gsrWjMTsKYAK_wQ0t4IWfH7Ne-9Gd9qOB8f3NxW2pYJLQvcThgkTJ2thBN0KUQo2WdkDYsTFrQonj2H1ZuD6OcgCIc_rWP6VqatPBzeQ9Lze6CiWIX8-lt2EyKL-EBT1kBbRLq-anw_HJz4d4kyjyLHlZbwSVaZp0caEgCrAu8bFEUPixNgRvVq1Nb0ZSIgNNDG0gtIFfZbKvzRliryy2TZlWLt-GxCo5AE97LwMiAoBTAB',
                    # 'kuaishou.live.web_ph': '90d5474dd7f839b3ae82fdd9e49aa5b232cc',
                },
                }
    jsonAct = JsonAct(logger)
    strAct = StrAct(logger)
    sessAct = SessionAct(logger)
    sessAct.start_session()
    sessAct.timeout = 10
    header_version, user_agent, init_header = sessAct.set_header("Flask")
    sessAct.request_header = init_header
    sessAct.request_url = "http://156.240.107.137:18082/api/worker/"
    post_data = jsonAct.format_string(post_data)
    sessAct.post_data = strAct.format_gzip(post_data)
    sessAct.check_post(False)
    sessAct.check_page(False)


def local_test():
    post_data = {
                # '_id': '1ad0bd7fdf507d1fe26f7bd3c339ae97',
                '_id': 'api53',
                'envMap': '66d7da3e5e9d6e351998a2d21a663512',
                #  'scrapeUrl': 'https://space.bilibili.com/29285093',
                #  "scrapeUrl": "https://www.bilibili.com/video/BV1P64y167cN",
                #  'scrapeUrl': 'https://v.douyin.com/doEErap/',
                #  'scrapeUrl': 'https://www.douyin.com/user/MS4wLjABAAAAgw0GoIz5UYry1Msxuz4hIyCtKDXcJjb2RDm_LuYRArQ?previous_page=app_code_link',
                #  "scrapeUrl": "https://www.iesdouyin.com/share/user/MS4wLjABAAAAVa-EEhv-XLYqYqQK9cbdI6Vio6669YTrdbxOOOV6yZ8?sec_uid=MS4wLjABAAAAVa-EEhv-XLYqYqQK9cbdI6Vio6669YTrdbxOOOV6yZ8",
                # "scrapeUrl": "https://www.iesdouyin.com/share/user/59740671411?sec_uid=MS4wLjABAAAAQAy6DRBdPf81IBWFxrjSo28VNv8fqskbkWemGEVFHkw",
                # 'scrapeUrl': 'https://weibo.com/pudongnews',
                # 'scrapeUrl': 'https://m.weibo.cn/u/1822022935',
                # 'scrapeUrl': 'https://www.toutiao.com/c/user/token/MS4wLjABAAAAXcZXSbvWev4glCjwKPQkZd9KY_fvucdnTt3eVlRHryMeJ0E6sOlhZKeotCMd38KT/?source=feed',
                # 'scrapeUrl': 'https://www.toutiao.com/a7031903736716984836/',
                'scrapeUrl': 'https://www.zhihu.com/people/hei-ze-peng-shi/posts',
                # 'scrapeUrl': "http://zhuanlan.zhihu.com/p/30752040",
                # 'scrapeUrl': "https://weixin.sogou.com/weixin?type=1&s_from=input&query=rmrbwx&ie=utf8&_sug_=n&_sug_type_=",
                # 'scrapeUrl': 'https://www.ixigua.com/home/3768752705372835/?list_entrance=homepage',
                # "scrapeUrl": "https://weibo.com/2557375422/KtiZy2WyI?from=page_1001062557375422_profile&wvr=6&mod=weibotime",
                
                # "scrapeUrl": "https://live.kuaishou.com/profile/LLi20010302",
                # "scrapeUrl": "https://live.kuaishou.com/u/2181681/3xfwy4un4i3fyrc",
                # "scrapeUrl": "https://live.kuaishou.com/u/KPL704668133/3xwbgm953qds3h6",
                # 'scrapeUrl': 'https://www.xiaohongshu.com/discovery/item/61130d22000000000102ec3d',
                # "scrapeUrl": "https://www.xiaohongshu.com/discovery/item/6138e0c30000000021037b49",
                #  'scrapeUrl': "https://h5.weishi.qq.com/weishi/personal/1619309092424220/wspersonal",
                #  'scrapeUrl': 'https://h5.weishi.qq.com/weishi/feed/7pOQmQ47q1MUX8seS/wsfeed?wxplay=1&id=7pOQmQ47q1MUX8seS&spid=',
                # 'scrapeUrl': 'https://www.xiaohongshu.com/user/profile/6095776f000000000101fbed',
                # 'scrapeUrl': 'https://www.xiaohongshu.com/user/profile/5555a2d862a60c11e5838975',
                #  'scrapeUrl': 'https://weixin.sogou.com/weixin?type=1&s_from=input&query=wwwbailve&ie=utf8&_sug_=n&_sug_type_=',
                'toolType': 3, "flowType": 1, 'platIdentity': 'wb', 'accountIdentity': 'pers',
                'username': 'chrome', 'password': '', "isUrls": 1, "isLast": 1,
                "cookies": {
                    # 'cookie': '__ac_nonce=061a6eda200e59b98e0f7; __ac_signature=_02B4Z6wo00f01y-npbQAAIDDr6Vf93z9OD8vh6EAAKpZa2; ttcid=8ed07bbd3d134113b4f04e63b960480423; tt_webid=7036572732482111013; csrftoken=8dd698739b72695b5af783987f50e740; s_v_web_id=verify_kwmz8qkp_8bu9MhJV_fWlD_4QYr_8eR4_aKfEdgTwR98E; MONITOR_WEB_ID=7036572732482111013; ttwid=1%7CXRibk1-39iT5OIOPzOmLuddTxeJx82f69ZHAqbH7FFQ%7C1638329773%7Cfe110b8faff7828f2e877cbffe25ca032a893fd82a709c6a7928f50b48b30ef8; tt_scid=FAAtSMLjWA5V8i1sX7DewihGtSwGyxPcCx7aE2SGJfokXJNF7z6ZiaDGdXAQx1-p19de'
                    'cookie': 'uuid_n_v=v1; uuid=32CB843078CD11ECB4D1C7788BF30AC7230CD0E2A29C4DC283DBC32F03E351CC; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1642558328; _lxsdk_cuid=17e701b0c6613-0c34ef9ce73f8f-978183a-144000-17e701b0c67c8; _lxsdk=32CB843078CD11ECB4D1C7788BF30AC7230CD0E2A29C4DC283DBC32F03E351CC; __mta=19272455.1642558328009.1642558340436.1642558343269.3; _lxsdk_s=17e701b0c67-76a-18-337%7C%7C12; _csrf=008757b25afc9f2d22edb6ae9eadd16bfb2e521b0cf359516b68ed2e03d4cbc2'
                },
                    
                
                }

    account = "cele"
    plat = "km"
    create_var = globals()
    worker = create_var[account.capitalize() + plat.upper() + "Worker"]()
    result = worker.process_main(post_data)


if __name__ == '__main__':
    # post_test()
    local_test()

    