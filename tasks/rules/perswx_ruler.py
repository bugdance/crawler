#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> weixin ruler
@@..> package tasks.rules
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> base import
from dataclasses import dataclass, field
# @@..> import utils
from .base_ruler import BaseWorker, BaseAct, DomAct, TimeAct, JsonAct, StrAct


@dataclass
class PersWXWorker(BaseWorker):
    """
    [weixin web scrape]
    """
    def process_index(self) -> bool:
        # index flow
        if self.flowType == 1:
            return self.process_profile()
        elif self.flowType == 2:
            if self.get_work():
                return True
            else:
                if not self.work_id:
                    self.logger.info(f"非法work号码(*>﹏<*)【{self.work_id}】")
                    return False
                return self.process_work()
        else:
            self.logger.info(f"非法flow类型(*>﹏<*)【{self.flowType}】")
            return False

    def get_work(self) -> bool:
        # @@..! set the blacklist and whitelist
        self.blacklist = {"creator.douyin.com"}
        self.whitelist = {"weixin.sogou.com"}
        if self.process_verify(self.scrapeUrl):
            self.get_return(6, 0)
            return True
        # @@... ways of parse work_id

        # check work_id

        # @@..! return false is do nothing
        return False

    def process_work(self) -> bool:
        # after get work_id, get work page

        # parse data and check
        return False

    def get_profile(self) -> bool:
        # @@..! set the blacklist and whitelist
        self.blacklist = {"creator.douyin.com"}
        self.whitelist = {"weixin.sogou.com"}
        if self.process_verify(self.scrapeUrl):
            self.get_return(6, 0)
            return True
        # @@... ways of parse user_id
        for k, v in self.url_dict.items():
            if "query" in k:
                self.user_id = v[0]
        if not self.user_id:
            self.logger.info(f"非法user号码(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(6, 0)
            return True
        # @@..! return false is do nothing
        return False

    def process_profile(self) -> bool:
        # get user_id
        if self.get_profile():
            return True
        else:
            if not self.user_id:
                self.logger.info(f"非法user号码(*>﹏<*)【{self.user_id}】")
                return False
        # first request
        self.net.url = "https://v.sogou.com/"
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "v.sogou.com",
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
        })
        if not self.net.get_response("get", is_redirect=True):
            return False
        if not self.net.get_page("text", False):
            return False
        
        # after get user_id, get profile page
        TimeAct.format_sleep(30)
        self.homeUrl = f"https://weixin.sogou.com/weixin?type=1&query={self.user_id}" \
                       f"&ie=utf8&s_from=input&_sug_=y&_sug_type_="
        self.net.url = self.homeUrl
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "weixin.sogou.com",
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
        })
        if not self.net.get_response("get", is_redirect=True):
            return False
        if not self.net.get_page("text", False):
            return False
        # check captcha
        html_dom = DomAct.parse_dom(self.net.page)
        captcha_gen = DomAct.parse_selector(html_dom, "#seccodeImage", "id")
        captcha, captcha_gen = BaseAct.parse_generator(captcha_gen)
        if captcha:
            self.logger.info(f"非法image验证(*>﹏<*)【{self.homeUrl}】")
            return False
        # check 404
        no_gen = DomAct.parse_selector(html_dom, "#noresult_part1_container", "id")
        no_result, no_gen = BaseAct.parse_generator(no_gen)
        if no_result:
            self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(6, 0)
            return True
#######################################################################################
        # check user_id
        parse_gen = DomAct.parse_selector(
            html_dom, "label[name=em_weixinhao]", "text")
        userId, parse_gen = BaseAct.parse_generator(parse_gen)
        if not userId and userId != self.user_id:
            self.logger.info("非法user号码(*>﹏<*)【page】")
            self.get_return(6, 0)
            return True
        userId = str(userId)

        parse_gen = DomAct.parse_selector(
            html_dom, "a[uigs='account_image_0'] img", "src")
        avatar, parse_gen = BaseAct.parse_generator(parse_gen)
        if not avatar:
            avatar = ""
        else:
            if not avatar.startswith("http"):
                avatar = "https:" + avatar
            
        parse_gen = DomAct.parse_selector(
            html_dom, "li[id*='box_0'] .ew-pop .pop img[data-id]", "src")
        qrCode, parse_gen = BaseAct.parse_generator(parse_gen)
        if not qrCode:
            qrCode = ""
        else:
            if not qrCode.startswith("http"):
                qrCode = "https:" + qrCode

        parse_gen = DomAct.parse_xpath(
            html_dom, "//a[@uigs='account_name_0']", True)
        nickname, parse_gen = BaseAct.parse_generator(parse_gen)
        if not nickname:
            nickname = ""
        else:
            nickname = StrAct.format_html(nickname)
            nickname = StrAct.format_clear(nickname)

        parse_gen = DomAct.parse_xpath(
            html_dom, "//dl[contains(.//dt, '功能介绍')]//dd", True)
        desc, parse_gen = BaseAct.parse_generator(parse_gen)
        if not desc:
            desc = ""
        else:
            desc = StrAct.format_html(desc)
            desc = StrAct.format_clear(desc, True)

        parse_gen = DomAct.parse_xpath(
            html_dom, "//dd[i[@class='identify']]", True)
        authDetail, parse_gen = BaseAct.parse_generator(parse_gen)
        if not authDetail:
            authDetail = ""
        else:
            authDetail = StrAct.format_html(authDetail)
            authDetail = StrAct.format_clear(authDetail, True)
        # format the data
        if authDetail:
            isAuth = 1
        else:
            isAuth = 2
