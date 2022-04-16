#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> base ruler
@@..> package tasks.rules
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> base import
from dataclasses import dataclass, field
# @@..> import utils
from utils.base_tools import BaseAct, LogAct
from utils.str_tools import StrAct, UrlAct, DomAct, EncryptAct
from utils.json_tools import JsonAct
from utils.num_tools import NumAct, TimeAct
from utils.net_tools import NetAct
from utils.data_tools import DataAct


#######################################################################################
@dataclass
class BaseWorker:
    """
    [define base]
    """
    # # # base define
    logger: any = field(default_factory=bool)
    handler: any = field(default_factory=bool)
    net: any = field(default_factory=bool)
    # # # process define
    header_version: str = field(default_factory=str)        # 初始化版本
    user_agent: str = field(default_factory=str)            # 初始化UA
    init_header: dict = field(default_factory=dict)         # 初始化请求头。
    url_head: str = field(default_factory=str)              # 链接头
    url_domain: str = field(default_factory=str)            # 链接域名
    url_path: str = field(default_factory=str)              # 链接路径
    url_dict: dict = field(default_factory=dict)            # 链接参数
    blacklist: set = field(default_factory=set)             # 域名黑名单
    whitelist: set = field(default_factory=set)             # 域名白名单
    # # # interface define
    taskId: str = field(default_factory=str)                # 任务编号
    envMap: str = field(default_factory=str)                # 任务编号
    scrapeUrl: str = field(default_factory=str)             # 抓取链接
    homeUrl: str = field(default_factory=str)               # 展示链接
    username: str = field(default_factory=str)              # 用户名
    password: str = field(default_factory=str)              # 密码
    cookies: dict = field(default_factory=dict)             # cookie
    # # # tool type 1审核/2快速/3账号/4更新
    toolType: int = field(default_factory=int)
    # # # flow type 1主页(isUrls)/2作品页(isLast)
    flowType: int = field(default_factory=int)
    # # # call back
    user_id: str = field(default_factory=str)               # 主页ID
    work_id: str = field(default_factory=str)               # 作品ID
    isUrls: int = field(default_factory=int)                # 作品是否是链接
    isLast: int = field(default_factory=int)                # 作品是否是最终
    profileBase: dict = field(default_factory=dict)         # web 基础数据
    profileCounts: dict = field(default_factory=dict)       # web 基础计数
    workBase: dict = field(default_factory=dict)            # web 作品数据
    workList: list[str] = field(default_factory=list)       # web 作品数据
    workUrls: list[str] = field(default_factory=list)       # web 作品链接
    callback_data: dict = field(default_factory=dict)       # 回调数据

    def init_assignment(self, process_dict: dict = None) -> bool:
        """
        [init]

        Args:
            process_dict (dict, optional): [interface args]. Defaults to None.

        Returns:
            bool: [nothing.]
        """
        # # # Parse the detail
        self.taskId = process_dict.get('_id')
        self.envMap = process_dict.get('envMap')
        self.scrapeUrl = process_dict.get('scrapeUrl')
        self.username = process_dict.get('username')
        self.password = process_dict.get('password')
        self.cookies = process_dict.get('cookies')
        self.toolType = process_dict.get("toolType")
        self.flowType = process_dict.get("flowType")
        self.isLast = process_dict.get("isLast")
        # # # define
        log_path = f"logs/{self.taskId}.log"
        # self.logger, self.handler = LogAct.init_log(log_path, False)
        self.logger, self.handler = LogAct.init_log(log_path)
        self.net = NetAct()
        self.net.logger = self.logger
        self.data = DataAct()
        self.data.logger = self.logger

        JsonAct.logger = self.logger
        StrAct.logger = self.logger
        UrlAct.logger = self.logger
        DomAct.logger = self.logger
        EncryptAct.logger = self.logger
        NumAct.logger = self.logger
        TimeAct.logger = self.logger
        self.logger.info(process_dict)
        return True

    def process_main(self, process_dict: dict = None) -> dict:
        """
        [main]

        Args:
            process_dict (dict, optional): [interface args]. Defaults to None.

        Returns:
            dict: [nothing.]
        """
        if not self.init_assignment(process_dict):
            LogAct.unload_log(self.logger, self.handler)
            return {}
        # # # 启动爬虫，建立header。
        self.net.set_session()
        # self.net.set_session(True, "http://127.0.0.1:8888")
        self.net.timeout = 10
        self.header_version, self.user_agent, self.init_header = \
            self.net.set_header()
        # # # 主体流程。
        if self.process_index():
            self.logger.info(self.callback_data)
            self.net.set_close()
            LogAct.unload_log(self.logger, self.handler)
            return self.callback_data
        else:
            self.net.set_close()
            LogAct.unload_log(self.logger, self.handler)
            return {}

    def process_verify(self, verify_url: str = "") -> bool:
        """
        [verify domain]

        Args:
            verify_url (str, optional): [url]. Defaults to nothing.

        Returns:
            bool: [nothing.]
        """
        # 检查链接是否合格
        if not UrlAct.parse_check(verify_url):
            return True
        self.url_head, self.url_domain, self.url_path, self.url_dict = \
            UrlAct.parse_url(verify_url)
        if not self.url_path:
            self.logger.info(f"非法path路径(*>﹏<*)【{self.scrapeUrl}】")
            return True
        # 检查域名是否合格
        self.url_domain = self.url_domain.lower()
        if StrAct.parse_include(self.url_domain, self.blacklist):
            self.logger.info(f"非法domain黑名(*>﹏<*)【{self.scrapeUrl}】")
            return True
        if not StrAct.parse_include(self.url_domain, self.whitelist):
            self.logger.info(f"非法domain白名(*>﹏<*)【{self.scrapeUrl}】")
            return True
        # 返回False不操作
        if self.url_head == "http":
            verify_url = StrAct.parse_replace(verify_url, "http://", "https://")
        return False

    def process_return(self) -> None:
        """
        [return data]

        Returns:
            None: [nothing.]
        """
        self.callback_data["_id"] = self.taskId
        self.callback_data['envMap'] = self.envMap
        self.callback_data['toolType'] = self.toolType
        self.callback_data['flowType'] = self.flowType
        self.callback_data['isUrls'] = self.isUrls
        self.callback_data['isLast'] = self.isLast
        self.callback_data["scrapeUrl"] = self.scrapeUrl
        self.callback_data["homeUrl"] = self.homeUrl
        self.callback_data['profileBase'] = self.profileBase
        self.callback_data['profileCounts'] = self.profileCounts
        self.callback_data['workBase'] = self.workBase
        self.callback_data['workList'] = self.workList
        self.callback_data['workUrls'] = self.workUrls
        self.callback_data['updateDate'] = ""

    def process_index(self) -> bool:
        """
        [index flow]
        1 profile
            tool 1 审核
            tool 2 快速 -> isUrls
            tool 3 账号 -> isUrls
            tool 4 更新 -> isUrls
        2 work
            tool 1 作品
            tool 2 快速 -> isLast
            tool 4 更新 -> isLast

        Returns:
            bool: [nothing.]
        """
        pass

    def process_work(self) -> bool:
        """
        [work flow]

        Returns:
            bool: [nothing.]
        """
        pass

    def process_profile(self) -> bool:
        """
        [profile flow]

        Returns:
            bool: [nothing.]
        """
        pass

    def get_work(self) -> bool:
        """
        [get work data]

        Returns:
            bool: [nothing.]
        """
        pass

    def get_profile(self) -> bool:
        """
        [get profile data]

        Returns:
            bool: [nothing.]
        """
        pass

    def get_return(self, plat_id, is_use):
        """
        [set return data]

        Returns:
            any: [nothing.]
        """
        today_date = TimeAct.format_now()
        today_string = str(today_date.date())
        self.process_return()
        self.callback_data["platId"] = plat_id
        self.callback_data['isUse'] = is_use
        self.callback_data['updateDate'] = today_string

    def regex_first(self, source_data, regex_syntax):
        """
        [get regex first value]

        Returns:
            any: [nothing.]
        """
        value_gen = StrAct.parse_regex(source_data, regex_syntax)
        value, value_gen = BaseAct.parse_generator(value_gen)
        return value

    def json_first(self, source_data, path_syntax, is_default):
        """
        [get json first value]

        Returns:
            any: [nothing.]
        """
        value_gen = JsonAct.parse_json(source_data, path_syntax)
        value, value_gen = BaseAct.parse_generator(value_gen)
        if is_default:
            if value is False or value is None:
                return ""

        return value

    def json_number(self, source_data, path_syntax, is_default):
        """
        [get json int]

        Returns:
            any: [nothing.]
        """
        value = self.json_first(source_data, path_syntax, is_default)
        if value is False or value is None:
            if is_default:
                value = ""
            else:
                return False

        int_gen = StrAct.parse_integer(value)
        int_value, int_gen = BaseAct.parse_generator(int_gen)
        if is_default:
            if int_value is False or int_value is None:
                return 0

        return int_value


