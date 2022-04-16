#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> unit test
@@..> package tests
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> import current path
import sys
sys.path.append('..')
# @@..> base import
from utils.base_tools import BaseAct, LogAct
# from utils.auto_tools import AutoAct
from utils.data_tools import DataAct
from utils.json_tools import JsonAct
from utils.net_tools import NetAct
from utils.pool_tools import PoolAct
from utils.num_tools import NumAct, TimeAct
from utils.str_tools import StrAct, UrlAct, DomAct, EncryptAct
# @@..> import data
from data_tester import data
import pandas as pd




if __name__ == '__main__':

    logger, handler = LogAct.init_log()

    # TimeAct.logger = logger
    # StrAct.logger = logger
    # JsonAct.logger = logger
    
    # slide = DataAct()
    # slide.logger = logger
    


    pool = PoolAct()
    pool.logger = logger
    pool.init_app()
    
    # source = pool.init_mongo("mongodb://127.0.0.1:27017/source")
    
    # result = pool.query_mongo(source, "update", {"platId": 1}, {"fansNum": "$profileCounts.fansNum"}, [])
    # df = pd.DataFrame(list(result))
    # print(df["fansNum"].mean())
    
    
    # result = pool.query_mongo(
    #     jingdong, "company",
    #     {}, {}, []
    # )
    

    # path = "jingdong.csv"
    # columns_list = ['_id', "keyword", "name"]
    
    # df = pd.DataFrame(list(result), columns=columns_list)
    # df.to_csv(path, index=False)
    
    # from faker import Faker
    # fake = Faker(['zh_CN'])
    # print(fake.address())