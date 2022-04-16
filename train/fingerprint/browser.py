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
import os


class Browser:
	"""
    浏览器基础方法类
    """
	
	def __init__(self):
		self.logger = None  # 类基础日志
		self.opts = webdriver.ChromeOptions()  # 浏览器配置
		self.caps = None  # 浏览器技能
		self.driver = None  # 浏览器驱动
	
	def set_headless(self, proxy_server: str = "", time_out: int = 5) -> bool:
		"""
		启动无头是否成功
		:param proxy_server: 代理服务
		:param time_out: 超时时间
		:return: bool
		"""
		try:
			self.opts.headless = True  # 启用无头
			self.opts.add_argument('--no-sandbox')  # 无头下禁用沙盒
			self.opts.add_argument('--disable-dev-tools')  # 无头下禁用dev
			self.opts.add_argument('--disable-gpu')  # 禁用gpu加速
			self.opts.add_argument('--disable-infobars')  # 禁用提示
			self.opts.add_argument('--ignore-certificate-errors')  # 忽略证书错误
			self.opts.add_argument('--allow-running-insecure-content')  # 与上同步使用
			self.opts.add_argument('--disable-crash-reporter')  # 禁用汇报
			self.opts.add_argument('--incognito')  # 隐身模式
			self.opts.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; WOW64) '
			                       'AppleWebKit/537.36 (KHTML, like Gecko) '
			                       'Chrome/70.0.3538.67 Safari/537.36')  # user-agent
			if proxy_server:
				self.opts.add_argument('--proxy-server=http://localhost:9000')
			self.caps = self.opts.to_capabilities()  # 更新技能
			preferences = {'profile.default_content_setting_values': {'images': 2, 'notifications': 2}}
			self.opts.add_experimental_option('prefs', preferences)
			# self.caps['loggingPrefs'] = {'performance': 'ALL'}                          # 获取trace log
			self.driver = webdriver.Chrome(desired_capabilities=self.caps)  # 启动浏览器
			self.driver.set_page_load_timeout(time_out)  # 全局页面加载超时
			self.driver.set_script_timeout(time_out)  # 全局js加载超时
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

	def set_refresh(self) -> bool:
		"""
		刷新页面是否成功
		:param url: 链接地址
		:return: bool
		"""
		try:
			self.driver.refresh()
		except WebDriverException:
			self.logger.info(f"刷新页面框架失败(*>﹏<*)【NO】")
			return False
		except ReadTimeoutError:
			self.logger.info(f"刷新页面响应超时(⊙﹏⊙)【NO】")
			return False
		except Exception as ex:
			self.logger.info(f"刷新页面未知失败(*>﹏<*)【{ex}】")
			return False
		else:
			self.logger.info(f"刷新页面程序成功(*^__^*)【OK】")
			return True
	
	def set_quit(self) -> bool:
		"""
		刷新页面是否成功
		:param url: 链接地址
		:return: bool
		"""
		try:
			self.driver.quit()
		except WebDriverException:
			self.logger.info(f"退出页面框架失败(*>﹏<*)【NO】")
			return False
		except ReadTimeoutError:
			self.logger.info(f"退出页面响应超时(⊙﹏⊙)【NO】")
			return False
		except Exception as ex:
			self.logger.info(f"退出页面未知失败(*>﹏<*)【{ex}】")
			return False
		else:
			self.logger.info(f"退出页面程序成功(*^__^*)【OK】")
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

	def set_shell(self, shell: str = "") -> bool:
		"""
		执行脚本是否成功
		:param shell: 脚本语法
		:return: bool
		"""
		try:
			code = os.system(shell)  # 执行脚本，linux下代码返回0是成功
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
