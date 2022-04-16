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
    
    def set_headless(self, proxy_server: str = "", time_out: int = 5) -> bool:
        """
        启动无头是否成功
        :param proxy_server: 代理服务
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
            if proxy_server:
                self.opts.add_argument('--proxy-server=http://localhost:9000')
            self.caps = self.opts.to_capabilities()                                     # 更新技能
            # preferences = {'profile.default_content_setting_values':
            #                    {'images': 2, 'notifications': 2}}
            # self.opts.add_experimental_option('prefs', preferences)
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
            handles = self.driver.window_handles
            for handle in window:
                handles.remove(handle)
            self.driver.switch_to.window(handles[0])
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
    
    def set_cookie(self, cookie: str = "") -> bool:
        """
        设置缓存是否成功
        :param cookie: 接口传来的cookie
        :return: bool
        """
        try:
            self.logger.info(cookie)
            cookie_string = cookie.strip(';')
            cookie_list = cookie_string.split(';')
            for i in cookie_list:
                single = i.split('=')
                self.driver.delete_cookie(single[0])
                if single[0] == "JSESSIONID" or single[0] == "tk":
                    self.driver.add_cookie({'name': single[0], 'value': single[1], 'domain': 'kyfw.12306.cn', 'path': '/otn'})
                else:
                    self.driver.add_cookie(
                        {'name': single[0], 'value': single[1], 'domain': 'kyfw.12306.cn', 'path': '/'})
        except WebDriverException:
            self.logger.info("设置缓存框架失败(*>﹏<*)【NO】")
            return False
        except ReadTimeoutError:
            self.logger.info("设置缓存响应超时(⊙﹏⊙)【NO】")
            return False
        except Exception as ex:
            self.logger.info(f"设置缓存未知失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info("设置缓存程序成功(*^__^*)【OK】")
            return True
    
    def delete_cookies(self):
        """
        删除缓存是否成功
        :return:
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
        :param css:
        :param attr:
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
            final_text = re.sub("\n|\t|\r|\s", "", css_text)
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
        :return:
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
            im = Image.open(BytesIO(self.driver.get_screenshot_as_png()))
            element = self.driver.find_element_by_css_selector(css)
            left = element.location['x']
            top = element.location['y']
            right = left + element.size['width']
            bottom = top + element.size['height']
            im = im.crop((left, top, right, bottom))
            im.save(path)
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
        
    def return_cookies(self) -> str:
        """
        返回缓存是否成功
        :return: str
        """
        try:
            jsessionid = f"{self.driver.get_cookie('JSESSIONID')['name']}=" \
                f"{self.driver.get_cookie('JSESSIONID')['value']};"
            bigipserverotn = f"{self.driver.get_cookie('BIGipServerotn')['name']}=" \
                f"{self.driver.get_cookie('BIGipServerotn')['value']};"
            route = f"{self.driver.get_cookie('route')['name']}=" \
                f"{self.driver.get_cookie('route')['value']};"
            cookies = jsessionid + bigipserverotn + route + "current_captcha_type=Z;"
        except WebDriverException:
            self.logger.info("返回缓存框架失败(*>﹏<*)【NO】")
            return ""
        except ReadTimeoutError:
            self.logger.info(f"返回缓存响应超时(⊙﹏⊙)【NO】")
            return ""
        except Exception as ex:
            self.logger.info(f"返回缓存未知失败(*>﹏<*)【{ex}】")
            return ""
        else:
            self.logger.info("返回缓存程序成功(*^__^*)【OK】")
            return cookies
    
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
            element = self.driver.find_element_by_css_selector(css)
            for i in range(0, len(code_list), 2):
                x_move = int(code_list[i]) + x_increment
                y_move = int(code_list[i + 1]) + y_increment
                ActionChains(self.driver).move_to_element_with_offset(
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
    
    def get_addr(self) -> str:
        """
        获取地址是否成功
        :return: str
        """
        try:
            addr = ""
            ip = os.popen("ip address | grep eth1")
            if not ip:
                self.logger.info(f"获取网卡数据失败(*>﹏<*)【eth1】")
            else:
                addr = self.parse_regex("\d+.\d+.\d+.\d+", ip.read())
        except Exception as ex:
            self.logger.info(f"获取机器数据失败(*>﹏<*)【{ex}】")
            return ""
        else:
            self.logger.info(f"获取机器数据成功(*^__^*)【{addr}】")
            return addr

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
                image_flow = base64.b64encode(f.read())  # 对图片base64编码
        except Exception as ex:
            self.logger.info(f"转化打码程序失败(*>﹏<*)【{ex}】")
            return ""
        else:
            self.logger.info("转化打码程序成功(*^__^*)【OK】")
            return str(image_flow, 'utf-8')
    
    def get_scan(self, image_flow, login_name, login_pwd) -> bool:
        """
        获取扫码是否成功
        :param image_flow:
        :param login_name:
        :param login_pwd:
        :return: bool
        """
        try:
            rep_url = "http://appgeturl.hangtian123.net/AppRepServer/GetRepUrlServlet?type=1"       # 请求rep地址
            with request.urlopen(url=rep_url, timeout=5) as res:
                response = res.read().decode('utf-8')
            result = self.parse_json(response)
            server_ip = result.get("serverIp", "")                                                  # 解析获取地址
            if not server_ip:
                self.logger.info(f"获取扫码地址为空(*>﹏<*)【{result}】")
                return False
            data_dict = {"loginName": login_name, "loginPwd": login_pwd, "qrcode": image_flow}      # 拼接转化请求数据
            data_string = str(data_dict)
            data_quote = parse.quote(data_string)
            query_url = f"http://{server_ip}:19090/api/train/app/control?datatypeflag=qrScanLogin&jsonStr={data_quote}"
            with request.urlopen(url=query_url, timeout=5) as res:
                response = res.read().decode('utf-8')
            result = self.parse_json(response)                                                      # 请求返回结果
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
            product_agent = "0C13D7C3566147EB90D1E273278DCDD9hangt"  # 权限认证
            upload_url = "http://taobaodama.hangtian123.net/captcha/api/uploadCaptcha.jsp"  # 上传图片地址
            result_url = "http://taobaodama.hangtian123.net/captcha/api/queryResult.jsp"  # 获取结果地址
            # # # 第一次加密
            product_string = product_agent + image_flow
            hash_md5 = hashlib.md5(product_string.encode('utf-8')).hexdigest()  # md5加密
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
                    time.sleep(interval)  # 间隔时间
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
    
    def parse_json(self, json_string: str = "") -> dict:
        """
        转化字典是否成功
        :param json_string:
        :return: dict
        """
        try:
            data_dict = json.loads(json_string)
        except Exception as ex:
            self.logger.info(f"转化字典程序失败(*>﹏<*)【{ex}】")
            return {}
        else:
            self.logger.info(f"转化字典程序成功(*^__^*)【OK】")
            return data_dict
    
    def parse_dump(self, json_dict=None) -> str:
        """
        解析字典是否成功
        :param json_dict:
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
            code = os.system(shell)  # 执行脚本
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
    
    def set_proxy(self, proxy_server: str = "", proxy_auth: str = "") -> None:
        """
        设置代理是否成功
        :return: None
        """
        if proxy_server and proxy_auth:
            self.set_shell("./kill_proxy.sh")
            self.set_shell(f'mitmdump -q -p 9000 --mode upstream:{proxy_server} '
                           f'--set upstream_auth={proxy_auth} > /dev/null 2>&1 &')
            # self.set_shell("kill_proxy.bat")
            # self.set_shell(f'start /b mitmdump -p 9000 --mode upstream:{proxy_server} --set upstream_auth={proxy_auth}')
            # time.sleep(2)
        else:
            self.set_shell("./kill_proxy.sh")
    
    def get_result(self, data_dict=None, pay_method: int = 2) -> str:
        """
        占座数据返回结果
        :param data_dict: 待解析的结果数据字典
        :param pay_method: 待解析的结果数据字典
        :return: str
        """
        try:
            data_orders = data_dict['orders'][0]  # 获取下单数据
            data_ticket = data_orders["tickets"][0]  # 单人车票信息汇总，只提取公共信息
            data_tickets = data_orders["tickets"]  # 无论单人多人，总的票信息
            data_list = []  # 车票信息列表
            passengers = []  # 人名列表
            # # # 提取每张票信息
            for i in data_tickets:
                data = {
                    "ticket_type_name": i["ticket_type_name"], "return_flag": "N",
                    "return_deliver_flag": i["return_deliver_flag"],
                    "pay_limit_time": i["pay_limit_time"], "resign_flag": "4",
                    "ticket_status_name": "待支付", "ticket_type_code": i["ticket_type_code"],
                    "deliver_fee_char": i["deliver_fee_char"], "amount_char": i["amount_char"],
                    "lose_time": i["lose_time"],
                    "is_need_alert_flag": str(i["is_need_alert_flag"]).lower(),
                    "start_train_date_page": i["start_train_date_page"], "fee_char": i["fee_char"],
                    "dynamicProp": i["dynamicProp"], "is_deliver": i["is_deliver"],
                    "ticket_no": i["ticket_no"], "batch_no": i["batch_no"],
                    "seat_type_name": i["seat_type_name"], "seat_flag": i["seat_flag"],
                    "coach_name": i["coach_name"], "confirm_flag": "N", "ticket_status_code": "i",
                    "coach_no": i["coach_no"], "cancel_flag": "Y", "sequence_no": i["sequence_no"],
                    "trade_mode": "", "passengerDTO": i['passengerDTO'],
                    "reserve_time": i["reserve_time"], "insure_query_no": "",
                    "seat_type_code": i["seat_type_code"], "seat_no": i["seat_no"],
                    "pay_mode_code": i["pay_mode_code"], "train_date": i["train_date"],
                    "ticket_price": i["ticket_price"],
                    "str_ticket_price_page": i["str_ticket_price_page"],
                    "come_go_traveller_ticket_page": i["come_go_traveller_ticket_page"],
                    "print_eticket_flag": "N", "seat_name": i["seat_name"],
                    "stationTrainDTO": i["stationTrainDTO"], "limit_time": i["limit_time"]
                }
                data_list.append(data)
                passengers.append(i['passengerDTO']['passenger_name'])
            # # # 最终回传汇总的信息
            data_final = {
                "status": "true", "validateMessages": {}, "validateMessagesShowId": "_validatorMessage",
                "data": {
                    "to_page": "db",
                    "orderDBList": [
                        {
                            "recordCount": "1", "return_flag": "N", "resign_flag": "N",
                            "ticket_totalnum": data_orders['ticket_totalnum'],
                            "from_station_name_page": [
                                data_ticket['stationTrainDTO']['from_station_name']],
                            "pay_flag": "Y", "if_deliver": data_orders['if_deliver'],
                            "start_train_date_page": data_ticket['start_train_date_page'],
                            "array_passser_name_page": passengers,
                            "arrive_time_page": data_ticket['stationTrainDTO']['arrive_time'][-8:-3],
                            "order_date": data_orders['order_date'],
                            "train_code_page": data_ticket['stationTrainDTO']['station_train_code'],
                            "tickets": data_list, "confirm_flag": "N", "if_show_resigning_info": "N",
                            "ticket_total_price_page": data_orders['ticket_total_price_page'],
                            "come_go_traveller_order_page": data_orders['come_go_traveller_order_page'],
                            "cancel_flag": "Y", "sequence_no": data_orders['sequence_no'],
                            "insure_query_no": "",
                            "isNeedSendMailAndMsg": data_orders['isNeedSendMailAndMsg'],
                            "ticket_price_all": data_orders['ticket_price_all'],
                            "canOffLinePay": data_orders['canOffLinePay'],
                            "pay_resign_flag": "N",
                            "to_station_name_page": [data_ticket['stationTrainDTO']['to_station_name']],
                            "start_time_page": data_ticket['stationTrainDTO']['start_time'][-8:-3],
                            "print_eticket_flag": "N", "reserve_flag_query": "p"
                        }
                    ]
                },
                "payUrlFlag": "flase", "payUrl": "", "payUrlFailMsg": "", "httpstatus": 200,
                "messages": [], "payMethod": pay_method
            }
            result = str(data_final).replace("'", r'\"')  # 修饰双引号给接口识别
            return result
        except Exception as ex:
            self.logger.info(f"解析结果失败（╯＾╰）【{ex}】")
            return ""