#######################################################################################
        self.scrapeUrl = self.homeUrl
        # if certify take data and return
        if self.toolType == 1:
            self.profileCounts = {'fansNum': 0, 'followNum': 0}
            self.get_return(6, 1)
            return True
        # get work list
        TimeAct.format_sleep(30)
        self.net.url = f"https://weixin.sogou.com/weixin?type=2&s_from=input" \
                       f"&query={self.user_id}&ie=utf8&_sug_=n&_sug_type_="
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "weixin.sogou.com",
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Referer": self.homeUrl
        })
        if not self.net.get_response("get", is_redirect=True):
            return False
        if not self.net.get_page("text", False):
            return False
        # check captcha
        html_dom = DomAct.parse_dom(self.net.page)
        captcha_gen = DomAct.parse_selector(html_dom, "#seccodeImage", "id")
        captcha, captcha_gen = BaseAct.parse_generator(captcha_gen)
        if captcha:
            self.logger.info(f"非法image验证(*>﹏<*)【{self.homeUrl}】")
            return False
        # check 404 no data
        no_gen = DomAct.parse_selector(html_dom, "#noresult_part1_container", "id")
        no_result, no_gen = BaseAct.parse_generator(no_gen)
        if no_result:
            self.logger.info(f"非法works数据(*>﹏<*)【{self.scrapeUrl}】")
            
        # @@..! set isUrls is 0 and isLast is 1
        self.isLast = 1
        self.isUrls = 0
        # get blog ids list and take urls
        html_dom = DomAct.parse_dom(self.net.page)
        parse_gen = DomAct.parse_selector(
            html_dom, "ul.news-list>li", "text", True)
        for i in parse_gen:
            # parse sub dom
            sub_dom = DomAct.parse_dom(i)
            # get UserName and check
            sub_gen = DomAct.parse_selector(sub_dom, ".s-p a", "text")
            blogUserName, sub_gen = BaseAct.parse_generator(sub_gen)
            if blogUserName != nickname:
                continue

            blogUrl = f"https://weixin.sogou.com/weixin?type=2&s_from=input" \
                      f"&query={self.user_id}&ie=utf8&_sug_=n&_sug_type_="

            sub_gen = DomAct.parse_selector(sub_dom, ".img-box img", "src")
            blogCover, sub_gen = BaseAct.parse_generator(sub_gen)
            if blogCover is False:
                sub_gen = DomAct.parse_selector(sub_dom, ".txt-box img:first-child", "src")
                blogCover, sub_gen = BaseAct.parse_generator(sub_gen)
            if blogCover:
                if not blogCover.startswith("http"):
                    blogCover = "https:" + blogCover
            else:
                blogCover = ""

            sub_gen = DomAct.parse_selector(sub_dom, "h3 a", "text", True)
            blogTitle, sub_gen = BaseAct.parse_generator(sub_gen)
            blogTitle = StrAct.format_html(blogTitle)
            blogTitle = StrAct.format_clear(blogTitle, True)
            
            sub_gen = DomAct.parse_selector(sub_dom, ".txt-info", "text", True)
            blogDesc, sub_gen = BaseAct.parse_generator(sub_gen)
            blogDesc = StrAct.format_html(blogDesc)
            blogDesc = StrAct.format_clear(blogDesc, True)
            
            sub_gen = DomAct.parse_selector(sub_dom, ".s-p", "t")
            blogCreated, sub_gen = BaseAct.parse_generator(sub_gen)
            int_gen = StrAct.parse_integer(blogCreated)
            blogCreated, int_gen = BaseAct.parse_generator(int_gen)
            if blogCreated is False:
                blogCreated = 0
            # type 0 pic/1 video
            blogType = 0
            # take data and return
            self.workBase = {
                "id": 0, "showId": 0, "scrapeUrl": "",
                "url": blogUrl, "uid": "", "nickname": "",
                "type": blogType, "title": blogTitle, "cover": blogCover,
                "created": blogCreated, "source": "", "extra": "",
                "desc": blogDesc, "duration": 0, "videoUrl": "",
                "picNum": 0, "picUrl": [],

                "likeNum": 0, "commentNum": 0, "shareNum": 0,
                "forwardNum": 0, "collectNum": 0,
                "playNum": 0, "viewNum": 0,
                "rewardNum": 0, "danmakuNum": 0, "blogRepost": {}
            }
            # if tool type is not 1, take list
            if self.toolType != 1:
                self.workList.append(self.workBase)
        # set numbers
        if not no_result:
            work_nums = 10
            if self.toolType == 2:
                work_nums = 5
            self.workList = self.workList[:work_nums]
        
        # @@..! matchUid -> userId
        # take base and counts data and return
        self.profileBase = {
            "matchUid": userId, "userId": userId, "accountId": userId,
            "secId": "", "avatar": avatar, "qrCode": qrCode, "nickname": nickname,
            "field": "", "isMember": 0, "isAuth": isAuth,
            "gender": 0, "age": "", "birth": "", "constellation": "",
            "area": "", "notice": "", "desc": desc,
            "memberLevel": "", "memberType": "", "memberDetail": "",
            "authLevel": "", "authType": "", "authDetail": str(authDetail),
            "isCompany": 0, "isGovernmentMedia": 0
        }
        self.profileCounts = {
            "fansNum": 0, "followNum": 0,
            "videos": 0, "blogs": 0, "worksNum": 0,
            "favoriteNum": 0, "collectNum": 0, "likeNum": 0,
            "playNum": 0, "viewNum": 0, "rewardNum": 0
        }

        self.get_return(6, 1)
        return True

