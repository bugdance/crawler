#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> toutiao ruler
@@..> package tasks.rules
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> base import
from dataclasses import dataclass, field
# @@..> import utils
from .base_ruler import BaseWorker, BaseAct, DomAct, TimeAct, JsonAct, StrAct, UrlAct


@dataclass
class PersTTWorker(BaseWorker):
    """
    [toutiao web scrape]
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
        self.whitelist = {"www.toutiao.com"}
        if self.process_verify(self.scrapeUrl):
            self.get_return(8, 0)
            return True
        # @@... ways of parse work_id
        if "/a" in self.url_path:
            self.work_id = self.regex_first(self.url_path, "/a(\\d+)")
        else:
            self.logger.info(f"非法work号码(*>﹏<*)【{self.scrapeUrl}】")
            return False
        # check work_id
        if not self.work_id:
            self.logger.info(f"非法work号码(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(8, 0)
            return True
        # @@..! return false is do nothing
        return False

    def process_work(self) -> bool:
        # @@..! set cookie
        if self.cookies:
            cookies = self.cookies.get("cookie", "")
            cookies_dict = {}
            if cookies:
                cookies = StrAct.format_clear(cookies)
                cookies = cookies.split(";")
                for i in cookies:
                    cookies_gen = StrAct.parse_regex(i, "(.*?)=")
                    name, cookies_gen = BaseAct.parse_generator(cookies_gen)
                    cookies_gen = StrAct.parse_regex(i, ".*?=(.*)")
                    value, cookies_gen = BaseAct.parse_generator(cookies_gen)
                    cookies_dict[name] = value

                self.net.set_cookie(cookies_dict)
        else:
            self.logger.info("非法cookies参数(*>﹏<*)【cookies】")
        # after get work_id, get work page
        self.net.url = f"https://www.toutiao.com/a{self.work_id}"
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "www.toutiao.com",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document"
        })
        if not self.net.get_response("get", is_redirect=True):
            return False
        if not self.net.get_page("text", False):
            return False
        # check 404 page
        html_dom = DomAct.parse_dom(self.net.page)
        parse_gen = DomAct.parse_selector(
            html_dom, "img[usemap*='#map']", "src")
        map404, parse_gen = BaseAct.parse_generator(parse_gen)
        if map404:
            self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(8, 0)
            return True
        # parse data and check
        parse_gen = DomAct.parse_selector(html_dom, "script#RENDER_DATA", "text")
        result_data, parse_gen = BaseAct.parse_generator(parse_gen)
        result_data = UrlAct.parse_quote(result_data)
        result_dict = JsonAct.format_json(result_data)
        if not result_dict:
            self.logger.info(f"非法数据获取(*>﹏<*)【{self.scrapeUrl}】")
            return False
        # check work_id
        blogId = self.json_first(result_dict, "$.data.itemId", 1)
        if not blogId:
            self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
            return False
        # base data
        blogUrl = f"https://www.toutiao.com/a{blogId}"
        blogCover = self.json_first(result_dict, "$.data.cover", 1)
        blogTitle = self.json_first(result_dict, "$.data.title", 1)
        blogDesc = self.json_first(result_dict, "$.data.abstract", 1)
        blogCreated = self.json_first(result_dict, "$.data.publishTime", 1)
        blogCreated = TimeAct.parse_timestring(blogCreated, "%Y-%m-%d %H:%M")
        int_gen = StrAct.parse_integer(blogCreated.timestamp())
        blogCreated, int_gen = BaseAct.parse_generator(int_gen)
        if blogCreated is False:
            blogCreated = 0
        # type 0 pic/1 video
        # check type
        blogType = 0
        # count data
        # take data and return
        if not self.isLast:
            self.isLast = 0
        self.workBase = {
            "id": blogId, "showId": blogId, "scrapeUrl": blogUrl,
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
        self.get_return(8, 1)
        return True

    def get_profile(self) -> bool:
        # @@..! must need {'ttwid': '', 's_v_web_id': ''}
        # @@..! flow need {'csrftoken': '', '__ac_signature': ''}
        # @@..! set the blacklist and whitelist
        self.blacklist = {"creator.douyin.com"}
        self.whitelist = {"www.toutiao.com"}
        if self.process_verify(self.scrapeUrl):
            self.get_return(8, 0)
            return True
        # @@... ways of parse user_id
        if self.url_path and "/c/user/" in self.url_path:
            pass
        else:
            self.logger.info(f"非法profile页面(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(8, 0)
            return True
        # @@..! set cookie
        if self.cookies:
            cookies = self.cookies.get("cookie", "")
            cookies_dict = {}
            if cookies:
                cookies = StrAct.format_clear(cookies)
                cookies = cookies.split(";")
                for i in cookies:
                    cookies_gen = StrAct.parse_regex(i, "(.*?)=")
                    name, cookies_gen = BaseAct.parse_generator(cookies_gen)
                    cookies_gen = StrAct.parse_regex(i, ".*?=(.*)")
                    value, cookies_gen = BaseAct.parse_generator(cookies_gen)
                    cookies_dict[name] = value

                self.net.set_cookie(cookies_dict)
        else:
            self.logger.info("非法cookies参数(*>﹏<*)【cookies】")
        # get profile page
        self.net.url = self.scrapeUrl
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "www.toutiao.com",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document"
        })
        if not self.net.get_response("get", is_redirect=True):
            return False
        if not self.net.get_page("text", False):
            return False
        # check 404 page
        html_dom = DomAct.parse_dom(self.net.page)
        parse_gen = DomAct.parse_selector(
            html_dom, "img[usemap*='#map']", "src")
        map404, parse_gen = BaseAct.parse_generator(parse_gen)
        if map404:
            self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(8, 0)
            return True
        # check user_id
        if self.process_verify(self.net.response.url):
            self.get_return(8, 0)
            return True
        if self.url_path.count("/") == 4:
            self.user_id = self.regex_first(self.url_path, "/user/token/(.*)")
        else:
            self.user_id = self.regex_first(self.url_path, "/user/token/(.*)/")
        if not self.user_id:
            self.logger.info(f"非法user号码(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(8, 0)
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
#######################################################################################
        cookies = self.net.get_cookie()
        csrf_token = cookies.get("csrftoken", "")
        signature = cookies.get("__ac_signature", "")
        # parse data
        html_dom = DomAct.parse_dom(self.net.page)
        parse_gen = DomAct.parse_selector(html_dom, "script#RENDER_DATA", "text")
        result_data, parse_gen = BaseAct.parse_generator(parse_gen)
        result_data = UrlAct.parse_quote(result_data)
        result_dict = JsonAct.format_json(result_data)
        if not result_dict:
            self.logger.info(f"非法数据获取(*>﹏<*)【{self.scrapeUrl}】")
            return False
        userId = self.json_first(result_dict, "$.data.profileUserInfo.userId", 1)
        accountId = self.json_first(result_dict, "$.data.profileUserInfo.mediaId", 1)
        nickname = self.json_first(result_dict, "$.data.profileUserInfo.name", 1)
        avatar = self.json_first(result_dict, "$.data.profileUserInfo.avatarUrl", 1)
        desc = self.json_first(result_dict, "$.data.profileUserInfo.description", 1)
        isAuth = self.json_first(result_dict, "$.data.profileUserInfo.userVerified", 1)
        authDetail = self.json_first(
            result_dict, "$.data.profileUserInfo.userAuthInfo.auth_info", 1)
        # format the data
        if isAuth:
            isAuth = 1
        else:
            isAuth = 2
        # count data
        self.net.url = "https://www.toutiao.com/api/pc/user/fans_stat"
        self.net.params = (("_signature", signature), )
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Accept": "application/json, text/plain, */*",
            "Host": "www.toutiao.com",
            "X-CSRFToken": csrf_token,
            "tt-anti-token": "undefined",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.toutiao.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": f"https://www.toutiao.com/c/user/token/{self.user_id}/?source=feed&tab=article",
        })
        self.net.posts = f"token={self.user_id}"
        if not self.net.get_response("post", "data"):
            return False
        if not self.net.get_page("json"):
            return False
        
        followNum = self.json_first(self.net.page, "$.data.following", 0)
        fansNum = self.json_first(self.net.page, "$.data.fans", 0)
        likeNum = self.json_first(self.net.page, "$.data.digg_count", 0)
        if fansNum is False:
            self.logger.info("非法fans数据(*>﹏<*)【cookies】")
            return False
        fansNum = StrAct.parse_millions(fansNum)
        followNum = StrAct.parse_millions(followNum)
        likeNum = StrAct.parse_millions(likeNum)
#######################################################################################
        self.homeUrl = f"https://www.toutiao.com/c/user/token/{self.user_id}/?source=feed&tab=article"
        self.scrapeUrl = self.homeUrl
        # if certify take data and return
        if self.toolType == 1:
            self.profileCounts = {'fansNum': fansNum, 'followNum': followNum}
            self.get_return(8, 1)
            return True
        # get work list
        self.net.url = "https://www.toutiao.com/api/pc/list/user/feed"
        self.net.params = (
            ("category", "pc_profile_article"), ("token", self.user_id), 
            ("max_behot_time", "0"), ("aid", "24"), 
            ("app_name", "toutiao_web"), ("_signature", signature),
        )
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Accept": "application/json, text/plain, */*",
            "Host": "www.toutiao.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": f"https://www.toutiao.com/c/user/token/{self.user_id}/?source=feed&tab=article"
        })
        if not self.net.get_response("get"):
            return False
        if self.net.code != 400:
            if not self.net.get_page("json"):
                return False
            verify = self.json_first(self.net.page, "$.data", 1)
            if not verify:
                self.logger.info("非法作品数据(*>﹏<*)【cookies】")
        
        # @@..! set isUrls is 0 and isLast is 1
        self.isLast = 1
        self.isUrls = 0
        # get blog ids list and take urls
        work_nums = 10
        if self.toolType == 2:
            work_nums = 5
        # check if code is 400
        if self.net.code != 400:
            blog_gen = JsonAct.parse_json(self.net.page, f"$.data[:{work_nums}]")
            for i in blog_gen:
                # get id and check
                # cell_type = self.json_first(i, "$.cell_type", 1)
                # cell_type 60文章/32微头条/0西瓜视频/202问答
                blogId = self.json_first(i, "$.item_id", 0)
                if not blogId:
                    self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
                    continue
                blogUrl = f"https://www.toutiao.com/a{blogId}"
                # @@..! take url list
                self.workUrls.append(blogUrl)
                # base data
                blogCover = self.json_first(i, "$.image_list[0].url", 1)
                blogTitle = self.json_first(i, "$.title", 1)
                blogDesc = self.json_first(i, "$.abstract", 1)
                blogTitle = StrAct.format_clear(blogTitle, True)
                blogDesc = StrAct.format_clear(blogDesc, True)
                blogCreated = self.json_number(i, "$.publish_time", 1)
                # type 0 pic/1 video
                blogPicUrl = []
                pic_gen = JsonAct.parse_json(i, "$.image_list.*.url")  
                for p in pic_gen:
                    blogPicUrl.append(p)
                blogPicNum = len(blogPicUrl)
                # check type
                blogType = 0
                # count data
                blogLike = self.json_number(i, "$.digg_count", 1)
                blogComment = self.json_number(i, "$.comment_count", 1)
                blogForward = self.json_number(i, "$.forward_info.forward_count", 1)
                blogView = self.json_number(i, "$.read_count", 1)
                # take data and return
                self.workBase = {
                    "id": blogId, "showId": blogId, "scrapeUrl": blogUrl,
                    "url": blogUrl, "uid": "", "nickname": "",
                    "type": blogType, "title": blogTitle, "cover": blogCover,
                    "created": blogCreated, "source": "", "extra": "",
                    "desc": blogDesc, "duration": 0, "videoUrl": "",
                    "picNum": blogPicNum, "picUrl": blogPicUrl,

                    "likeNum": blogLike, "commentNum": blogComment, 
                    "shareNum": blogForward, "forwardNum": blogForward, 
                    "collectNum": 0, "playNum": 0, "viewNum": blogView,
                    "rewardNum": 0, "danmakuNum": 0, "blogRepost": {}
                }
                # if tool type is not 1, take list
                if self.toolType != 1:
                    self.workList.append(self.workBase)

        # @@..! matchUid -> userId
        # take base and counts data and return
        self.profileBase = {
            "matchUid": userId, "userId": userId, "accountId": accountId,
            "secId": "", "avatar": avatar, "qrCode": "", "nickname": nickname,
            "field": "", "isMember": 0, "isAuth": isAuth,
            "gender": 0, "age": "", "birth": "", "constellation": "",
            "area": "", "notice": "", "desc": desc,
            "memberLevel": "", "memberType": "", "memberDetail": "",
            "authLevel": "", "authType": "", "authDetail": str(authDetail),
            "isCompany": 0, "isGovernmentMedia": 0
        }
        
        self.profileCounts = {
            "fansNum": fansNum, "followNum": followNum,
            "videos": 0, "blogs": 0, "worksNum": 0,
            "favoriteNum": 0, "collectNum": 0, "likeNum": likeNum,
            "playNum": 0, "viewNum": 0, "rewardNum": 0
        }

        self.get_return(8, 1)
        return True










 






   

