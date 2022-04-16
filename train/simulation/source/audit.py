#! /usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
    written by pyleo
"""
import time


class Audit:
    """
    审核支付的流程类
    """
    def __init__(self):
        # ========================类要保持的数据========================
        self.logger = None                                              # 基础日志
        self.base = None                                                # 基础类
        self.main_window = None                                         # 主窗口
        self.save_cookies: str = ""                                     # 临时保存的cookie
        self.real_message: str = ""                                     # 真实返回的信息
        self.return_message: str = ""                                   # 返回接口的信息
        self.return_status: str = "false"                               # 返回结果状态
        self.proxy_status: str = "proxy_check"                          # 返回代理状态
        # ========================类要配置的数据========================
        self.redis_queue = None                                         # redis队列
        self.redis_result = None                                        # redis结果
        self.redis_machine = None                                       # redis机器
        self.machine_addr: str = ""
        self.proxy_failure = None
        self.proxy_addr: str = ""                                       # 代理服务器
        self.proxy_server: str = ""                                     # 代理地址
        self.proxy_auth: str = "yunku:123"                              # 代理认证
        self.interval = 2                                               # 打码间隔
        self.circulation = 4                                            # 循环次数
        self.page_search = 5                                            # 打开页面查找时间
        self.local_search = 5                                           # 点击按钮本页查找时间
        self.next_search = 10                                           # 点击按钮跳转查找时间
        self.audit_proxy = 0                                            # 是否启用代理
        self.cookie_way = 1                                             # 是否cookie登录方式 0 不开启  1 开启
        self.login_way = 1                                              # 登录方式  0 老版登录  1 新版自适应登录  2 打码登录  3 扫码登录
        self.time_out = 10                                              # 加载超时时间
        # ========================接口传来的数据========================
        self.key_label = ""
        self.ticket_code: str = ""                                         # 接口订单编号
        self.login_name: str = ""                                       # 登录账号
        self.login_pwd: str = ""                                        # 登录密码
        self.ticket_date: str = ""                                        # 起始站三字码
        self.cookie: str = ""                                           # 传入的cookie
        
    def parse_audit(self, data_dict=None) -> bool:
        """
        解析审核是否成功
        :param data_dict: 外部传入数据
        :return: bool
        """
        try:
            self.login_name = data_dict.get('username', '')
            self.login_pwd = data_dict.get('password', '')
            self.ticket_code = data_dict.get('ticket_code', '')
            self.ticket_date = data_dict.get('ticket_date', '')
            self.cookie = data_dict.get('cookie', '')
        except Exception as ex:
            self.logger.info(f"解析接口数据失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"解析接口数据成功(*^__^*)【{self.login_name}】【{self.login_pwd}】")
            return True
        
    def execute_process(self, data_dict=None):
        """
        审核支付流程函数
        :return: str
        """
        if self.parse_audit(data_dict):  # 解析数据
            self.get_config()  # 获取配置数据
            self.save_cookies = self.cookie  # 保存临时cookie
            if self.audit_proxy:  # 如果开启代理
                self.get_proxy()  # 获取代理
                self.base.set_proxy(self.proxy_server, self.proxy_auth)  # 设置代理
            if self.base.set_headless(self.proxy_server, self.time_out):  # 开启新会话
                if self.login_switch():  # 登录
                    if self.check_ticket():  # 获取支付链接
                        pass
        if self.audit_proxy:  # 判断是否开启代理
            self.proxy_status = "proxy_check"
            self.return_proxy()  # 归还代理
        self.return_result()  # 归还结果
        self.base.set_quit()
        self.base.set_shell("./kill_all.sh")

    def login_switch(self) -> bool:
        """
        登录主要切换流程
        :return: bool
        """
        if self.cookie_way:  # 如果cookie登录
            if self.login_cookie():
                return True
            else:
                if "网络忙" in self.real_message:  # 如果cookie登录失败
                    return False
                else:
                    if self.login_way == 0:  # 如果新版登录
                        return self.login_old()
                    elif self.login_way == 1:
                        return self.login_new()
                    elif self.login_way == 2:
                        if self.base.set_url("https://kyfw.12306.cn/otn/resources/login.html"):
                            if self.base.wait_element("li.login-hd-account", self.page_search):
                                return self.login_captcha()
                    elif self.login_way == 3:
                        if self.base.set_url("https://kyfw.12306.cn/otn/resources/login.html"):
                            if self.base.wait_element("li.login-hd-code", self.page_search):
                                return self.login_scan()
        else:
            if self.login_way == 0:  # 如果新版登录
                return self.login_old()
            elif self.login_way == 1:
                return self.login_new()
            elif self.login_way == 2:
                if self.base.set_url("https://kyfw.12306.cn/otn/resources/login.html"):
                    if self.base.wait_element("li.login-hd-account", self.page_search):
                        return self.login_captcha()
            elif self.login_way == 3:
                if self.base.set_url("https://kyfw.12306.cn/otn/resources/login.html"):
                    if self.base.touch_element("li.login-hd-code", self.page_search):
                        return self.login_scan()
        if self.base.check_error():
            self.real_message = "获取到错误的页面，网络忙"
            self.return_message = "审核支付失败"
            return False
        self.real_message = "页面打开失败或操作失败"
        self.return_message = "审核支付失败"
        return False

    def login_cookie(self) -> bool:
        """
        缓存登录主要流程
        :return: bool
        """
        if self.base.set_url("https://kyfw.12306.cn/otn/resources/login.html"):  # 代开登录页
            self.base.set_cookie(self.cookie)  # 设置cookie
            if self.base.set_url("https://kyfw.12306.cn/otn/view/index.html"):  # 刷新客户页
                if self.base.wait_element("strong.welcome-name", self.next_search):
                    if self.base.wait_element("div.mask"):  # 消除蒙版
                        self.base.set_style("class", "mask", "none")
                    return True
        self.base.delete_cookies()  # 如果失败先删除旧cookie
        if self.base.check_error():
            self.real_message = "获取到错误的页面，网络忙"
            self.return_message = "审核支付失败"
            return False
        self.real_message = "页面打开失败或操作失败"
        self.return_message = "审核支付失败"
        return False

    def login_old(self) -> bool:
        """
        老版登录是否成功
        :return: bool
        """
        if self.base.set_url("https://kyfw.12306.cn/otn/login/init"):  # 打开老版登录页面
            if self.base.touch_element("#loginSub", self.page_search):  # 登录按钮是否可按
                if not self.base.wait_element("img.touclick-image", self.page_search):  # 如果不存在图片，强行登录
                    self.base.set_text("#username", self.login_name)
                    self.base.set_text("#password", self.login_pwd)
                    self.base.set_click("#loginSub")
                    if self.base.hide_element("#loginSub", self.local_search):
                        if self.base.wait_element("strong.welcome-name", self.next_search):
                            if self.base.wait_element("div.mask"):
                                self.base.set_style("class", "mask", "none")
                            return True
                else:  # 如果存在图片打码登录
                    src = self.base.get_value("img.touclick-image", "src")
                    if src:
                        self.main_window = self.base.get_window()  # 保存辅助页面，打开新的页面
                        if self.main_window:
                            self.base.set_script("window.open('');")
                            self.base.set_window(self.main_window)  # 切换新页面，保存图骗
                            if self.base.set_url(src):
                                if self.base.wait_element("img", self.page_search):
                                    self.base.crop_image("img", "img/test.png")
                                    image_flow = self.base.transform_captcha(r"img/test.png")
                                    code_list = self.base.get_captcha(image_flow, self.interval)  # 获取打码坐标
                                    self.base.set_close()
                                    self.base.set_switch(self.main_window)
                                    if code_list:
                                        self.base.set_text("#username", self.login_name)
                                        self.base.set_text("#password", self.login_pwd)
                                        self.base.click_image(code_list, "img.touclick-image", y_increment=30)  # 点击打码图片
                                        self.base.set_click("#loginSub")
                                        if self.base.hide_element("#loginSub", self.local_search):
                                            if self.base.wait_element("strong.welcome-name", self.next_search):
                                                if self.base.wait_element("div.mask"):
                                                    self.base.set_style("class", "mask", "none")
                                                return True
        if self.base.check_error():
            self.real_message = "获取到错误的页面，网络忙"
            self.return_message = "审核支付失败"
            return False
        self.real_message = "页面打开失败或操作失败"
        self.return_message = "审核支付失败"
        return False

    def login_new(self) -> bool:
        """
        新版登录主要流程
        :return:
        """
        if self.base.set_url("https://kyfw.12306.cn/otn/resources/login.html"):  # 打开新版登录页面
            if self.base.show_elements("ul.login-hd>li", self.page_search):  # 查询按钮群
                login_class = self.base.find_elements("ul.login-hd>li", "class")
                if login_class:
                    if "login-hd-account" in login_class:  # 打码登录
                        return self.login_captcha()
                    elif "login-hd-code" in login_class:  # 扫码登录
                        return self.login_scan()
                    else:
                        self.logger.info(f"没有找到登录标签(*>﹏<*)【{login_class}】")
            if self.base.touch_element("#J-login"):  # 强行登录
                self.base.set_text("#J-userName", self.login_name)
                self.base.set_text("#J-password", self.login_pwd)
                self.base.set_click("#J-login")
                if self.base.hide_element("#J-login", self.local_search):
                    if self.base.wait_element("strong.welcome-name", self.next_search):
                        if self.base.wait_element("div.mask"):
                            self.base.set_style("class", "mask", "none")
                        return True
        if self.base.check_error():
            self.real_message = "获取到错误的页面，网络忙"
            self.return_message = "审核支付失败"
            return False
        self.real_message = "页面打开失败或操作失败"
        self.return_message = "审核支付失败"
        return False

    def login_scan(self) -> bool:
        """
        扫码登录验证流程
        :return: bool
        """
        self.base.set_click("li.login-hd-code")
        if self.base.wait_element("#J-qrImg", self.local_search):
            src = self.base.get_value("#J-qrImg", "src")  # 获取图片地址
            if src:
                self.main_window = self.base.get_window()
                if self.main_window:
                    self.base.set_script("window.open('');")
                    self.base.set_window(self.main_window)
                if self.base.set_url(src):
                    if self.base.wait_element("img", self.page_search):
                        self.base.crop_image("img", "img/test.png")
                        image_flow = self.base.transform_scan("img/test.png")
                        self.base.set_close()
                        self.base.set_switch(self.main_window)
                        if self.base.get_scan(image_flow, self.login_name, self.login_pwd):  # 获取打码坐标
                            if self.base.hide_element("li.login-hd-code", self.local_search):
                                if self.base.wait_element("strong.welcome-name", self.next_search):
                                    if self.base.wait_element("div.mask"):
                                        self.base.set_style("class", "mask", "none")  # 消除蒙版
                                        return True
        if self.base.check_error():
            self.real_message = "获取到错误的页面，网络忙"
            self.return_message = "审核支付失败"
            return False
        self.real_message = "页面打开失败或操作失败"
        self.return_message = "审核支付失败"
        return False

    def login_captcha(self) -> bool:
        """
        打码登录验证流程
        :return: bool
        """
        self.base.set_click("li.login-hd-account")
        if self.base.wait_element("#J-loginImg", self.local_search):
            src = self.base.get_value("#J-loginImg", "src")  # 获取图片地址
            if src:
                self.main_window = self.base.get_window()
                if self.main_window:
                    self.base.set_script("window.open('');")
                    self.base.set_window(self.main_window)
                if self.base.set_url(src):
                    if self.base.wait_element("img", self.page_search):
                        self.base.crop_image("img", "img/test.png")
                        image_flow = self.base.transform_captcha(r"img/test.png")
                        code_list = self.base.get_captcha(image_flow, self.interval)  # 获取打码坐标
                        self.base.set_close()
                        self.base.set_switch(self.main_window)
                        if code_list:
                            self.base.click_image(code_list, "img#J-loginImg.imgCode", y_increment=30)  # 点击打码图片
                            self.base.set_text("#J-userName", self.login_name)
                            self.base.set_text("#J-password", self.login_pwd)  # 输入文本
                            self.base.set_click("#J-login")
                            if self.base.hide_element("#J-login", self.local_search):
                                if self.base.wait_element("strong.welcome-name", self.next_search):
                                    if self.base.wait_element("div.mask"):
                                        self.base.set_style("class", "mask", "none")
                                    return True
        if self.base.check_error():
            self.real_message = "获取到错误的页面，网络忙"
            self.return_message = "审核支付失败"
            return False
        self.real_message = "页面打开失败或操作失败"
        self.return_message = "审核支付失败"
        return False

    def check_ticket(self) -> bool:
        """
        审核订单支付流程
        :return: bool
        """
        if self.base.set_url("https://kyfw.12306.cn/otn/view/train_order.html"):  # 打开我的未完成
            if self.base.wait_element("#order_tab li[data-type='0']", self.page_search):  # 点击tab
                if self.base.wait_element("div.mask"):
                    self.base.set_style("class", "mask", "none")
                self.base.set_click("#order_tab li[data-type='0']")
                if self.base.wait_element("#searchNoTrip", self.local_search):  # 查询按钮
                    if self.base.wait_element("div.mask"):
                        self.base.set_style("class", "mask", "none")
                    self.base.set_script(f'document.getElementById("noTripFromDate").value="{self.ticket_date}";')
                    self.base.set_script(f'document.getElementById("noTripName").value="{self.ticket_code}";')
                    self.base.set_click("#searchNoTrip")  # 查询
                    if self.base.wait_element("#not_travel", self.local_search):
                        if self.base.wait_element("div.mask"):
                            self.base.set_style("class", "mask", "none")
                        if self.base.wait_element(f"#query_order_form_{self.ticket_code}", self.local_search):
                            self.save_cookies = self.base.return_cookies()
                            self.real_message = "已支付,可以出票"
                            self.return_message = self.real_message
                            return True
                        else:
                            if self.base.show_elements("#not_travel div.empty-txt>p"):
                                self.real_message = self.base.get_text("#not_travel div.empty-txt>p")
                                self.return_message = self.real_message
                                return False
        if self.base.check_error():
            self.real_message = "获取到错误的页面，网络忙"
            self.return_message = "审核支付失败"
            return False
        self.real_message = "页面打开失败或操作失败"
        self.return_message = "审核支付失败"
        return False

    def return_data(self):
        """
        回调接口最终格式
        :return: str
        """
        # # # 共有参数
        result_data = {
            "msg": self.return_message, "cookie": self.save_cookies
        }
        json_return = self.base.parse_dump(result_data)
        return json_return

    def get_config(self) -> bool:
        """
        获取配置是否成功
        :return: bool
        """
        try:
            config_data = self.redis_queue.hgetall("config_name")  # 获取配置
        except Exception as ex:
            self.logger.info(f"获取配置数据失败(*>﹏<*)【{ex}】")
            return False
        else:
            if config_data:
                self.interval = int(config_data.get("interval", 2))
                self.page_search = int(config_data.get("page_search", 5))
                self.local_search = int(config_data.get("local_search", 5))
                self.next_search = int(config_data.get("next_search", 10))
                self.audit_proxy = int(config_data.get("audit_proxy", 1))
                self.login_way = int(config_data.get("login_way", 1))
                self.cookie_way = int(config_data.get("cookie_way", 1))
                self.time_out = int(config_data.get("time_out", 10))
                self.logger.info("获取配置数据成功(*^__^*)【OK】")
                return True
            else:
                self.logger.info("获取配置数据为空(*>﹏<*)【NO】")
                return False

    def get_proxy(self) -> bool:
        """
        获取代理是否成功
        :return: bool
        """
        try:
            self.proxy_addr = self.redis_queue.rpop("proxy_leisure")
        except Exception as ex:
            self.logger.info(f"代理队列获取失败(*>﹏<*)【{ex}】")
            return False
        else:
            if not self.proxy_addr:
                self.logger.info("代理队列获取为空(*>﹏<*)【NO】")
                return False
            else:
                try:
                    proxy_data = self.redis_machine.hgetall(self.proxy_addr)
                except Exception as ex:
                    self.logger.info(f"代理获取数据失败(*>﹏<*)【{ex}】")
                    return False
                else:
                    if proxy_data:
                        self.proxy_server = proxy_data.get('proxy_server', '')
                        self.proxy_auth = proxy_data.get('proxy_auth', 'yunku:123')
                        self.logger.info(f"代理获取数据成功(*^__^*)【{self.proxy_server}】【{self.proxy_auth}】")
                        return True
                    else:
                        self.logger.info(f"代理获取数据为空(*>﹏<*)【{self.proxy_addr}】")
                        return False

    def return_proxy(self) -> bool:
        """
        归还代理是否成功
        :return: bool
        """
        try:
            self.redis_queue.lpush(self.proxy_status, self.proxy_addr)
        except Exception as ex:
            self.logger.info(f"归还代理数据失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"归还代理数据成功(*^__^*)【{self.proxy_status}】【{self.proxy_addr}】")
            return True

    def return_result(self) -> bool:
        """
        归还结果是否成功
        :return: bool
        """
        try:
            send_data = {"ip": self.machine_addr, "data": self.return_data(),
                         "proxy": self.proxy_addr, "circulation": 0,
                         "real_message": self.real_message, "return_message": self.return_message}
            self.redis_result.hmset(self.key_label, send_data)
            self.redis_queue.lpush("machines", self.machine_addr)
        except Exception as ex:
            self.logger.info(f"归还结果数据失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"归还结果数据成功(*^__^*)【{self.key_label}】")
            return True
