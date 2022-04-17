#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@@..> auto tools
@@..> package utils
@@..> author pyleo <lihao@372163.com>
"""
#######################################################################################
# @@..> base import
from dataclasses import dataclass, field
from .base_tools import ErrorMessage, error_async
# @@..> PuppeteerAct
from pyppeteer import launch, launcher
# @@..! for linux
# from signal import signal, SIGCLD, SIG_IGN


#######################################################################################
# @@... to be continue
@dataclass
class AutoAct:
    """
    [automated browser]
    """
    __logger: any = field(default_factory=bool)
    __browser: any = field(default_factory=bool)
    __page: any = field(default_factory=bool)

    @property
    def logger(self):
        return self.__logger

    @logger.setter
    def logger(self, value):
        self.__logger = value

    @property
    def browser(self):
        return self.__browser

    @property
    def page(self):
        return self.__page

    @error_async("设置无头未知失败")
    async def set_browser(self, headless: bool = True) -> None:
        """
        [set to Chrome]

        Args:
            headless (bool, optional): [set headless mode or not]. Defaults to True.

        Returns:
            None: [nothing.]
        """
        # @@..! must be enabled
        if "--enable-automation" in launcher.DEFAULT_ARGS:
            launcher.DEFAULT_ARGS.remove("--enable-automation")
        # @@..! prevent zombie process, linux only
        # signal(SIGCLD, SIG_IGN)

        self.__browser = await launch({
            'acceptInsecureCerts': True,
            "ignoreHTTPSErrors": True, "headless": headless, "autoClose": False,
            "dumpio": True, "timeout": 1000 * 180,
            "args": [
                # '--proxy-server=http://122.94.44.245:3138'
                '--no-sandbox', '--disable-gpu',
                '--disable-dev-tools',
                "--ignore-certificate-errors", "--ignore-ssl-errors",
                '--disable-infobars', '--allow-running-insecure-content',
                '--disable-crash-reporter'
            ]
        })
        self.__page = await self.__browser.newPage()
        # await self.__page.authenticate({'username': '', 'password': ''})
        await self.__page.setUserAgent(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/71.0.3542.0 Safari/537.36"
        )
        await self.__page.setViewport({'width': 1366, 'height': 768})

    @error_async("设置拦截未知失败")
    async def set_intercept(self, is_intercept: bool) -> None:
        """
        [set to intercept]

        Args:
            is_intercept (bool, optional): [set intercept or not]. Defaults to True.

        Returns:
            None: [nothing.]
        """
        await self.__page.setRequestInterception(is_intercept)

    @ErrorMessage("设置抓包未知失败")
    def set_capture(self, capture_type: str = "",
                    capture_func: any = None) -> None:
        """
        [set to intercept]

        Args:
            capture_type (str, optional): [request/response]. Defaults to nothing.
            capture_func (any, optional): [function]. Defaults to None.

        Returns:
            None: [nothing.]
        """
        self.__page.on(capture_type, capture_func)

    @error_async("设置地址未知失败")
    async def set_url(self, source_url: str = "") -> None:
        """
        [open the url]

        Args:
            source_url (str, optional): [nothing.]. Defaults to nothing.

        Returns:
            None: [nothing.]
        """
        await self.__page.goto(source_url)

    async def get_url(self) -> str:
        """
        [get the url]

        Returns:
            str: [nothing.]
        """
        try:
            return await self.__page.url
        except Exception as ex:
            self.__logger.info(f"获取地址未知失败(*>﹏<*)【{ex}】")
            return ""

    async def get_page(self) -> str:
        """
        [get the page content]

        Returns:
            str: [nothing.]
        """
        try:
            return await self.__page.content()
        except Exception as ex:
            self.__logger.info(f"获取页面未知失败(*>﹏<*)【{ex}】")
            return ""

    @error_async("设置关闭未知失败")
    async def set_close(self) -> None:
        """
        [close the tab]

        Returns:
            None: [nothing.]
        """
        await self.__page.close()

    @error_async("设置退出未知失败")
    async def set_quit(self) -> None:
        """
        [quit the browser]

        Returns:
            None: [nothing.]
        """
        await self.__browser.close()

    @error_async("设置刷新未知失败")
    async def set_refresh(self) -> None:
        """
        [refresh the web]

        Returns:
            None: [nothing.]
        """
        await self.__page.reload()

    @error_async("设置缓存未知失败")
    async def set_cookies(self, cookie_list: list = None) -> None:
        """
        [set custom cookies]

        Args:
            cookie_list (list, optional):
                [name/value/domain/path]. Defaults to None.

        Returns:
            None: [nothing.]
        """
        for i in cookie_list:
            await self.__page.setCookie(i)

    async def get_cookies(self) -> list:
        """
        [get the cookies]

        Returns:
            list: [nothing.]
        """
        try:
            return await self.__page.cookies()
        except Exception as ex:
            self.__logger.info(f"获取缓存未知失败(*>﹏<*)【{ex}】")
            return []

    @error_async("删除缓存未知失败")
    async def set_clear(self) -> bool:
        """
        [clear all cookies]

        Returns:
            bool: [nothing.]
        """
        await self.__page.deleteCookie()

    @error_async("设置文本未知失败")
    async def set_text(self, css_syntax: str = "", source_text: str = "") -> None:
        """
        [set to text]

        Args:
            css_syntax (str, optional): [nothing.]. Defaults to nothing.
            source_text (str, optional): [nothing.]. Defaults to nothing.

        Returns:
            None: [nothing.]
        """
        await self.__page.type(css_syntax, source_text, {"delay": 1000 * 0.1})

    @error_async("设置点击未知失败")
    async def set_click(self, css_syntax: str = "") -> None:
        """
        [element click]

        Args:
            css_syntax (str, optional): [nothing.]. Defaults to nothing.

        Returns:
            None: [nothing.]
        """
        await self.__page.click(css_syntax)

    @error_async("设置回车未知失败")
    async def set_enter(self) -> None:
        """
        [element enter]

        Returns:
            None: [nothing.]
        """
        await self.__page.keyboard.press("Enter", {"delay": 1000 * 0.1})
