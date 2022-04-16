#! /usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
    written by pyleo
"""
import time


class Query:
    """
    查询类
    """
    def __init__(self):
        self.logger = None                      # 日志
        self.mongo_client = None                # 数据库连接
        self.mongo_db = None                    # 数据库
        self.mongo_coll = None                  # 数据表
        self.redis_queue = None
        self.current_time = None                # 当前时间
        self.last_time = None                   # 最后时间
        self.first_time = None                  # 开始时间
        self.sum_count = 0                      # 总订单数
        self.success_count = 0                  # 成功响应数
        self.failure_count = 0                  # 失败响应数
        self.tickets_count = 0                  # 占座成功数
        self.success_rate = 0.00                # 返回成功率
        self.failure_rate = 0.00                # 返回失败率
        self.tickets_rate = 0.00                # 占座成功率
        self.average_time = 0.00                # 平均耗时
        self.is_more = False                    # 是否多了失败原因
        self.none_count = 0                     # 无票订单
        self.wait_count = 0                     # 排队订单
        self.verification_count = 0             # 核验订单
        self.conflict_count = 0                 # 冲突订单
        self.restrict_count = 0                 # 限制订单
        self.init_count = 0                     # 初始订单
        self.comparison_count = 0               # 比对订单
        self.timeout_count = 0                  # 超时订单
        self.none_rate = 0.00                   # 无票率
        self.wait_rate = 0.00                   # 排队率
        self.verification_rate = 0.00           # 核验率
        self.conflict_rate = 0.00               # 冲突率
        self.restrict_rate = 0.00               # 限制率
        self.init_rate = 0.00                   # 初始率
        self.comparison_rate = 0.00             # 比对率
        self.timeout_rate = 0.00                # 超时率
        self.all_times = []                     # 时间图每分时间列表
        self.all_sum = []                       # 时间图每分订单总数
        self.all_tickets = []                   # 时间图每分占座总数
        self.all_rate = []                      # 时间图每分占座成功率
        self.machines = 0                       # 在线rep数
        self.proxies = 0                        # 在线代理数
        
    def connect_mongo(self) -> None:
        """
        数据库连接
        :return: None
        """
        try:
            self.mongo_db = self.mongo_client['statistics']                         # 数据库
            self.mongo_coll = self.mongo_db['monitor']                              # 监控表
        except Exception as ex:
            self.logger.info(f"连接数据库失败(*>﹏<*)【{ex}】")
        else:
            self.logger.info(f"连接数据库成功(*^__^*)【OK】")
    
    def get_machines(self) -> None:
        """
        获取机器数
        :return: None
        """
        try:
            self.machines = self.redis_queue.llen("machines")
            self.proxies = self.redis_queue.llen("proxy_leisure")
        except Exception as ex:
            self.logger.info(f"连接数据队列失败(*>﹏<*)【{ex}】")
        else:
            self.logger.info(f"连接数据队列成功(*^__^*)【OK】")
        
    def get_time(self) -> None:
        """
        获取时间范围
        :return: None
        """
        unit = 60  # 单位
        cur_time = int(time.time())  # 现在时间
        self.current_time = cur_time - (cur_time % unit)  # 上一时间
        self.last_time = self.current_time + 60  # 结束时间
        self.first_time = self.last_time - 2400  # 起始时间
    
    def get_data(self) -> None:
        """
        获取数据统计
        :return: None
        """
        try:
            self.sum_count = len(self.mongo_coll.distinct(
                "key", {"status": "order", "start_time": {"$gte": self.first_time, "$lt": self.last_time}}))
            self.tickets_count = len(self.mongo_coll.distinct(
                "key", {"status": "order", "start_time": {"$gte": self.first_time, "$lt": self.last_time}, "real_msg": {"$regex": "成功"}}))
            self.failure_count = self.sum_count - self.tickets_count
    
            self.none_count = len(self.mongo_coll.distinct(
                "key", {"status": "order", "start_time": {"$gte": self.first_time, "$lt": self.last_time},
                        "$or": [{"real_msg": {"$regex": "无余票"}}, {"real_msg": {"$regex": "足够的票"}}]}))
            self.wait_count = len(self.mongo_coll.distinct(
                "key", {"status": "order", "start_time": {"$gte": self.first_time, "$lt": self.last_time},
                        "$or": [{"real_msg": {"$regex": "排队"}}, {"real_msg": {"$regex": "等待"}}]}))
            self.verification_count = len(self.mongo_coll.distinct(
                "key", {"status": "order", "start_time": {"$gte": self.first_time, "$lt": self.last_time}, "real_msg": {"$regex": "核验"}}))
            self.conflict_count = len(self.mongo_coll.distinct(
                "key", {"status": "order", "start_time": {"$gte": self.first_time, "$lt": self.last_time}, "real_msg": {"$regex": "行程冲突"}}))
            self.restrict_count = len(self.mongo_coll.distinct(
                "key", {"status": "order", "start_time": {"$gte": self.first_time, "$lt": self.last_time}, "real_msg": {"$regex": "限制"}}))
            self.init_count = len(self.mongo_coll.distinct(
                "key", {"status": "order", "start_time": {"$gte": self.first_time, "$lt": self.last_time},
                        "$or": [{"real_msg": {"$regex": "乘客人数不符"}}, {"real_msg": {"$regex": "证件格式不对"}},
                                {"real_msg": {"$regex": "解析接口数据失败"}}]}))
            self.comparison_count = len(self.mongo_coll.distinct(
                "key", {"status": "order", "start_time": {"$gte": self.first_time, "$lt": self.last_time},
                        "$or": [{"real_msg": {"$regex": "没有此坐席"}}, {"real_msg": {"$regex": "不可识别的坐席"}}]}))
            self.timeout_count = len(self.mongo_coll.distinct(
                "key", {"status": "order", "start_time": {"$gte": self.first_time, "$lt": self.last_time},
                        "$or": [{"real_msg": {"$regex": "超时"}}, {"real_msg": {"$regex": "网络忙"}},
                                {"real_msg": {"$regex": "系统繁忙"}}, {"real_msg": {"$regex": "操作失败"}}]}))
            self.success_count = self.sum_count - self.timeout_count
            failure_sum = self.none_count + self.wait_count + self.verification_count + self.conflict_count + \
                          self.restrict_count + self.init_count + self.comparison_count + self.timeout_count
            if self.failure_count != failure_sum:
                self.is_more = True
        except Exception as ex:
            self.logger.info(f"获取数据统计失败(*>﹏<*)【{ex}】")
        else:
            self.logger.info(f"获取数据统计成功(*^__^*)【OK】")
      
    def get_rate(self) -> None:
        """
        获取数据比例
        :return: None
        """
        try:
            if self.sum_count:
                self.tickets_rate = round((self.tickets_count / self.sum_count) * 100, 2)
                self.failure_rate = round((self.failure_count / self.sum_count) * 100, 2)
                self.success_rate = round((self.success_count / self.sum_count) * 100, 2)
                sum_time = 0
                run_time = self.mongo_coll.find({"status": "order", "start_time": {"$gte": self.first_time, "$lt": self.last_time}}, {"_id": 0, "run_time": 1})
                for i in run_time:
                    sum_time += i.get('run_time', 0)
                self.average_time = round(sum_time / self.sum_count, 2)
            if self.failure_count:
                self.none_rate = round((self.none_count / self.failure_count) * 100, 2)  # 无票率
                self.wait_rate = round((self.wait_count / self.failure_count) * 100, 2)  # 排队率
                self.verification_rate = round((self.verification_count / self.failure_count) * 100, 2)  # 核验率
                self.conflict_rate = round((self.conflict_count / self.failure_count) * 100, 2)  # 冲突率
                self.restrict_rate = round((self.restrict_count / self.failure_count) * 100, 2)  # 限制率
                self.init_rate = round((self.init_count / self.failure_count) * 100, 2)  # 初始率
                self.comparison_rate = round((self.comparison_count / self.failure_count) * 100, 2)  # 比对率
                self.timeout_rate = round((self.timeout_count / self.failure_count) * 100, 2)  # 超时率
        except Exception as ex:
            self.logger.info(f"获取数据比例失败(*>﹏<*)【{ex}】")
        else:
            self.logger.info(f"获取数据比例成功(*^__^*)【OK】")

    def get_in(self) -> None:
        """
        获取每分钟数据
        :return: None
        """
        try:
            for i in range(self.first_time, self.last_time, 60):
                per_time = time.strftime("%H:%M", time.localtime(i))
                per_sum = len(self.mongo_coll.distinct("key", {"status": "order", "start_time": {"$gte": i, "$lt": i + 60}}))
                if per_sum:
                    per_tickets = len(self.mongo_coll.distinct("key", {"status": "order", "start_time": {"$gte": i, "$lt": i + 60}, "real_msg": {"$regex": "成功"}}))
                    per_rate = round((per_tickets / per_sum) * 100, 2)
                else:
                    per_sum, per_tickets, per_rate = 0, 0, 0.00
                self.all_times.append(per_time)
                self.all_sum.append(per_sum)
                self.all_tickets.append(per_tickets)
                self.all_rate.append(per_rate)
        except Exception as ex:
            self.logger.info(f"获取每分钟数据失败(*>﹏<*)【{ex}】")
        else:
            self.logger.info(f"获取每分钟数据成功(*^__^*)【OK】")

    def main(self) -> None:
        """
        主运行函数
        :return: None
        """
        self.connect_mongo()
        self.get_machines()
        self.get_time()
        self.get_data()
        self.get_rate()
        self.get_in()
