#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@@..> net tools
@@..> package utils
@@..> author pyleo <lihao@372163.com>
"""
#######################################################################################
# @@..> base import
from dataclasses import dataclass, field
# @@..> NetAct
from requests import request, Session
from requests.models import Response
from requests.utils import dict_from_cookiejar
from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from random import sample


#######################################################################################
@dataclass
class NetAct:
    """
    [net object]
    """
    __logger: any = field(default_factory=bool)
    __normal: request = field(default_factory=bool)
    __session: Session = field(default_factory=bool)
    __response: Response = field(default_factory=bool)
    __code: int = field(default_factory=int)
    __page: any = field(default_factory=bool)
    # custom args
    __url: str = field(default_factory=str)
    __headers: dict = field(default_factory=dict)
    __params: tuple = field(default_factory=tuple)
    __posts: any = field(default_factory=bool)
    __proxies: dict = field(default_factory=dict)
    __timeout: int = field(default_factory=int)

    @property
    def logger(self):
        return self.__logger

    @logger.setter
    def logger(self, value):
        self.__logger = value

    @property
    def normal(self):
        self.__normal = request
        return self.__normal

    @property
    def session(self):
        return self.__session

    @property
    def response(self):
        return self.__response

    @property
    def code(self):
        return self.__code

    @property
    def page(self):
        return self.__page

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, value):
        self.__url = value

    @property
    def headers(self):
        return self.__headers

    @headers.setter
    def headers(self, value):
        self.__headers = value

    @property
    def params(self):
        return self.__params

    @params.setter
    def params(self, value):
        self.__params = value

    @property
    def posts(self):
        return self.__posts

    @posts.setter
    def posts(self, value):
        self.__posts = value

    @property
    def proxies(self):
        return self.__proxies

    @proxies.setter
    def proxies(self, value):
        self.__proxies = value

    @property
    def timeout(self):
        return self.__timeout

    @timeout.setter
    def timeout(self, value):
        self.__timeout = value

    def set_session(self, is_proxy: bool = False, address: str = "") -> bool:
        """
        [start session]

        Args:
            is_proxy (bool, optional): [if set proxy or not]. Defaults to False.
            address (str, optional): [http://127.0.0.1:8000]. Defaults to nothing.

        Returns:
            bool: [nothing.]
        """
        # @@..! eliminate ssl alarm.
        disable_warnings(InsecureRequestWarning)
        if isinstance(is_proxy, bool) and isinstance(address, str):
            self.__session = Session()
            self.__session.keep_alive = False
            self.__session.max_redirects = 3
            if is_proxy:
                self.__proxies = {"https": address, "http": address}
            else:
                self.__proxies = {}
            return True
        else:
            self.__logger.info(f"设置session运行失败(*>﹏<*)【{is_proxy}/{address}】")
            return False

    def set_close(self) -> bool:
        """
        [close the session]

        Returns:
            bool: [nothing.]
        """
        if isinstance(self.__session, Session):
            if isinstance(self.__response, Response):
                self.__response.close()

            self.__session.close()
            return True
        else:
            self.__logger.info(f"设置session关闭失败(*>﹏<*)【{self.session}】")
            return False

    def set_cookie(self, cookie_dict: dict = None, is_domain: bool = False) -> None:
        """
        [set cookie dict with no domain]

        Args:
            cookie_dict (dict, optional): [key/value]. Defaults to None.
            is_domain (bool, optional): [nothing]. Defaults to False.

        Returns:
            None: [nothing.]
        """
        if isinstance(self.__session, Session) \
                and isinstance(cookie_dict, dict) and isinstance(is_domain, bool):
            try:
                if is_domain:
                    cookie_name = cookie_dict.get('name', "")
                    cookie_value = cookie_dict.get('value', "")
                    cookie_domain = cookie_dict.get('domain', "")
                    cookie_path = cookie_dict.get('path', "")
                    self.__session.cookies.set(
                        name=cookie_name, value=cookie_value,
                        domain=cookie_domain, path=cookie_path)
                else:
                    for k, v in cookie_dict.items():
                        self.__session.cookies.set(name=k, value=v)

                return True
            except Exception as ex:
                self.__logger.info(f"设置cookie缓存失败(*>﹏<*)【{ex}】")
                return False
        else:
            self.__logger.info(f"设置cookie缓存失败(*>﹏<*)【{is_domain}】")
            return False

    def get_cookie(self) -> dict:
        """
        [get cookie]

        Returns:
            dict: [nothing.]
        """
        if isinstance(self.__session, Session):
            return dict_from_cookiejar(self.__session.cookies)
        else:
            return {}

    def set_clear(self) -> bool:
        """
        [clear the cookie]

        Returns:
            bool: [nothing.]
        """
        try:
            self.__session.cookies.clear()
            return True
        except Exception as ex:
            self.__logger.info(f"清除cookie缓存失败(*>﹏<*)【{ex}】")
            return False

    def get_response(self, req_type: str = "", data_type: str = "",
                     is_redirect: bool = False, encoding: str = "utf-8") -> bool:
        """
        [request method]

        Args:
            req_type (str, optional): [get/post..]. Defaults to nothing.
            data_type (str, optional): [json/data..]. Defaults to nothing.
            is_redirect (bool, optional): [if jump or not]. Defaults to False.
            encoding (str, optional): [utf-8/iso-8859-1]. Defaults to utf-8.

        Returns:
            bool: [nothing.]
        """
        if isinstance(self.__session, Session) and isinstance(req_type, str) \
                and isinstance(data_type, str) and isinstance(is_redirect, bool) \
                and isinstance(encoding, str):
            pass
        else:
            self.__logger.info("获取response数据失败(*>﹏<*)【type】")
            self.__response = None
            return False

        try:
            session_params = {
                "url": self.__url, "headers": self.__headers,
                "params": self.__params, "proxies": self.__proxies,
                "allow_redirects": is_redirect, "timeout": self.__timeout,
                "verify": False, "stream": False
            }

            if req_type in ("post", "put", "patch"):
                if data_type == "json":
                    session_params.update({"json": self.__posts})
                elif data_type == "data":
                    session_params.update({"data": self.__posts})
                elif data_type == "files":
                    session_params.update({"files": self.__posts})
                else:
                    self.__response = None
                    self.__logger.info("获取response数据失败(*>﹏<*)【data_type】")
                    return False

            if req_type == "get":
                with self.__session.get(**session_params) as self.__response:
                    pass
            elif req_type == "options":
                with self.__session.options(**session_params) as self.__response:
                    pass
            elif req_type == "head":
                with self.__session.head(**session_params) as self.__response:
                    pass
            elif req_type == "delete":
                with self.__session.delete(**session_params) as self.__response:
                    pass
            elif req_type == "post":
                with self.__session.post(**session_params) as self.__response:
                    pass
            elif req_type == "put":
                with self.__session.put(**session_params) as self.__response:
                    pass
            elif req_type == "patch":
                with self.__session.patch(**session_params) as self.__response:
                    pass
            else:
                self.__response = None
                self.__logger.info("获取response数据失败(*>﹏<*)【req_type】")
                return False

            self.__response.encoding = encoding
            self.__code = self.__response.status_code
            return True

        except Exception as ex:
            self.__response = None
            self.__logger.info(f"获取response数据失败(*>﹏<*)【{self.__url}】")
            self.__logger.info(f"【{req_type}/{data_type}/{is_redirect}】")
            self.__logger.info(f"获取response失败原因(*>﹏<*)【{ex}】")
            return False

    def get_page(self, data_type: str = "", is_check: bool = True,
                 code: int = 200, is_log: bool = True) -> bool:
        """
        [parse the data]

        Args:
            data_type (str, optional): [json/data..]. Defaults to nothing.
            is_check (bool, optional): [if check code or not]. Defaults to True.
            code (int, optional): [http status code]. Defaults to 200.
            is_log (bool, optional): [if print log or not]. Defaults to True.

        Returns:
            bool: [nothing.]
        """
        if isinstance(self.__response, Response) and isinstance(data_type, str) \
                and isinstance(is_check, bool) and isinstance(code, int):
            pass
        else:
            self.__page = None
            self.__logger.info("获取page页面失败(*>﹏<*)【type】")
            return False

        try:
            if is_check:
                if code != self.__code:
                    self.__page = None
                    self.__logger.info(f"获取page编码失败(*>﹏<*)【{self.__url}】")
                    self.__logger.info(f"【{code}|{self.__code}】")
                    return False

            if data_type == "json":
                self.__page = self.__response.json()
            elif data_type == "text":
                self.__page = self.__response.text
            elif data_type == "content":
                self.__page = self.__response.content
            else:
                self.__page = None
                self.__logger.info("获取page页面失败(*>﹏<*)【data_type】")
                return False

            if is_log:
                self.__logger.info(f"获取page页面成功(*^__^*)【{self.__url}】")
            return True
        except Exception as ex:
            self.__page = None
            self.__logger.info(f"获取page页面失败(*>﹏<*)【{self.__url}】")
            self.__logger.info(f"【{data_type}/{is_check}/{code}】")
            self.__logger.info(f"获取page失败原因(*>﹏<*)【{ex}】")
            return False

    def set_header(self, version: str = "chrome") -> tuple:
        """
        [build the header, if none to random]

        Args:
            version (str, optional): [json/data..]. Defaults to Chrome.

        Returns:
            tuple: [nothing.]
        """
        if not isinstance(version, str):
            version = "chrome"
        # # # version dict
        defaults = {
            "flask": {
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "close",
                'Content-Encoding': 'gzip',
                'Content-Type': 'application/json;charset=UTF-8'
            },
            "xiaomi": {
                "User-Agent": "Mozilla/5.0 (Linux; Android 9; Redmi Note 8 "
                              "Build/PKQ1.190616.001; wv) AppleWebKit/537.36 "
                              "(KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 "
                              "Mobile Safari/537.36 T7/12.23 swan/2.35.0 "
                              "swan-baiduboxapp/12.23.0.11 baiduboxapp/12.23.0.11 "
                              "(Baidu; P1 9)",
                "Accept-Encoding": "gzip",
                "Connection": "keep-alive",
            },
            "edge": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.66",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                          "image/webp,image/apng,*/*;q=0.8,"
                          "application/signed-exchange;v=b3;q=0.9",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            },
            "chrome": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/96.0.4664.45 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                          "image/avif,image/webp,image/apng,*/*;q=0.8,"
                          "application/signed-exchange;v=b3;q=0.9",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            },
            "chronium": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/71.0.3542.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                          "image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            },
            "firefox": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) "
                              "Gecko/20100101 Firefox/81.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                          "image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;"
                                   "q=0.3,en;q=0.2",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            },
            "ubrowser": {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.3; WOW64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/55.0.2883.87 UBrowser/6.2.4098.3 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                          "image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            },
            "huawei": {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; YAL-AL10; "
                              "HMSCore 5.0.3.304; GMSCore 20.15.16) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/83.0.4103.106 HuaweiBrowser/11.0.3.302 Mobile "
                              "Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;"
                          "q=0.9,image/webp,image/apng,*/*;"
                          "q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Accept-Language": "zh-CN,zh;q=0.9,en-CN;q=0.8,en-US;q=0.7,en;q=0.6",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            },
        }

        # @@..> If the corresponding version cannot be found, random one.
        version_dict = defaults.get(version)
        if version_dict:
            user_agent = version_dict.get("User-Agent")
            return_header = version_dict
        else:
            key = sample(defaults.keys(), 1)
            version = key[0]
            version_dict = defaults.get(version)
            user_agent = version_dict.get("User-Agent")
            return_header = version_dict

        return version, user_agent, return_header
