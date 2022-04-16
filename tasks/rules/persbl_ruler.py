#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> bilibili ruler
@@..> package tasks.rules
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> base import
from dataclasses import dataclass, field
# @@..> import utils
from .base_ruler import BaseWorker, BaseAct, DomAct, JsonAct


@dataclass
class PersBLWorker(BaseWorker):
    """
    [bilibili web scrape]
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
        # @@..! the login process at least need {'SESSDATA': ''}
        # @@..! set the blacklist and whitelist
        self.blacklist = {"video.bilibili.com", "search.bilibili.com",
                          "space.bilibili.com", "m.bilibili.com"}
        self.whitelist = {"www.bilibili.com", "b23.tv"}
        if self.process_verify(self.scrapeUrl):
            self.get_return(3, 0)
            return True
        # @@... ways of parse work_id
        if "www.bilibili.com" in self.url_domain and self.url_path:
            self.work_id = self.regex_first(self.url_path, "/video/(.*)")

        elif "b23.tv" in self.url_domain and self.url_path:
            self.net.url = self.scrapeUrl
            self.net.headers = BaseAct.format_copy(self.init_header)
            self.net.headers.update({
                "Host": "b23.tv",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Dest": "document"
            })
            if not self.net.get_response("get"):
                return False
            if not self.net.get_page("text", False, 302):
                return False
            # parse next jump
            html_dom = DomAct.parse_dom(self.net.page)
            redirect_gen = DomAct.parse_selector(html_dom, "a", "href")
            redirect_url, redirect_gen = BaseAct.parse_generator(redirect_gen)
            if redirect_url is False or self.process_verify(redirect_url):
                self.logger.info(f"非法b23.tv跳转(*>﹏<*)【{self.scrapeUrl}】")
                self.get_return(3, 0)
                return True
            if "www.bilibili.com" in self.url_domain and self.url_path:
                self.work_id = self.regex_first(self.url_path, "/video/(.*)")

            else:
                self.logger.info(f"非法b23.tv跳转(*>﹏<*)【{self.scrapeUrl}】")
                self.get_return(3, 0)
                return True
        else:
            self.logger.info(f"非法url链接(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(3, 0)
            return True
        # check work_id
        if self.work_id is False:
            self.logger.info(f"非法work号码(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(3, 0)
            return True
        # @@..! return false is do nothing
        return False

    def process_work(self) -> bool:
        # after get work_id, get work page
        videoUrl = f"https://www.bilibili.com/video/{self.work_id}"
        self.net.url = videoUrl
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "www.bilibili.com",
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
#######################################################################################
        # parse data and check
        regex_string = self.regex_first(
            self.net.page, "__INITIAL_STATE__\\s{0,}=\\s{0,}({.*?})\\s{0,};")
        regex_dict = JsonAct.format_json(regex_string)
        if not regex_dict:
            self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
            return False
        videoId = self.json_first(regex_dict, "$.videoData.bvid", 0)
        if not videoId:
            self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
            return False
        # base data
        videoCover = self.json_first(regex_dict, "$.videoData.pic", 1)
        videoTitle = self.json_first(regex_dict, "$.videoData.title", 1)
        videoDesc = self.json_first(regex_dict, "$.videoData.desc", 1)
        videoCreated = self.json_number(regex_dict, "$.videoData.pubdate", 1)
        videoDuration = self.json_number(regex_dict, "$.videoData.duration", 1)
        # count data
        videoPlay = self.json_number(regex_dict, "$.videoData.stat.view", 1)
        videoComment = self.json_number(regex_dict, "$.videoData.stat.reply", 1)
        videoLike = self.json_number(regex_dict, "$.videoData.stat.like", 1)
        videoShare = self.json_number(regex_dict, "$.videoData.stat.share", 1)
        videoCollect = self.json_number(regex_dict, "$.videoData.stat.favorite", 1)
        videoCoin = self.json_number(regex_dict, "$.videoData.stat.coin", 1)
        videoDanmaku = self.json_number(regex_dict, "$.videoData.stat.danmaku", 1)
        # take data and return
        if not self.isLast:
            self.isLast = 0

        self.workBase = {
            "id": videoId, "showId": videoId, "scrapeUrl": videoUrl,
            "url": videoUrl, "uid": "", "nickname": "",
            "type": 1, "title": videoTitle, "cover": videoCover,
            "created": videoCreated, "source": "", "extra": "", 
            "desc": videoDesc, "duration": videoDuration, "videoUrl": "",
            "picNum": 0, "picUrl": [],
            
            "likeNum": videoLike, "commentNum": videoComment,
            "shareNum": videoShare, "forwardNum": videoShare,
            "collectNum": videoCollect, "playNum": videoPlay, "viewNum": 0, 
            "rewardNum": videoCoin, "danmakuNum": videoDanmaku, "blogRepost": {},
        }
        self.get_return(3, 1)
        return True

    def get_profile(self) -> bool:
        # @@..! the login process at least need {'SESSDATA': ''}
        # @@..! set the blacklist and whitelist
        self.blacklist = {"video.bilibili.com", "search.bilibili.com"}
        self.whitelist = {"space.bilibili.com", "m.bilibili.com", "b23.tv"}
        if self.process_verify(self.scrapeUrl):
            self.get_return(3, 0)
            return True
        # @@... ways of parse user_id
        if "space.bilibili.com" in self.url_domain and self.url_path:
            self.user_id = self.regex_first(self.url_path, "/(\\d+)")

        elif "m.bilibili.com" in self.url_domain and \
                self.url_path.startswith("/space/"):

            self.user_id = self.regex_first(self.url_path, "/space/(\\d+)")
        elif "b23.tv" in self.url_domain and self.url_path:
            self.net.url = self.scrapeUrl
            self.net.headers = BaseAct.format_copy(self.init_header)
            self.net.headers.update({
                "Host": "b23.tv",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Dest": "document"
            })
            if not self.net.get_response("get"):
                return False
            if not self.net.get_page("text", False, 302):
                return False
            # parse next jump
            html_dom = DomAct.parse_dom(self.net.page)
            redirect_gen = DomAct.parse_selector(html_dom, "a", "href")
            redirect_url, redirect_gen = BaseAct.parse_generator(redirect_gen)
            if redirect_url is False or self.process_verify(redirect_url):
                self.logger.info(f"非法b23.tv跳转(*>﹏<*)【{self.scrapeUrl}】")
                self.get_return(3, 0)
                return True
            if "space.bilibili.com" in self.url_domain and self.url_path:
                self.user_id = self.regex_first(self.url_path, "/(\\d+)")

            else:
                self.logger.info(f"非法b23.tv跳转(*>﹏<*)【{self.scrapeUrl}】")
                self.get_return(3, 0)
                return True
        else:
            self.logger.info(f"非法url链接(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(3, 0)
            return True
        # check user_id
        if self.user_id is False:
            self.logger.info(f"非法user号码(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(3, 0)
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
        # @@..! set cookie
        if self.cookies:
            self.net.set_cookie(self.cookies)
        else:
            self.logger.info("非法cookies参数(*>﹏<*)【cookies】")
        # after get user_id, get profile page
        self.homeUrl = f"https://space.bilibili.com/{self.user_id}"

        self.net.url = self.homeUrl
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "space.bilibili.com",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document"
        })
        if not self.net.get_response("get"):
            return False
        # check 404 page
        if self.net.code == 404:
            self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(3, 0)
            return True
        if not self.net.get_page("text"):
            return False
#######################################################################################
        # get info data
        self.net.url = f"https://api.bilibili.com/x/space/acc/info?" \
                       f"mid={self.user_id}&jsonp=jsonp"
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "api.bilibili.com",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://space.bilibili.com",
            "Referer": "https://space.bilibili.com/",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty"
        })
        if not self.net.get_response("get"):
            return False
        if not self.net.get_page("json"):
            return False
        # check user_id
        userId = self.json_first(self.net.page, "$.data.mid", 0)
        if not userId and userId != self.user_id:
            self.logger.info("非法user号码(*>﹏<*)【page】")
            self.get_return(3, 0)
            return True
        userId = str(userId)
        # parse data
        nickname = self.json_first(self.net.page, "$.data.name", 1)
        avatar = self.json_first(self.net.page, "$.data.face", 1)
        gender = self.json_first(self.net.page, "$.data.sex", 1)
        birth = self.json_first(self.net.page, "$.data.birthday", 1)
        desc = self.json_first(self.net.page, "$.data.sign", 1)
        memberLevel = self.json_first(self.net.page, "$.data.level", 1)
        memberType = self.json_number(self.net.page, "$.data.vip.type", 1)
        memberDetail = self.json_first(self.net.page, "$.data.vip.label.text", 1)
        authDetail = self.json_first(self.net.page, "$.data.official.title", 1)
        # format the data
        if "女" in gender:
            gender = 2
        elif "男" in gender:
            gender = 1
        else:
            gender = 0
        if memberLevel:
            isMember = 1
        else:
            isMember = 2
        if memberType == 1:
            memberDetail = "普通会员"
        if authDetail:
            isAuth = 1
        else:
            isAuth = 2
#######################################################################################
        self.scrapeUrl = f"https://space.bilibili.com/{self.user_id}"
        # fans data
        self.net.url = f"https://api.bilibili.com/x/relation/stat?" \
                       f"vmid={self.user_id}&jsonp=jsonp"
        if not self.net.get_response("get"):
            return False
        if not self.net.get_page("json"):
            return False
        fansNum = self.json_number(self.net.page, "$.data.follower", 1)
        followNum = self.json_number(self.net.page, "$.data.following", 1)
        # if certify take data and return
        if self.toolType == 1:
            self.profileCounts = {'fansNum': fansNum, 'followNum': followNum}
            self.get_return(3, 1)
            return True
        # notice data
        self.net.url = f"https://api.bilibili.com/x/space/notice?" \
                       f"mid={self.user_id}&jsonp=jsonp"
        if not self.net.get_response("get"):
            return False
        if not self.net.get_page("json"):
            return False
        notice = self.json_first(self.net.page, "$.data", 1)
        # field data
        self.net.url = f"https://api.bilibili.com/x/space/acc/tags?" \
                       f"mid={self.user_id}&jsonp=jsonp"
        if not self.net.get_response("get"):
            return False
        if not self.net.get_page("json"):
            return False
        fields = self.json_first(self.net.page, "$.data[0].tags", 1)
        if fields and isinstance(fields, list):
            fields = ",".join(fields)
        else:
            fields = ""
        # @@..! play data, must login
        self.net.url = f"https://api.bilibili.com/x/space/upstat?" \
                       f"mid={self.user_id}&jsonp=jsonp"
        if not self.net.get_response("get"):
            return False
        if not self.net.get_page("json"):
            return False
        likeNum = self.json_number(self.net.page, "$.data.likes", 0)
        playNum = self.json_number(self.net.page, "$.data.archive.view", 0)
        # charging data
        self.net.url = f"https://elec.bilibili.com/api/query.rank.do?" \
                       f"mid={self.user_id}&jsonp=jsonp"
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "elec.bilibili.com",
            "Accept": "*/*",
            "Referer": "https://space.bilibili.com/",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Dest": "script"
        })
        if not self.net.get_response("get"):
            return False
        if not self.net.get_page("json"):
            return False
        totalChargingNum = self.json_number(self.net.page, "$.data.total_count", 1)
        # video data
        self.net.url = f"https://api.bilibili.com/x/space/arc/search?" \
                       f"mid={self.user_id}&pn=1&ps=25&index=1&jsonp=jsonp"
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "api.bilibili.com",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://space.bilibili.com",
            "Referer": "https://space.bilibili.com/",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty"
        })
        if not self.net.get_response("get"):
            return False
        if not self.net.get_page("json"):
            return False
        videos = self.json_number(self.net.page, "$.data.page.count", 1)
        # get video ids list and take urls
        self.isLast = 0
        self.isUrls = 1
        work_nums = 10
        if self.toolType == 2:
            work_nums = 5
        video_gen = JsonAct.parse_json(
            self.net.page, f"$.data.list.vlist.[:{work_nums}].bvid")
        for i in video_gen:
            self.workUrls.append(f"https://www.bilibili.com/video/{i}")
        if not self.workUrls:
            self.isLast = 1
            self.isUrls = 0
        # @@..! matchUid -> userId
        # take base and counts data and return
        self.profileBase = {
            "matchUid": userId, "userId": userId, "accountId": userId,
            "secId": "", "avatar": avatar, "qrCode": "", "nickname": nickname,
            "field": fields, "isMember": isMember, "isAuth": isAuth,
            "gender": gender, "age": "", "birth": birth, "constellation": "",
            "area": "", "notice": notice, "desc": desc,
            "memberLevel": str(memberLevel), "memberType": str(memberType),
            "memberDetail": str(memberDetail),
            "authLevel": "", "authType": "", "authDetail": str(authDetail),
            "isCompany": 0, "isGovernmentMedia": 0
        }
        self.profileCounts = {
            "fansNum": fansNum, "followNum": followNum,
            "videos": videos, "blogs": 0, "worksNum": videos,
            "favoriteNum": 0, "collectNum": 0, "likeNum": 0,
            "playNum": 0, "viewNum": 0, "rewardNum": totalChargingNum
        }

        # @@..! check login data and return
        if likeNum is False:
            self.logger.info("非法user登录(*>﹏<*)【cookies】")
        else:
            self.profileCounts['likeNum'] = likeNum
            self.profileCounts['playNum'] = playNum

        self.get_return(3, 1)
        return True
