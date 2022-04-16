#! /usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
    written by pyleo
"""
import jsbeautifier
import Levenshtein
import requests
import difflib
import re
import time


class Compare:
    """
    对比函数类
    """
    def __init__(self):
        self.logger = None                          # 日志变量
        self.mongo_client = None                    # mongo数据库驱动
        self.mongo_db = None                        # mongo数据库
        self.mongo_parameter = None                 # mongo参数表
        self.mongo_content = None                   # mongo内容表
        self.mongo_time = None                      # mongo时间表
        self.new_stamp: int = 0                     # 最新时间时间戳
        self.old_stamp: int = 0                     # 上一次时间时间戳
        self.new_time: str = ""                     # 最新时间的格式化显示时间
        self.old_time: str = ""                     # 上一次时间的格式化显示时间
        self.url_more: list = []                    # 新时间比旧时间多的地址
        self.url_less: list = []                    # 新时间比旧时间少的地址
        self.content_url: dict = {}                 # 生成的内容对比可点击查看的链接
        self.final_args: dict = {}                  # 最终生成的对比参数结果
    
    def ding_talk(self, content: str = "") -> None:
        """
        发送预警函数
        :param content: 发送内容
        :return: None
        """
        ding_url = "https://oapi.dingtalk.com/robot/send?access_token=" \
                   "499590050800d5272d50385e2fdfd5a6699364db2e11e006bbb83d89f624bd81"       # 发送地址
        ding_json = {"msgtype": "text", "text": {"content": content},                       # 发送信息
                     "at": {"atMobiles": ["18501250875"], "isAtAll": True}}
        try:
            with requests.post(url=ding_url, json=ding_json, timeout=5) as res:             # 发送请求
                response = res.json()
        except Exception as ex:
            self.logger.info(f"发送预警失败(*>﹏<*)【{ex}】")
        else:
            self.logger.info(f"发送预警成功(*^__^*)【{response}】")
    
    def connect_mongo(self) -> None:
        """
        数据库连接
        :return: None
        """
        try:
            self.mongo_db = self.mongo_client['package']                        # 数据库
            self.mongo_parameter = self.mongo_db['parameter']                   # 参数表
            self.mongo_content = self.mongo_db['content']                       # 内容表
            self.mongo_time = self.mongo_db['time']                             # 时间表
        except Exception as ex:
            self.logger.info(f"连接数据库失败(*>﹏<*)【{ex}】")
        else:
            self.logger.info(f"连接数据库成功(*^__^*)【OK】")
    
    def get_time(self) -> bool:
        """
        获取时间戳列表
        :return: list
        """
        try:
            all_stamp = self.mongo_time.find_one({"type": "time"})
            if all_stamp:
                self.new_stamp = all_stamp['new_time']
                self.old_stamp = all_stamp['old_time']
            else:
                self.logger.info(f"获取时间戳数据为空(*>﹏<*)【{all_stamp}】")
        except Exception as ex:
            self.logger.info(f"获取时间戳失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"获取时间戳成功(*^__^*)【OK】")
            return True

    def get_data(self, status: str = "", get_stamp: int = 0) -> list:
        """
        获取数据结果集
        :param status:  获取类型 parameter获取参数时间戳，content获取内容时间戳
        :param get_stamp:
        :return: list
        """
        try:
            return_result = []
            if "parameter" in status:
                result = self.mongo_parameter.find({"scrape_time": get_stamp})          # 根据时间戳获取数据
            elif "content" in status:
                result = self.mongo_content.find({"scrape_time": get_stamp})
            else:
                result = []
                self.logger.info(f"获取数据类型错误(*>﹏<*)【{status}】")
            if result:
                for i in result:
                    return_result.append(i)
            else:
                self.logger.info(f"获取数据为空(*>﹏<*)【{result}】")
                return []
        except Exception as ex:
            self.logger.info(f"获取数据失败(*>﹏<*)【{ex}】")
            return []
        else:
            self.logger.info(f"获取数据成功(*^__^*)【OK】")
            return return_result

    def parse_time(self, get_stamp) -> str:
        """
        转化时间戳
        :param get_stamp: 时间戳
        :return: str
        """
        try:
            get_time = time.localtime(get_stamp)                                # 转换时间戳为时间类型
            return_time = time.strftime('%Y-%m-%d %H-%M-%S', get_time)          # 格式化时间
        except Exception as ex:
            self.logger.info(f"转化时间戳失败(*>﹏<*)【{ex}】")
            return ""
        else:
            self.logger.info(f"转化时间戳成功(*^__^*)【OK】")
            return return_time
    
    def write_file(self, path, content) -> None:
        """
        写入文件函数
        :param path: 文件地址
        :param content: 写入内容
        :return: None
        """
        try:
            with open(path, 'w', encoding='utf-8') as f:                        # 打开文件写入内容
                f.write(content)
        except Exception as ex:
            self.logger.info(f"写入文件失败(*>﹏<*)【{ex}】")
        else:
            self.logger.info(f"写入文件成功(*^__^*)【OK】")
        
    def read_file(self, path) -> list:
        """
        读取文件
        :param path: 文件地址
        :return: list
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:                        # 打开文件读取内容
                file = f.readlines()
        except Exception as ex:
            self.logger.info(f"读取文件失败(*>﹏<*)【{ex}】")
            return []
        else:
            self.logger.info(f"读取文件成功(*^__^*)【OK】")
            return file

    def compare_url(self) -> None:
        """
        比对基础连接地址
        :return: None
        """
        new_url = []                                                                # 获取最新一次时间链接集合
        old_url = []                                                                # 获取上一次时间链接集合
        self.connect_mongo()                                                        # 链接数据库
        self.get_time()                           # 获取时间戳
        # # # 获取格式化后的时间列表
        if self.new_stamp and self.old_stamp:
            self.new_time = self.parse_time(self.new_stamp)
            self.old_time = self.parse_time(self.old_stamp)
            # # # 获取新旧俩次结果
            new_result = self.get_data("parameter", self.new_stamp)
            old_result = self.get_data("parameter", self.old_stamp)
            # # # 提出新旧俩次链接集合
            if new_result and old_result:
                for n in new_result:
                    new_url.append(n['package_url'])
                for o in old_result:
                    old_url.append(o['package_url'])
                # # # 提出多余的新地址
                for i in new_url:
                    if i not in old_url:
                        self.url_more.append(i)
                # # # 提出多余的旧地址
                for j in old_url:
                    if j not in new_url:
                        self.url_less.append(j)

    def compare_detail(self, args_type: str = "", new_args: list=None, old_args: list=None) -> dict:
        """
        对比参数的细节
        :param args_type: 参数类型
        :param new_args: 新参数
        :param old_args: 旧参数
        :return: dict
        """
        more_detail, less_detail = [], []           # 声明多了的参数，少的参数
        try:
            for k in new_args:                          # 新参数比旧参数多
                if k not in old_args:
                    more_detail.append(k)
            for k in old_args:                          # 新参数比就参数少
                if k not in new_args:
                    less_detail.append(k)
        except Exception as ex:
            self.logger.info(ex)
            return {}
        else:
            if more_detail or less_detail:
                return {"type": args_type, "more": more_detail, "less": less_detail}
            else:
                return {}
                
    def compare_args(self) -> None:
        """
        比对相同地址参数
        :return: None
        """
        self.connect_mongo()                                                        # 链接数据库
        self.get_time()                           # 获取时间戳
        # # # 获取格式化后的时间列表
        if self.new_stamp and self.old_stamp:
            self.new_time = self.parse_time(self.new_stamp)
            self.old_time = self.parse_time(self.old_stamp)
            # # # 获取新旧俩次结果
            new_result = self.get_data("parameter", self.new_stamp)
            old_result = self.get_data("parameter", self.old_stamp)
            if new_result and old_result:                                           # 嵌套循环俩次结果对比
                for n in new_result:
                    for o in old_result:
                        if o['package_url'] == n['package_url']:                    # 对比新旧俩次相等的地址参数
                            all_args = []
                            # # # 对比新旧俩次地址参数
                            args = self.compare_detail("args", n['package_args'], o['package_args'])
                            if args:
                                all_args.append(args)
                            # # # 对比新旧俩次地址请求的headers
                            headers = self.compare_detail("headers", n['package_headers'], o['package_headers'])
                            if headers:
                                all_args.append(headers)
                            # # # 对比新旧俩次地址请求的cookies
                            cookies = self.compare_detail("cookies", n['package_cookies'], o['package_cookies'])
                            if cookies:
                                all_args.append(cookies)
                            # # # 对比新旧俩次回传的cookies
                            sets = self.compare_detail("set_cookies", n['package_sets'], o['package_sets'])
                            if sets:
                                all_args.append(sets)
                            self.final_args[o['package_url']] = all_args

    def compare_content(self) -> None:
        """
        比对js内容
        :return: None
        """
        self.connect_mongo()                                                        # 链接数据库
        self.get_time()                           # 获取时间戳
        # # # 获取格式化后的时间列表
        if self.new_stamp and self.old_stamp:
            self.new_time = self.parse_time(self.new_stamp)
            self.old_time = self.parse_time(self.old_stamp)
            # # # 获取新旧俩次结果
            new_result = self.get_data("content", self.new_stamp)
            old_result = self.get_data("content", self.old_stamp)
            if new_result and old_result:
                for i in new_result:                                                            # 嵌套循环比对俩次内容
                    for j in old_result:
                        if i['package_url'] == j['package_url']:
                            # 提出链接地址并转换格式区分地址保存
                            url = i['package_url'].split("/")                                   # 分割斜杠
                            url = url[-1].replace(".", "_")                                     # 转换点字符
                            sub_text1 = re.sub("\n|\t|\r|\s", "", i['package_text'])            # 清洗特殊字符
                            sub_text2 = re.sub("\n|\t|\r|\s", "", i['package_text'])
                            value = Levenshtein.ratio(sub_text1, sub_text2)                     # 计算莱文斯坦比
                            if value < 0.8:                                                     # 如果小于0.8预警
                                self.ding_talk(f"{i['package_url']}有变化")
                                js1 = jsbeautifier.beautify(sub_text1)                          # 格式化js代码
                                js2 = jsbeautifier.beautify(sub_text2)
                                self.write_file(f"static/{url}-1.txt", js1)                     # 写入文件保存
                                self.write_file(f"static/{url}-2.txt", js2)
                                file1 = self.read_file(f"static/{url}-1.txt")                   # 读取保存的文件
                                file2 = self.read_file(f"static/{url}-2.txt")
                                # # # 对比内容并生成html标签
                                d = difflib.HtmlDiff(4, 50)
                                q = d.make_file(file1, file2, "源内容", "比对内容", True, 5)
                                self.write_file(f'static/{url}.html', q)                        # 写入最终文件
                                self.content_url[i['package_url']] = f"{url}.html"              # 保存可点击的连接地址
            

