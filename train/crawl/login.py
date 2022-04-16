#! /usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
    written by pyleo
"""
import sys
sys.path.append('..')                                                                   # 导入环境当前目录
from apscheduler.schedulers.blocking import BlockingScheduler
from crawl.base import Base
import logging
import time
import pymongo
import socket
socket.setdefaulttimeout(5)                                                             # 全局socket超时


logger = logging.getLogger("selenium")                                                  # 基础日志
formatter = logging.Formatter('【%(asctime)s】%(message)s')                             # 日志格式
mongo_client = pymongo.MongoClient("mongodb://101.236.17.132:27017/")                   # 数据库驱动


class Login:
    """
    登录测试类
    """
    def __init__(self):
        self.logger = None                                                              # 日志声明
        self.base = Base()                                                              # 基础工具类
        self.main_window = None                                                         # 主窗口
        self.login_name = ""                                                            # 登录用户名
        self.login_pwd = ""                                                             # 登录用户密码
        self.time_minute = ""                                                           # 钉钉预警时间
        self.message = ""                                                               # 返回的失败原因
        # # # 查询的链接列表，包含下列字符串的连接地址会被请求内容并存储入库
        self.query_list: list = ["GetJS", "login_new"]
    
    def execute_process(self) -> None:
        """
        执行程序流程函数
        :return: None
        """
        t = time.time()
        self.time_minute = time.strftime('%Y-%m-%d %H:%M', time.localtime(t))
        self.base.set_headless(5)
        if self.login_control():
            time.sleep(2)
            self.base.connect_mongo()
            if self.base.set_time():
                log = self.base.get_log()
                if log:
                    self.base.insert_parameter(log)
                    self.base.insert_content()
        self.base.set_quit()
        self.base.set_shell("./kill_all.sh")

    def login_control(self, count: int = 0, max_count: int = 2) -> bool:
        """
        登录控制是否成功
        :return: bool
        """
        if self.base.set_url("https://kyfw.12306.cn/otn/resources/login.html"):             # 打开新版登录页面
            if self.base.show_elements("ul.login-hd>li", 3):
                if self.login_captcha():
                    return True
                else:
                    self.logger.info(f"(*>﹏<*)新版登录失败【走老版登录】")
                    if self.login_old():
                        return True
                    else:
                        self.logger.info(f"(*>﹏<*)老版登录失败【走扫码登录】")
                        if self.login_scan():
                            return True
                        else:
                            self.base.ding_talk(f"(*>﹏<*)新版登录扫码登录失败【请查看原因】【{self.time_minute}】")
                            return False
            else:
                self.logger.info(f"(*>﹏<*)新版登录未查询到选择按钮群【走强行登录】")
                if self.login_force("J-login", "#J-userName", "#J-password", "#J-login-error"):
                    return True
                else:
                    self.logger.info(f"(*>﹏<*)新版登录强行登录失败【走老版登录】")
                    if self.login_old():
                        return True
                    else:
                        self.base.ding_talk(f"(*>﹏<*)老版登录失败【请查看原因】【{self.time_minute}】")
                        return False
        else:
            if count < max_count:
                return self.login_control(count + 1, max_count)
            else:
                self.base.ding_talk(f"(*>﹏<*)重试打开3次新版登录页失败【请查看原因】【{self.time_minute}】")
                return False

    def login_force(self, button_id: str = "", username_css: str = "", password_css: str = "", error_css: str = "") -> bool:
        """
        强行登录流程
        :return: bool
        """
        if self.base.touch_element(f"#{button_id}"):  # 强行登录
            self.base.set_text(username_css, self.login_name)
            self.base.set_text(password_css, self.login_pwd)
            self.base.set_script(f"document.getElementById('{button_id}').click();")
            if self.base.hide_element(f"#{button_id}", 3):
                if self.base.wait_element("strong.welcome-name", 5):
                    if self.base.wait_element("div.mask"):
                        self.base.set_style("class", "mask", "none")
                    return True
            if self.base.wait_element(error_css):
                self.message = self.base.get_text(error_css)
                self.logger.info(self.message)
                return False
        return False

    def login_captcha(self, count: int = 0, max_count: int = 2) -> bool:
        """
        打码登录验证流程
        :return: bool
        """
        if self.base.set_url("https://kyfw.12306.cn/otn/resources/login.html"):             # 打开新版登录页面
            if self.base.wait_element("li.login-hd-account", 3):
                if self.base.set_click("li.login-hd-account"):                                                      # 点击打码按钮
                    if self.base.wait_element("#J-loginImg", 3):
                        src = self.base.get_value("#J-loginImg", "src")                                             # 获取图片地址
                        if src:
                            if "base64" in src:
                                self.logger.info("新版登录图片地址是base64,走来源切图")
                                image_flow = self.base.transform_source(src)
                                if image_flow:
                                    code_list = self.base.get_captcha(image_flow, 2)                                # 获取打码坐标
                                    if code_list:
                                        self.base.click_image(code_list, "img#J-loginImg.imgCode", y_increment=30)  # 点击打码图片
                                        if self.login_force("J-login", "#J-userName", "#J-password", "#J-login-error"):
                                            return True
                                        else:
                                            if count < max_count:
                                                return self.login_captcha(count + 1, max_count)
                            elif "http" in src:
                                self.logger.info("新版登录图片地址是http,走地址切图")
                                self.main_window = self.base.get_window()
                                if self.main_window:
                                    self.base.set_script("window.open('');")
                                    self.base.set_window(self.main_window)
                                    if self.base.set_url(src):
                                        if self.base.wait_element("img", 3):
                                            if self.base.crop_image("img", "img/test.png"):
                                                image_flow = self.base.transform_captcha(r"img/test.png")
                                                if image_flow:
                                                    code_list = self.base.get_captcha(image_flow, 2)                                # 获取打码坐标
                                                    self.base.set_close()
                                                    self.base.set_switch(self.main_window)
                                                    if code_list:
                                                        self.base.click_image(code_list, "img#J-loginImg.imgCode", y_increment=30)  # 点击打码图片
                                                        if self.login_force("J-login", "#J-userName", "#J-password", "#J-login-error"):
                                                            return True
                                                        else:
                                                            if count < max_count:
                                                                return self.login_captcha(count + 1, max_count)
                            else:
                                self.logger.info(f"新版登录打码图片是未知类型(*>﹏<*)")
        return False
        
    def login_scan(self) -> bool:
        """
        扫码登录验证流程
        :return: bool
        """
        if self.base.set_url("https://kyfw.12306.cn/otn/resources/login.html"):  # 打开新版登录页面
            if self.base.wait_element("#J-qrImg", 3):
                src = self.base.get_value("#J-qrImg", "src")                                            # 获取图片地址
                if src:
                    if "base64" in src:
                        self.logger.info("新版登录图片地址是base64,走来源切图")
                        image_flow = self.base.transform_source(src)
                        if image_flow:
                            if self.base.get_scan(image_flow, self.login_name, self.login_pwd):         # 请求扫码登录
                                if self.base.hide_element("li.login-hd-code", 3):
                                    if self.base.wait_element("strong.welcome-name", 8):                # 等待获取用户名
                                        if self.base.wait_element("div.mask"):
                                            self.base.set_style("class", "mask", "none")                # 消除蒙版
                                        return True
                    elif "http" in src:
                        self.logger.info("新版登录图片地址是http,走地址切图")
                        self.main_window = self.base.get_window()
                        if self.main_window:
                            self.base.set_script("window.open('');")
                            self.base.set_window(self.main_window)
                            if self.base.set_url(src):
                                if self.base.wait_element("img", 3):
                                    if self.base.crop_image("img", "img/test.png"):
                                        image_flow = self.base.transform_scan("img/test.png")
                                        if image_flow:
                                            self.base.set_close()
                                            self.base.set_switch(self.main_window)
                                            if self.base.get_scan(image_flow, self.login_name, self.login_pwd):     # 请求扫码登录
                                                if self.base.hide_element("li.login-hd-code", 3):
                                                    if self.base.wait_element("strong.welcome-name", 8):
                                                        if self.base.wait_element("div.mask"):
                                                            self.base.set_style("class", "mask", "none")            # 消除蒙版
                                                        return True
                    else:
                        self.logger.info(f"新版登录扫码图片是未知类型(*>﹏<*)")
        return False
            
    def login_old(self, count: int = 0, max_count: int = 2) -> bool:
        """
        老版登录是否成功
        :return: bool
        """
        if self.base.set_url("https://kyfw.12306.cn/otn/login/init"):  # 打开老版登录页面
            if self.base.wait_element("img.touclick-image", 3):                                 # 如果存在图片，获取地址
                src = self.base.get_value("img.touclick-image", "src")
                if src:
                    if "http" in src:
                        self.logger.info("老版登录图片地址是http,走地址切图")
                        self.main_window = self.base.get_window()
                        if self.main_window:
                            self.base.set_script("window.open('');")
                            self.base.set_window(self.main_window)
                            if self.base.set_url(src):
                                if self.base.wait_element("img", 3):
                                    if self.base.crop_image("img", "img/test.png"):
                                        image_flow = self.base.transform_captcha(r"img/test.png")
                                        if image_flow:
                                            code_list = self.base.get_captcha(image_flow, 2)            # 获取打码坐标
                                            self.base.set_close()                                       # 关闭打码页面
                                            self.base.set_switch(self.main_window)
                                            if code_list:
                                                self.base.click_image(code_list, "img.touclick-image", y_increment=30)  # 点击打码图片
                                                if self.login_force("loginSub", "#username", "#password", "#error_msgmypasscode1"):
                                                    return True
                                                if "验证码" in self.message:
                                                    if count < max_count:
                                                        return self.login_old(count + 1, max_count)
                    elif "base64" in src:
                        self.logger.info("老版登录图片地址是base64,走来源切图")
                        image_flow = self.base.transform_source(src)
                        if image_flow:
                            code_list = self.base.get_captcha(image_flow, 2)                                # 获取打码坐标
                            if code_list:
                                self.base.click_image(code_list, "img.touclick-image", y_increment=30)      # 点击打码图片
                                if self.login_force("loginSub", "#username", "#password", "#error_msgmypasscode1"):
                                    return True
                                else:
                                    if "验证码" in self.message:
                                        if count < max_count:
                                            return self.login_old(count + 1, max_count)
                    else:
                        self.logger.info(f"老版登录打码图片是未知类型(*>﹏<*)")
            else:
                self.logger.info(f"(*>﹏<*)老版登录获取图片失败【走强行登录】")
                if self.login_force("loginSub", "#username", "#password", "#error_msgmypasscode1"):
                    return True
        return False


if __name__ == '__main__':
    logger.setLevel(level=logging.INFO)  # 日志级别
    handler = logging.FileHandler("login.log")  # 日志地址
    # handler = logging.StreamHandler()
    handler.setFormatter(formatter)  # 日志格式化
    logger.addHandler(handler)  # 加载日志
    login = Login()
    login.base.logger, login.logger = logger, logger
    login.base.mongo_client = mongo_client
    login.login_name = "13084233827"
    login.login_pwd = "22In06jA8"
    scheduler = BlockingScheduler()
    scheduler.add_job(login.execute_process, 'cron', year="*", month="*", day="*", hour="6-23", minute="*/1")
    scheduler.start()
    # login.execute_process()
