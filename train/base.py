#! /usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
    written by pyleo
"""
# # # selenium
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
from urllib3.exceptions import ReadTimeoutError
# # # other
from PIL import Image
from io import BytesIO
from urllib import request, parse
from pyzbar import pyzbar
import requests
import re
import json
import hashlib
import base64
import time
import os


class Base:
    """
    浏览器基础方法类
    """
    def __init__(self):
        self.logger = None                          # 类基础日志
        self.opts = webdriver.ChromeOptions()       # 浏览器配置
        self.caps = None                            # 浏览器技能
        self.driver = None                          # 浏览器驱动
        self.mongo_client = None                    # 数据库驱动
        self.mongo_db = None                        # mongo数据库
        self.mongo_parameter = None                 # mongo参数表
        self.mongo_content = None                   # mongo内容表
        self.mongo_time = None                      # mongo时间表
        self.scrape_time = None                     # 插入时间戳
    
    def set_headless(self, time_out: int = 5) -> bool:
        """
        启动无头是否成功
        :param time_out: 超时时间
        :return: bool
        """
        try:
            self.opts.headless = True                                                   # 启用无头
            self.opts.add_argument('--no-sandbox')                                      # 无头下禁用沙盒
            self.opts.add_argument('--disable-dev-tools')                               # 无头下禁用dev
            self.opts.add_argument('--disable-gpu')                                     # 禁用gpu加速
            self.opts.add_argument('--disable-infobars')                                # 禁用提示
            self.opts.add_argument('--ignore-certificate-errors')                       # 忽略证书错误
            self.opts.add_argument('--allow-running-insecure-content')                  # 与上同步使用
            self.opts.add_argument('--disable-crash-reporter')                          # 禁用汇报
            self.opts.add_argument('--incognito')                                       # 隐身模式
            self.opts.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) '
                                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                                   'Chrome/70.0.3538.67 Safari/537.36')                 # user-agent
            self.caps = self.opts.to_capabilities()                                     # 更新技能
            self.caps['loggingPrefs'] = {'performance': 'ALL'}                          # 获取trace log
            self.driver = webdriver.Chrome(desired_capabilities=self.caps)              # 启动浏览器
            self.driver.set_page_load_timeout(time_out)                                 # 全局页面加载超时
            self.driver.set_script_timeout(time_out)                                    # 全局js加载超时
        except WebDriverException:
            self.logger.info("启动无头框架失败(*>﹏<*)【NO】")
            return False
        except ReadTimeoutError:
            self.logger.info("启动无头响应超时(⊙﹏⊙)【NO】")
            return False
        except Exception as ex:
            self.logger.info(f"启动无头未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info("启动无头程序成功(*^__^*)【OK】")
            return True
    
    def set_quit(self) -> bool:
        """
        关闭会话是否成功
        :return: bool
        """
        try:
            self.driver.quit()
        except WebDriverException:
            self.logger.info("关闭无头框架失败(*>﹏<*)【NO】")
            return False
        except ReadTimeoutError:
            self.logger.info("关闭无头响应超时(⊙﹏⊙)【NO】")
            return False
        except Exception as ex:
            self.logger.info(f"关闭无头未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info("关闭无头程序成功(*^__^*)【OK】")
            return True
    
    def set_close(self) -> bool:
        """
        关闭会话是否成功
        :return: bool
        """
        try:
            self.driver.close()
        except WebDriverException:
            self.logger.info("关闭会话框架失败(*>﹏<*)【NO】")
            return False
        except ReadTimeoutError:
            self.logger.info("关闭会话响应超时(⊙﹏⊙)【NO】")
            return False
        except Exception as ex:
            self.logger.info(f"关闭会话未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info("关闭会话程序成功(*^__^*)【OK】")
            return True
    
    def set_script(self, js: str = "") -> bool:
        """
        执行脚本是否成功
        :param js: 执行脚本类似document.getElementById
        :return: bool
        """
        try:
            self.driver.execute_script(js)
        except WebDriverException:
            self.logger.info("执行脚本框架失败(*>﹏<*)【NO】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"执行脚本响应超时(⊙﹏⊙)【NO】")
            return False
        except Exception as ex:
            self.logger.info(f"执行脚本未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"执行脚本程序成功(*^__^*)【OK】")
            return True
    
    def set_url(self, url: str = "") -> bool:
        """
        打开页面是否成功
        :param url: 链接地址
        :return: bool
        """
        try:
            self.driver.get(url)
        except WebDriverException:
            self.logger.info(f"打开页面框架失败(*>﹏<*)【{url}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"打开页面响应超时(⊙﹏⊙)【{url}】")
            return False
        except Exception as ex:
            self.logger.info(f"打开页面未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"打开页面程序成功(*^__^*)【{url}】")
            return True
    
    def set_click(self, css: str = "") -> bool:
        """
        点击元素是否成功
        :param css: css语法
        :return: bool
        """
        try:
            element = self.driver.find_element_by_css_selector(css)
            element.click()
        except WebDriverException:
            self.logger.info(f"点击元素框架失败(*>﹏<*)【{css}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"点击元素响应超时(⊙﹏⊙)【{css}】")
            return False
        except Exception as ex:
            self.logger.info(f"点击元素未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"点击元素程序成功(*^__^*)【{css}】")
            return True
    
    def get_window(self) -> str:
        """
        获取窗口是否成功
        :return: str
        """
        try:
            window = self.driver.current_window_handle
        except WebDriverException:
            self.logger.info("获取窗口框架失败(*>﹏<*)【NO】")
            return ""
        except ReadTimeoutError:
            self.logger.info("获取窗口响应超时(⊙﹏⊙)【NO】")
            return ""
        except Exception as ex:
            self.logger.info(f"获取窗口未知失败(*>﹏<*)【{ex}】")
            return ""
        else:
            self.logger.info("获取窗口程序成功(*^__^*)【OK】")
            return window
    
    def set_switch(self, window: str = "") -> bool:
        """
        切换窗口是否成功
        :param window: 窗口id
        :return: bool
        """
        try:
            self.driver.switch_to.window(window)
        except WebDriverException:
            self.logger.info("切换窗口框架失败(*>﹏<*)【NO】")
            return False
        except ReadTimeoutError:
            self.logger.info("切换窗口响应超时(⊙﹏⊙)【NO】")
            return False
        except Exception as ex:
            self.logger.info(f"切换窗口未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info("切换窗口程序成功(*^__^*)【OK】")
            return True
    
    def set_window(self, *window) -> bool:
        """
        设置窗口是否成功
        :param window: 窗口ID，可多个参数
        :return: bool
        """
        try:
            handles = self.driver.window_handles                    # 获取所有窗口句柄
            for handle in window:                                   # 循环所有句柄删除已有的句柄
                handles.remove(handle)
            self.driver.switch_to.window(handles[0])                # 切换到剩下的最后一个句柄
        except WebDriverException:
            self.logger.info("设置窗口框架失败(*>﹏<*)【NO】")
            return False
        except ReadTimeoutError:
            self.logger.info("设置窗口响应超时(⊙﹏⊙)【NO】")
            return False
        except Exception as ex:
            self.logger.info(f"设置窗口未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info("设置窗口程序成功(*^__^*)【OK】")
            return True
    
    def get_log(self) -> list:
        """
        获取日志是否成功
        :return: list
        """
        try:
            log = self.driver.get_log("performance")
        except WebDriverException:
            self.logger.info("获取日志框架失败(*>﹏<*)【NO】")
            return []
        except ReadTimeoutError:
            self.logger.info("获取日志响应超时(⊙﹏⊙)【NO】")
            return []
        except Exception as ex:
            self.logger.info(f"获取日志未知失败(*>﹏<*)【{ex}】")
            return []
        else:
            self.logger.info("获取日志程序成功(*^__^*)【OK】")
            return log
    
    def get_page(self) -> str:
        """
        获取页面是否成功
        :return: str
        """
        try:
            page = self.driver.page_source
        except WebDriverException:
            self.logger.info("获取页面框架失败(*>﹏<*)【NO】")
            return ""
        except ReadTimeoutError:
            self.logger.info("获取页面响应超时(⊙﹏⊙)【NO】")
            return ""
        except Exception as ex:
            self.logger.info(f"获取页面未知失败(*>﹏<*)【{ex}】")
            return ""
        else:
            self.logger.info("获取页面程序成功(*^__^*)【OK】")
            return page
    
    def delete_cookies(self) -> bool:
        """
        删除缓存是否成功
        :return: bool
        """
        try:
            self.driver.delete_all_cookies()
        except WebDriverException:
            self.logger.info("删除缓存框架失败(*>﹏<*)【NO】")
            return False
        except ReadTimeoutError:
            self.logger.info("删除缓存响应超时(⊙﹏⊙)【NO】")
            return False
        except Exception as ex:
            self.logger.info(f"删除缓存未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info("删除缓存程序成功(*^__^*)【OK】")
            return True
    
    def find_element(self, css: str = "", seconds: float = 1) -> bool:
        """
        查找元素是否成功
        :param css: css语法
        :param seconds: 超时时间
        :return: bool
        """
        try:
            WebDriverWait(driver=self.driver, timeout=seconds, poll_frequency=0.1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css)))
        except WebDriverException:
            self.logger.info(f"查找元素框架失败(*>﹏<*)【{css}】【{seconds}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"查找元素响应超时(⊙﹏⊙)【{css}】【{seconds}】")
            return False
        except Exception as ex:
            self.logger.info(f"查找元素未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"查找元素程序成功(*^__^*)【{css}】【{seconds}】")
            return True
    
    def wait_element(self, css: str = "", seconds: float = 1) -> bool:
        """
        等待元素是否成功
        :param css: css语法
        :param seconds: 超时时间
        :return: bool
        """
        try:
            WebDriverWait(driver=self.driver, timeout=seconds, poll_frequency=0.1).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css)))
        except WebDriverException:
            self.logger.info(f"等待元素框架失败(*>﹏<*)【{css}】【{seconds}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"等待元素响应超时(⊙﹏⊙)【{css}】【{seconds}】")
            return False
        except Exception as ex:
            self.logger.info(f"等待元素未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"等待元素程序成功(*^__^*)【{css}】【{seconds}】")
            return True
    
    def hide_element(self, css: str = "", seconds: float = 1) -> bool:
        """
        隐藏元素是否成功
        :param css: css语法
        :param seconds: 超时时间
        :return: bool
        """
        try:
            WebDriverWait(driver=self.driver, timeout=seconds, poll_frequency=0.1).until_not(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css)))
        except WebDriverException:
            self.logger.info(f"隐藏元素框架失败(*>﹏<*)【{css}】【{seconds}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"隐藏元素响应超时(⊙﹏⊙)【{css}】【{seconds}】")
            return False
        except Exception as ex:
            self.logger.info(f"隐藏元素未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"隐藏元素程序成功(*^__^*)【{css}】【{seconds}】")
            return True
    
    def touch_element(self, css: str = "", seconds: float = 1) -> bool:
        """
        触碰元素是否成功
        :param css: css语法
        :param seconds: 超时时间
        :return: bool
        """
        try:
            WebDriverWait(driver=self.driver, timeout=seconds, poll_frequency=0.1).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css)))
        except WebDriverException:
            self.logger.info(f"触碰元素框架失败(*>﹏<*)【{css}】【{seconds}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"触碰元素响应超时(⊙﹏⊙)【{css}】【{seconds}】")
            return False
        except Exception as ex:
            self.logger.info(f"触碰元素未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"触碰元素程序成功(*^__^*)【{css}】【{seconds}】")
            return True
    
    def show_elements(self, css: str = "", seconds: float = 1) -> bool:
        """
        显示元素是否成功
        :param css: css语法
        :param seconds: 超时时间
        :return: bool
        """
        try:
            WebDriverWait(driver=self.driver, timeout=seconds, poll_frequency=0.1).until(
                EC.visibility_of_any_elements_located((By.CSS_SELECTOR, css)))
        except WebDriverException:
            self.logger.info(f"显示元素框架失败(*>﹏<*)【{css}】【{seconds}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"显示元素响应超时(⊙﹏⊙)【{css}】【{seconds}】")
            return False
        except Exception as ex:
            self.logger.info(f"显示元素未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"显示元素程序成功(*^__^*)【{css}】【{seconds}】")
            return True
    
    def find_elements(self, css: str = "", attr: str = "") -> list:
        """
        查找属性是否成功
        :param css: css语法
        :param attr: 标签属性
        :return: list
        """
        elements_list = []
        try:
            elements = self.driver.find_elements_by_css_selector(css)
            for i in elements:
                elements_list.append(i.get_attribute(attr))
        except WebDriverException:
            self.logger.info(f"查找属性框架失败(*>﹏<*)【{css}】【{attr}】")
            return []
        except ReadTimeoutError:
            self.logger.info(f"查找属性响应超时(⊙﹏⊙)【{css}】【{attr}】")
            return []
        except Exception as ex:
            self.logger.info(f"查找属性未知失败(*>﹏<*)【{ex}】")
            return []
        else:
            self.logger.info(f"查找属性程序成功(*^__^*)【{css}】【{attr}】")
            return elements_list
    
    def wait_alert(self, seconds: float = 1) -> bool:
        """
        等待弹框是否成功
        :param seconds: 超时时间
        :return: bool
        """
        try:
            WebDriverWait(driver=self.driver, timeout=seconds, poll_frequency=0.1).until(EC.alert_is_present())
        except WebDriverException:
            self.logger.info(f"等待弹框框架失败(*>﹏<*)【{seconds}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"等待弹框响应超时(⊙﹏⊙)【{seconds}】")
            return False
        except Exception as ex:
            self.logger.info(f"等待弹框未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"等待弹框程序成功(*^__^*)【{seconds}】")
            return True
    
    def enter_alert(self) -> bool:
        """
        确认弹框是否成功
        :return: bool
        """
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
        except WebDriverException:
            self.logger.info("确认弹框框架失败(*>﹏<*)【NO】")
            return False
        except ReadTimeoutError:
            self.logger.info("确认弹框响应超时(⊙﹏⊙)【NO】")
            return False
        except Exception as ex:
            self.logger.info(f"确认弹框未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"确认弹框程序成功(*^__^*)【OK】")
            return True
    
    def set_text(self, css: str = "", value: str = "") -> bool:
        """
        设置文本是否成功
        :param css: css语法
        :param value: 文本内容
        :return: bool
        """
        try:
            element = self.driver.find_element_by_css_selector(css)
            element.clear()
            element.send_keys(value)
        except WebDriverException:
            self.logger.info(f"设置文本框架失败(*>﹏<*)【{css}】【{value}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"设置文本响应超时(⊙﹏⊙)【{css}】【{value}】")
            return False
        except Exception as ex:
            self.logger.info(f"设置文本未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"设置文本程序成功(*^__^*)【{css}】【{value}】")
            return True
    
    def get_text(self, css: str = "") -> str:
        """
        获取文本是否成功
        :param css: css语法
        :return: str
        """
        try:
            element = self.driver.find_element_by_css_selector(css)
            css_text = element.text
            final_text = re.sub("\n|\t|\r|\s", "", css_text)                    # 正则替换空格等特殊符号
        except WebDriverException:
            self.logger.info(f"获取文本框架失败(*>﹏<*)【{css}】")
            return ""
        except ReadTimeoutError:
            self.logger.info(f"获取文本响应超时(⊙﹏⊙)【{css}】")
            return ""
        except Exception as ex:
            self.logger.info(f"获取文本未知失败(*>﹏<*)【{ex}】")
            return ""
        else:
            self.logger.info(f"获取文本程序成功(*^__^*)【{css}】【{final_text}】")
            return final_text
    
    def get_value(self, css: str = "", attr: str = "") -> str:
        """
        获取属性是否成功
        :param css: css语法
        :param attr: 标签属性
        :return: str
        """
        try:
            element = self.driver.find_element_by_css_selector(css)
            value = element.get_attribute(attr)
        except WebDriverException:
            self.logger.info(f"获取属性框架失败(*>﹏<*)【{css}】")
            return ""
        except ReadTimeoutError:
            self.logger.info(f"获取属性响应超时(⊙﹏⊙)【{css}】")
            return ""
        except Exception as ex:
            self.logger.info(f"获取属性未知失败(*>﹏<*)【{ex}】")
            return ""
        else:
            self.logger.info(f"获取属性程序成功(*^__^*)【{css}】")
            return value
    
    def count_elements(self, css: str = "") -> int:
        """
        计数元素是否成功
        :param css: css语法
        :return: int
        """
        try:
            elements = self.driver.find_elements_by_css_selector(css)
            count = len(elements)
        except WebDriverException:
            self.logger.info(f"计数元素框架失败(*>﹏<*)【{css}】")
            return 0
        except ReadTimeoutError:
            self.logger.info(f"计数元素响应超时(⊙﹏⊙)【{css}】")
            return 0
        except Exception as ex:
            self.logger.info(f"计数元素未知失败(*>﹏<*)【{ex}】")
            return 0
        else:
            self.logger.info(f"计数元素程序成功(*^__^*)【{css}】【{count}】")
            return count
    
    def enter_element(self, css) -> bool:
        """
        回车元素是否成功
        :param css: css语法
        :return: bool
        """
        try:
            element = self.driver.find_element_by_css_selector(css)
            element.send_keys(Keys.ENTER)
        except WebDriverException:
            self.logger.info(f"回车元素框架失败(*>﹏<*)【{css}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"回车元素响应超时(⊙﹏⊙)【{css}】")
            return False
        except Exception as ex:
            self.logger.info(f"回车元素未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"回车元素程序成功(*^__^*)【{css}】")
            return True
    
    def set_style(self, status: str = "", text: str = "", style: str = "") -> None:
        """
        设置样式是否成功
        :param status: 状态是class, id
        :param text: 标签
        :param style: 样式是none,block
        :return: None
        """
        js = ""
        if status == "class":
            js = """
            var font=document.getElementsByClassName("%s");
            for(var i=0;i<font.length;i++){
                font[i].style.display='%s';
            }
            """ % (text, style)
        elif status == "id":
            js = f'document.getElementById("{text}").style="display: {style};";'
        else:
            pass
        self.set_script(js)
    
    def crop_image(self, css: str = "", path: str = "") -> bool:
        """
        截取图片是否成功
        :param path: 保存地址
        :param css: css语法
        :return: bool
        """
        try:
            im = Image.open(BytesIO(self.driver.get_screenshot_as_png()))               # 获取浏览器当前截图
            element = self.driver.find_element_by_css_selector(css)                     # 获取标签的大小，焦点
            left = element.location['x']
            top = element.location['y']
            right = left + element.size['width']
            bottom = top + element.size['height']
            im = im.crop((left, top, right, bottom))                                    # 进行裁剪
            im.save(path)                                                               # 保存
        except WebDriverException:
            self.logger.info(f"截取图片框架失败(*>﹏<*)【{css}】【{path}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"截取图片响应超时(⊙﹏⊙)【{css}】【{path}】")
            return False
        except Exception as ex:
            self.logger.info(f"截取图片未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"截取图片程序成功(*^__^*)【{css}】【{path}】")
            return True
    
    def check_error(self) -> bool:
        """
        检查页面是否被封
        :return: bool
        """
        try:
            current_url = self.driver.current_url
        except WebDriverException:
            self.logger.info("检查页面框架失败(*>﹏<*)【NO】")
            return False
        except ReadTimeoutError:
            self.logger.info("检查页面响应超时(⊙﹏⊙)【NO】")
            return False
        except Exception as ex:
            self.logger.info(f"检查页面未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            if "error" in current_url:
                self.logger.info(f"检查页面已被封禁(⊙﹏⊙)【{current_url}】")
                return True
            else:
                self.logger.info(f"检查页面没被封禁(*^__^*)【{current_url}】")
                return False
    
    def click_image(self, code_list: list, css: str, x_increment: float = 0, y_increment: float = 0) -> bool:
        """
        点击图片是否成功
        :param code_list: 坐标轴数据
        :param css: 要点击元素css语法
        :param x_increment: x偏移增量
        :param y_increment: y偏移增量
        :return: bool
        """
        try:
            element = self.driver.find_element_by_css_selector(css)                         # 获取标签
            for i in range(0, len(code_list), 2):                                           # 循环坐标数字，2个一组
                x_move = int(code_list[i]) + x_increment                                    # x轴加上偏移量
                y_move = int(code_list[i + 1]) + y_increment                                # y轴加上偏移量
                ActionChains(self.driver).move_to_element_with_offset(                      # 进行点击动作
                    element, x_move, y_move).click().perform()
        except WebDriverException:
            self.logger.info(f"点击图片框架失败(*>﹏<*)【{css}】【{code_list}】")
            return False
        except ReadTimeoutError:
            self.logger.info(f"点击图片响应超时(⊙﹏⊙)【{css}】【{code_list}】")
            return False
        except Exception as ex:
            self.logger.info(f"点击图片未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"点击图片程序成功(*^__^*)【{css}】【{code_list}】")
            return True
    
    def parse_sub(self, regex_text: str = "", replace_text: str = "", source: str = "") -> str:
        """
        正则替换是否成功
        :param regex_text: 正则
        :param replace_text: 替换成什么
        :param source: 匹配的数据来源
        :return: str
        """
        try:
            sub_text = re.sub(regex_text, replace_text, source)
        except Exception as ex:
            self.logger.info(f"正则替换数据失败(*>﹏<*)【{ex}】")
            return ""
        else:
            self.logger.info(f"正则替换数据成功(*^__^*)【{regex_text}】")
            return sub_text
    
    def parse_regex(self, reg: str = "", source: str = "") -> str:
        """
        正则匹配是否成功
        :param reg: 正则格式
        :param source: 匹配的数据来源
        :return: str
        """
        try:
            data = re.search(reg, source, re.S)
        except Exception as ex:
            self.logger.info(f"正则匹配数据失败(*>﹏<*)【{ex}】")
            return ""
        else:
            self.logger.info(f"正则匹配数据成功(*^__^*)【{reg}】")
            return data[0]
    
    def transform_source(self, src: str = "") -> str:
        """
        转化来源是否成功
        :param src: 图片base64数据串
        :return: str
        """
        if src:
            try:
                src = src.split(",")
            except Exception as ex:
                self.logger.info(f"转化来源未知失败(*>﹏<*)【{ex}】")
                return ""
            else:
                self.logger.info("转化来源程序成功(*^__^*)【OK】")
                return src[1]
        else:
            self.logger.info(f"转化来源参数为空(*>﹏<*)【{src}】")
            return ""
    
    def transform_scan(self, path) -> str:
        """
        转化扫码是否成功
        :param path: 图片地址
        :return: str
        """
        try:
            im = Image.open(path)
            barcode = pyzbar.decode(im)
            barcode_data = barcode[0].data.decode("utf-8")
        except Exception as ex:
            self.logger.info(f"转化扫码程序失败(*>﹏<*)【{ex}】")
            return ""
        else:
            self.logger.info("转化扫码程序成功(*^__^*)【OK】")
            return barcode_data
    
    def transform_captcha(self, path) -> str:
        """
        转化打码是否成功
        :param path: 图片地址
        :return: str
        """
        try:
            with open(path, 'rb') as f:
                image_flow = base64.b64encode(f.read())                             # 对图片base64编码
        except Exception as ex:
            self.logger.info(f"转化打码程序失败(*>﹏<*)【{ex}】")
            return ""
        else:
            self.logger.info("转化打码程序成功(*^__^*)【OK】")
            return str(image_flow, 'utf-8')
    
    def get_scan(self, image_flow, login_name, login_pwd) -> bool:
        """
        获取扫码是否成功
        :param image_flow: 扫码图片base64字符串
        :param login_name: 用户登录名
        :param login_pwd: 用户密码
        :return: bool
        """
        try:
            rep_url = "http://appgeturl.hangtian123.net/AppRepServer/GetRepUrlServlet?type=1"           # 请求app地址
            with request.urlopen(url=rep_url, timeout=10) as res:
                response = res.read().decode('utf-8')
            result = self.parse_json(response)
            server_ip = result.get("serverIp", "")                                                      # 解析获取地址
            if not server_ip:
                self.logger.info(f"获取扫码地址为空(*>﹏<*)【{result}】")
                return False
            data_dict = {"loginName": login_name, "loginPwd": login_pwd, "qrcode": image_flow}          # 拼接转化请求数据
            data_string = str(data_dict)
            data_quote = parse.quote(data_string)                                                       # 数据进行转义
            query_url = f"http://{server_ip}:19090/api/train/app/control?" \
                f"datatypeflag=qrScanLogin&jsonStr={data_quote}"                                        # 拼接第二个请求地址
            with request.urlopen(url=query_url, timeout=10) as res:
                response = res.read().decode('utf-8')
            result = self.parse_json(response)                                                          # 请求返回结果
            success = result.get("succ_flag", "")
            if success == "1":
                self.logger.info(f"获取扫码程序成功(*^__^*)【{result}】")
                return True
            else:
                self.logger.info(f"获取扫码返回失败(*>﹏<*)【{result}】")
                return False
        except Exception as ex:
            self.logger.info(f"获取扫码程序失败(*>﹏<*)【{ex}】")
            return False
    
    def get_captcha(self, image_flow: str = "", interval: int = 2) -> list:
        """
        获取打码是否成功
        :param image_flow: 打码图片base64字符串
        :param interval: 打码图片base64字符串
        :return: list
        """
        if image_flow:
            product_agent = "0C13D7C3566147EB90D1E273278DCDD9hangt"                                     # 权限认证
            upload_url = "http://taobaodama.hangtian123.net/captcha/api/uploadCaptcha.jsp"              # 上传图片地址
            result_url = "http://taobaodama.hangtian123.net/captcha/api/queryResult.jsp"                # 获取结果地址
            # # # 第一次加密
            product_string = product_agent + image_flow
            hash_md5 = hashlib.md5(product_string.encode('utf-8')).hexdigest()                          # md5加密
            # # # 第一次请求数据
            data = {'agentCode': "hangt", 'image': image_flow, 'hmac': hash_md5}
            post_data = bytes(parse.urlencode(data), encoding='utf-8')
            try:
                with request.urlopen(url=upload_url, data=post_data, timeout=5) as res:
                    response = res.read().decode('utf-8')
                # # # 解析并检查global
                get_result = self.parse_json(response)
                result = get_result.get('data', {}).get('globalId', '')
                if result:
                    time.sleep(interval)                                                                # 间隔时间
                    # # # 第二次加密
                    product_string = product_agent + result
                    hash_md5 = hashlib.md5(product_string.encode('utf-8')).hexdigest()
                    # # # 第二次请求数据
                    data = {'agentCode': "hangt", 'globalId': result, 'hmac': hash_md5}
                    post_data = bytes(parse.urlencode(data), encoding='utf-8')
                    with request.urlopen(url=result_url, data=post_data, timeout=5) as res:
                        response = res.read().decode('utf-8')
                    # # # 解析并检查global
                    get_result = self.parse_json(response)
                    result = get_result.get('data', {}).get('result', '')
                    if result:
                        result_list = []
                        for i in list(result.split(',')):
                            result_list.append(i)
                        if len(result_list) >= 2 and len(result_list) % 2 == 0:
                            self.logger.info(f"获取打码程序成功(*^__^*)【{result_list}】")
                            return result_list
                        else:
                            self.logger.info(f"打码个数不是偶数(*>﹏<*)【{result_list}】")
                            return []
            except Exception as ex:
                self.logger.info(f"获取打码程序失败(*>﹏<*)【{ex}】")
                return []
    
    def parse_json(self, json_string: str = "", is_log: int = 0) -> dict:
        """
        转化字典是否成功
        :param json_string: 需要转化字典的字符串
        :param is_log: 是否打印日志
        :return: dict
        """
        try:
            data_dict = json.loads(json_string)
        except Exception as ex:
            self.logger.info(f"转化字典程序失败(*>﹏<*)【{ex}】")
            return {}
        else:
            if is_log:
                self.logger.info(f"转化字典程序成功(*^__^*)【OK】")
            return data_dict
    
    def parse_dump(self, json_dict=None) -> str:
        """
        解析字典是否成功
        :param json_dict: 需要解析的字典
        :return: str
        """
        if not json_dict:
            json_dict = {}
        try:
            json_string = json.dumps(json_dict, ensure_ascii=False)
        except Exception as ex:
            self.logger.info(f"解析字典程序失败(*>﹏<*)【{ex}】")
            return ""
        else:
            self.logger.info(f"解析字典程序成功(*^__^*)【OK】")
            return json_string
    
    def set_shell(self, shell: str = "") -> bool:
        """
        执行脚本是否成功
        :param shell: 脚本语法
        :return: bool
        """
        try:
            code = os.system(shell)                         # 执行脚本，linux下代码返回0是成功
        except Exception as ex:
            self.logger.info(f"执行脚本程序失败(*>﹏<*)【{ex}】")
            return False
        else:
            if not code:
                self.logger.info(f"执行脚本程序成功(*^__^*)【{code}】")
                return True
            else:
                self.logger.info(f"执行脚本程序失败(*>﹏<*)【{code}】")
                return False

    def ding_talk(self, content: str = "") -> bool:
        """
        发送预警是否成功
        :param content: 发送内容
        :return: bool
        """
        ding_url = "https://oapi.dingtalk.com/robot/send?access_token=" \
                   "499590050800d5272d50385e2fdfd5a6699364db2e11e006bbb83d89f624bd81"       # 发送地址
        ding_json = {"msgtype": "text", "text": {"content": content},                       # 发送信息
                     "at": {"atMobiles": ["18501250875"], "isAtAll": True}}
        try:
            with requests.post(url=ding_url, json=ding_json, timeout=5) as res:             # 发送请求
                response = res.json()
        except Exception as ex:
            self.logger.info(f"发送预警程序失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"发送预警程序成功(*^__^*)【{response}】")
            return True

    def connect_mongo(self) -> None:
        """
        数据库连接是否成功
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

    def get_data(self, status: str = "", get_stamp: str = "") -> list:
        """
        获取数据结果集
        :param status:  获取类型 parameter获取参数时间戳，content获取内容时间戳
        :param get_stamp: 传入的时间戳
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

    def set_time(self) -> bool:
        """
        设置爬取时间入库
        :return: bool
        """
        self.scrape_time = int(time.time())
        try:
            all_time = self.mongo_time.find_one({"type": "time"})                   # 设置time数据库俩个标识
            if all_time:
                self.mongo_time.update(
                    {"type": "time"}, {"$set": {"new_time": self.scrape_time, "old_time": all_time['new_time']}}, upsert=True)
            else:
                self.mongo_time.update(
                    {"type": "time"}, {"$set": {"new_time": self.scrape_time, "old_time": self.scrape_time}}, upsert=True)
        except Exception as ex:
            self.logger.info(f"设置数据库时间失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info("设置数据库时间成功(*^__^*)【OK】")
            return True
    
    def insert_content(self, query=None) -> None:
        """
        插入数据库地址响应内容
        :param query: 传入的可查询列表
        :return: None
        """
        if query and type(query) is list:
            result = self.get_data("parameter", self.scrape_time)
            for i in result:
                for j in query:
                    if j in i['package_url']:
                        try:
                            with requests.get(i['package_url'], timeout=5) as res:
                                response = res.text
                            self.mongo_content.insert_one(
                                {"package_url": i['package_url'], "package_text": response, "scrape_time": self.scrape_time})
                        except Exception:
                            continue
                        else:
                            pass
                        
    def insert_parameter(self, get_log=None) -> None:
        """
        插入数据库地址参数
        :param get_log: 传入的日志列表
        :return: None
        """
        if get_log and type(get_log) is list:
            for i in get_log:                                                               # 循环日志集合
                # # # 根据日志格式获取字典信息
                msg = self.parse_json(i.get('message', {}))
                package = msg.get('message', {}).get('method', "")
                package_data = msg.get('message', {}).get('params', {})
                package_type = package_data.get('type', "")
                # # # 我们只查询network响应的信息，只要ajax,js,html
                if 'Network.responseReceived' in package:
                    if "XHR" in package_type or "Script" in package_type or "Document" in package_type:
                        all_url = package_data.get('response', {}).get('url', "")           # 获取连接地址，只要带http开头的，并分割？前后
                        if all_url and "http" in all_url:
                            # # # 分割？区分连接和参数
                            if "?" in all_url:
                                url = all_url.split("?")
                                base = url[0]
                                tails = url[1]
                                args = self.parse_args(tails)
                            else:
                                base = all_url
                                args = []
                            # # # 获取请求方法
                            method_text = package_data.get('response', {}).get('requestHeadersText', "")
                            if method_text:
                                method_text = method_text.split(" ")
                                method = method_text[0]
                            else:
                                method = ""
                            # # # 拆分header和cookie
                            header = package_data.get('response', {}).get('requestHeaders', {})
                            cookie = package_data.get('response', {}).get('requestHeaders', {}).get("Cookie", "")
                            if cookie:
                                header.pop('Cookie')
                            # # # 获取请求header，cookie, set_cookies
                            headers = self.parse_headers(header)
                            cookies = self.parse_cookies(cookie)
                            set_cookie = package_data.get('response', {}).get('headers', {}).get('Set-Cookie', "")
                            set_cookies = self.parse_sets(set_cookie)
                            # # # 插入数据库
                            try:
                                self.mongo_parameter.insert_one(
                                    {"package": package, "package_type": package_type, "package_method": method,
                                     "package_url": base, "package_args": args, "package_headers": headers,
                                     "package_cookies": cookies, "package_sets": set_cookies, "scrape_time": self.scrape_time
                                     })
                            except Exception:
                                continue
                            else:
                                pass

    def parse_args(self, tails: str = "") -> list:
        """
        解析链接后面参数
        :param tails: 参数字符串
        :return: list
        """
        try:
            args = []
            tails = tails.split("&")
            for j in tails:
                j = j.split("=")
                if len(j) > 1:
                    args.append(j[0])
        except Exception as ex:
            self.logger.info(f"解析链接参数失败(*>﹏<*)【{ex}】")
            return []
        else:
            return args

    def parse_headers(self, header=None) -> list:
        """
        解析链接请求头部
        :param header: 请求header字典
        :return: list
        """
        try:
            headers = []
            for i in header.keys():
                headers.append(i)
        except Exception as ex:
            self.logger.info(f"解析链接头部失败(*>﹏<*)【{ex}】")
            return []
        else:
            return headers

    def parse_cookies(self, cookie: str = "") -> list:
        """
        解析链接请求缓存
        :param cookie: 请求cookie
        :return: list
        """
        try:
            cookies = []
            cookie = cookie.split("; ")
            for kk in cookie:
                kk = kk.split("=")
                cookies.append(kk[0])
        except Exception as ex:
            self.logger.info(f"解析链接头部失败(*>﹏<*)【{ex}】")
            return []
        else:
            return cookies

    def parse_sets(self, set_cookie: str = "") -> list:
        """
        解析链接返回缓存
        :param set_cookie: 返回设置的cookie
        :return: list
        """
        try:
            set_cookies = []
            set_cookie = set_cookie.split("\n")
            for ss in set_cookie:
                ab = re.search('.*?;', ss, re.S)
                if ab:
                    ab = ab[0][:-1].split("=")
                    set_cookies.append(ab[0])
        except Exception as ex:
            self.logger.info(f"解析链接头部失败(*>﹏<*)【{ex}】")
            return []
        else:
            return set_cookies
