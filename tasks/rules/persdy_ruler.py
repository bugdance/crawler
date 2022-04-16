#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> douyin ruler
@@..> package tasks.rules
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> base import
from dataclasses import dataclass, field
# @@..> import utils
from .base_ruler import BaseWorker, BaseAct, DomAct, JsonAct, UrlAct, StrAct


@dataclass
class PersDYWorker(BaseWorker):
    """
    [douyin web scrape]
    """
    sec_uid: str = field(default_factory=str)

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
        self.whitelist = {"amemv.com", "iesdouyin.com", 
                          "v.douyin.com", "www.douyin.com"}
        if self.process_verify(self.scrapeUrl):
            self.get_return(1, 0)
            return True
        # @@... ways of parse user_id
        if "www.douyin.com" in self.url_domain:
            self.work_id = self.regex_first(self.url_path, "/video/(\\d+)")

        elif "v.douyin.com" in self.url_domain:
            self.net.url = self.scrapeUrl
            self.net.headers = BaseAct.format_copy(self.init_header)
            self.net.headers.update({
                "Host": "v.douyin.com",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Dest": "document",
            })
            if not self.net.get_response("get"):
                return False
            if not self.net.get_page("text", False):
                return False
            # parse next jump
            html_dom = DomAct.parse_dom(self.net.page)
            redirect_gen = DomAct.parse_selector(html_dom, "a", "href")
            redirect_url, redirect_gen = BaseAct.parse_generator(redirect_gen)
            if redirect_url is False or self.process_verify(redirect_url):
                self.logger.info(f"非法v.douyin跳转(*>﹏<*)【{self.scrapeUrl}】")
                self.get_return(1, 0)
                return True
            # check 404 page
            if "/404" in self.url_path:
                self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
                self.get_return(1, 0)
                return True
            # parse work_id
            self.work_id = self.regex_first(self.url_path, "/video/(\\d+)")
        # check work_id
        if self.work_id is False:
            self.logger.info(f"非法work号码(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(1, 0)
            return True
        # @@..! return false is do nothing
        return False

    def process_work(self):
        # after get work_id, get work page
        self.net.url = f"https://www.iesdouyin.com/web/api/v2/aweme/iteminfo/?" \
                       f"item_ids={self.work_id}&dytk=a422d4b0c0747e501b0d6a389fb83f06"
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "www.iesdouyin.com",
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Accept-Encoding": "",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
        })
        if not self.net.get_response("get"):
            return False
        if not self.net.get_page("json"):
            return False
        result_gen = JsonAct.parse_json(self.net.page, "$.item_list.*")
        for i in result_gen:
            # parse data and check
            videoId = self.json_first(i, "$.aweme_id", 0)
            if not videoId:
                self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
                continue
            # base data
            videoUrl = f"https://www.douyin.com/video/{videoId}"
            videoCover = self.json_first(i, "$.video.dynamic_cover.url_list[0]", 1)
            if not videoCover:
                videoCover = self.json_first(i, "$.video.cover.url_list[0]", 1)
            videoTitle = self.json_first(i, "$.desc", 1)
            videoStream = self.json_first(i, "$.video.play_addr.url_list[0]", 1)
            videoDuration = self.json_number(i, "$.video.duration", 1)
            videoCreated = self.json_number(i, "$.create_time", 1)
            videoExtra = self.json_first(i, "$.text_extra", 1)
            if videoExtra and isinstance(videoExtra, list):
                extra_list = []
                for t in videoExtra:
                    extra_list.append(t.get("hashtag_name"))
                videoExtra = ",".join(extra_list)
            else:
                videoExtra = ""
            # count data
            videoShare = self.json_number(i, "$.statistics.share_count", 1)
            videoLike = self.json_number(i, "$.statistics.digg_count", 1)
            videoComment = self.json_number(i, "$.statistics.comment_count", 1)
            # take data and return
            self.workBase = {
                "id": videoId, "showId": videoId, "scrapeUrl": videoUrl,
                "url": videoUrl, "uid": "", "nickname": "",
                "type": 1, "title": videoTitle, "cover": videoCover,
                "created": videoCreated, "source": "", "extra": videoExtra, 
                "desc": "", "duration": videoDuration, "videoUrl": videoStream,
                "picNum": 0, "picUrl": [],
                
                "likeNum": videoLike, "commentNum": videoComment,
                "shareNum": videoShare, "forwardNum": videoShare,
                "collectNum": 0, "playNum": 0, "viewNum": 0, 
                "rewardNum": 0, "danmakuNum": 0, "blogRepost": {},
            }
            # if tool type is not 1, take list
            if self.toolType != 1:
                self.workList.append(self.workBase)
        # set isLast is 1
        self.isLast = 1
        self.get_return(1, 1)
        return True

    def get_profile(self) -> bool:
        # @@..! the www.douyin.com at least need {'__ac_nonce': '', '__ac_signature': ''}
        # @@..! the sec_uid of url can't change
        # @@..! set the blacklist and whitelist
        self.blacklist = {"creator.douyin.com"}
        self.whitelist = {"amemv.com", "iesdouyin.com",
                          "v.douyin.com", "www.douyin.com", "t.cn"}
        if self.process_verify(self.scrapeUrl):
            self.get_return(1, 0)
            return True
        # @@... ways of parse user_id
        if "www.douyin.com" in self.url_domain and "/user/" in self.url_path:
            self.sec_uid = self.regex_first(self.url_path, "/user/(.*)")

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

            self.net.url = self.scrapeUrl
            self.net.headers = BaseAct.format_copy(self.init_header)
            self.net.headers.update({
                "Host": "www.douyin.com",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-User": "?1"
            })
            if not self.net.get_response("get"):
                return False
            if not self.net.get_page("text", False):
                return False
            # parse data
            html_dom = DomAct.parse_dom(self.net.page)
            data_gen = DomAct.parse_selector(html_dom, "script#RENDER_DATA", "text")
            result_data, data_gen = BaseAct.parse_generator(data_gen)
            result_data = UrlAct.parse_quote(result_data)
            result_dict = JsonAct.format_json(result_data)
            if not result_dict:
                self.logger.info(f"非法www.douyin抓取(*>﹏<*)【{self.scrapeUrl}】")
                return False

            self.user_id = self.json_first(result_dict, "$.*.user.user.uid", 0)

        else:
            # @@..! change the url
            if "t.cn" in self.url_domain:
                self.net.url = self.scrapeUrl
                self.net.headers = BaseAct.format_copy(self.init_header)
                self.net.headers.update({
                    "Host": "t.cn",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-User": "?1",
                    "Sec-Fetch-Dest": "document",
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
                    self.logger.info(f"非法t.cn跳转(*>﹏<*)【{self.scrapeUrl}】")
                    self.get_return(1, 0)
                    return True
                # @@..! get scrape url
                self.scrapeUrl = redirect_url

            if "v.douyin.com" in self.url_domain:
                self.net.url = self.scrapeUrl
                self.net.headers = BaseAct.format_copy(self.init_header)
                self.net.headers.update({
                    "Host": "v.douyin.com",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Dest": "document",
                })
                if not self.net.get_response("get"):
                    return False
                if not self.net.get_page("text", False):
                    return False
                # parse next jump
                html_dom = DomAct.parse_dom(self.net.page)
                redirect_gen = DomAct.parse_selector(html_dom, "a", "href")
                redirect_url, redirect_gen = BaseAct.parse_generator(redirect_gen)
                if redirect_url is False or self.process_verify(redirect_url):
                    self.logger.info(f"非法v.douyin跳转(*>﹏<*)【{self.scrapeUrl}】")
                    self.get_return(1, 0)
                    return True
            # check 404 page
            if "/404" in self.url_path:
                self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
                self.get_return(1, 0)
                return True
            # parse user_id and sec_uid
            self.sec_uid = self.regex_first(self.url_path, "/share/user/(.*)")
            # check if is all number
            if self.sec_uid.isdigit():
                for i, v in self.url_dict.items():
                    if "sec_uid" in i:
                        self.sec_uid = v[0]
        # check user_id and sec_uid
        if not self.sec_uid:
            self.logger.info(f"非法user号码(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(1, 0)
            return True
        # @@..! return false is do nothing
        return False
    
    
#     # @@..! new web
#     def process_profile(self) -> bool:
#         # get user_id
#         if self.get_profile():
#             return True
#         else:
#             if not self.sec_uid:
#                 self.logger.info(f"非法user号码(*>﹏<*)【{self.user_id}】")
#                 return False
#         # after get user_id, get profile page
#         # self.homeUrl = f"https://www.iesdouyin.com/share/user/" \
#         #                f"{self.user_id}?sec_uid={self.sec_uid}"
#         # get info data
#         self.net.url = f"https://www.iesdouyin.com/web/api/v2/" \
#                        f"user/info/?sec_uid={self.sec_uid}"
#         self.net.headers = BaseAct.format_copy(self.init_header)
#         self.net.headers.update({
#             "Host": "www.iesdouyin.com",
#             "Accept": "application/json",
#             "X-Requested-With": "XMLHttpRequest",
#             "Referer": self.homeUrl,
#             "Accept-Encoding": "",
#             "Sec-Fetch-Site": "same-origin",
#             "Sec-Fetch-Mode": "cors",
#             "Sec-Fetch-Dest": "empty",
#         })
#         if not self.net.get_response("get"):
#             return False
#         if not self.net.get_page("json"):
#             return False
#         # check user_id
#         userId = self.json_first(self.net.page, "$.user_info.uid", 0)
#         if not userId:
#             self.logger.info("非法user号码(*>﹏<*)【page】")
#             self.get_return(1, 0)
#             return True
#         userId = str(userId)
#         # @@..! parse data, the douyin id default is not short id
#         accountId = self.json_first(self.net.page, "$.user_info.unique_id", 1)
#         if not accountId:
#             accountId = self.json_first(self.net.page, "$.user_info.short_id", 1)
#         accountId = str(accountId)
#         avatar = self.json_first(
#             self.net.page, "$.user_info.avatar_thumb.url_list[0]", 1)
#         nickname = self.json_first(self.net.page, "$.user_info.nickname", 1)
#         desc = self.json_first(self.net.page, "$.user_info.signature", 1)
#         authType = self.json_number(self.net.page, "$.user_info.verification_type", 1)
#         authDetail = self.json_first(self.net.page, "$.user_info.custom_verify", 1)
#         isCompany = self.json_first(self.net.page, "$.user_info.is_enterprise_vip", 1)
#         isGovernmentMedia = self.json_first(
#             self.net.page, "$.user_info.is_gov_media_vip", 1)
#         # format the data
#         if authDetail:
#             isAuth = 1
#         else:
#             isAuth = 2
#         if isCompany:
#             isCompany = 1
#         else:
#             isCompany = 2
#         if isGovernmentMedia:
#             isGovernmentMedia = 1
#         else:
#             isGovernmentMedia = 2
#         # count data
#         followNum = self.json_number(self.net.page, "$.user_info.following_count", 1)
#         fansNum = self.json_number(self.net.page, "$.user_info.follower_count", 1)
#         videos = self.json_number(self.net.page, "$.user_info.aweme_count", 1)
#         favoriteNum = self.json_number(self.net.page, "$.user_info.favoriting_count", 1)
#         likeNum = self.json_number(self.net.page, "$.user_info.total_favorited", 1)
        
#         # @@..! get new fans num
#         # @@..! set cookie
#         if self.cookies:
#             self.net.set_cookie(self.cookies)
#         else:
#             self.logger.info("非法cookies参数(*>﹏<*)【cookies】")

#         self.net.url = f"https://www.douyin.com/user/{self.sec_uid}?previous_page=app_code_link"
#         self.net.headers = BaseAct.format_copy(self.init_header)
#         self.net.headers.update({
#             "Host": "www.douyin.com",
#             "Upgrade-Insecure-Requests": "1",
#             "Sec-Fetch-Site": "none",
#             "Sec-Fetch-Mode": "navigate",
#             "Sec-Fetch-Dest": "document",
#             "Sec-Fetch-User": "?1"
#         })
#         if not self.net.get_response("get"):
#             return False
#         if not self.net.get_page("text", False):
#             return False
#         # parse data
#         html_dom = DomAct.parse_dom(self.net.page)
#         data_gen = DomAct.parse_selector(html_dom, "script#RENDER_DATA", "text")
#         result_data, data_gen = BaseAct.parse_generator(data_gen)
#         result_data = UrlAct.parse_quote(result_data)
#         result_dict = JsonAct.format_json(result_data)
#         if not result_dict:
#             self.logger.info(f"非法www.douyin抓取(*>﹏<*)【{self.scrapeUrl}】")
#             return False
#         fansNum = self.json_number(result_dict, "$.*.user.user.mplatformFollowersCount", 0)
#         if not fansNum:
#             self.logger.info(f"非法www.douyin抓取(*>﹏<*)【{self.scrapeUrl}】")
#             return False
# #######################################################################################
#         self.scrapeUrl = f"https://www.iesdouyin.com/share/user/" \
#                          f"{userId}?sec_uid={self.sec_uid}"
#         self.homeUrl = self.scrapeUrl
#         # if certify take data and return
#         if self.toolType == 1:
#             self.profileCounts = {'fansNum': fansNum, 'followNum': followNum}
#             self.get_return(1, 1)
#             return True
#         # get video ids list and take urls
#         # @@..! set isUrls is 0 and isLast is 1
#         self.isUrls = 0
#         self.isLast = 1
#         work_nums = 10
#         if self.toolType == 2:
#             work_nums = 5
#         video_gen = JsonAct.parse_json(result_dict, f"$.*.post.data[:{work_nums}]")
#         for i in video_gen:
#             # get id and check
#             videoId = self.json_first(i, "$.awemeId", 0)
#             if not videoId:
#                 self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
#                 continue
            
#             videoUrl = f"https://www.douyin.com/video/{videoId}"
#             videoCover = self.json_first(i, "$.video.dynamicCover", 1)
#             if not videoCover:
#                 videoCover = self.json_first(i, "$.video.cover", 1)
#             if videoCover and not videoCover.startswith("http"):
#                 videoCover = "https:" + videoCover
                
#             videoTitle = self.json_first(i, "$.desc", 1)
#             videoStream = self.json_first(i, "$.video.playAddr.[0].src", 1)
#             if videoStream and not videoStream.startswith("http"):
#                 videoStream = "https:" + videoStream

#             videoDuration = self.json_number(i, "$.video.duration", 1)
#             videoCreated = self.json_number(i, "$.createTime", 1)
#             videoExtra = self.json_first(i, "$.textExtra", 1)
#             videoDesc = self.json_first(i, "$.desc", 1)
#             if videoExtra and isinstance(videoExtra, list):
#                 extra_list = []
#                 for t in videoExtra:
#                     extra_list.append(t.get("hashtagName"))
#                 videoExtra = ",".join(extra_list)
#             else:
#                 videoExtra = ""
#             # count data
#             videoShare = self.json_number(i, "$.stats.shareCount", 1)
#             videoLike = self.json_number(i, "$.stats.diggCount", 1)
#             videoComment = self.json_number(i, "$.stats.commentCount", 1)
#             # take data and return
#             self.workBase = {
#                 "id": videoId, "showId": videoId, "scrapeUrl": videoUrl,
#                 "url": videoUrl, "uid": "", "nickname": "",
#                 "type": 1, "title": videoTitle, "cover": videoCover,
#                 "created": videoCreated, "source": "", "extra": videoExtra, 
#                 "desc": videoDesc, "duration": videoDuration, 
#                 "videoUrl": videoStream,
#                 "picNum": 0, "picUrl": [],
                
#                 "likeNum": videoLike, "commentNum": videoComment,
#                 "shareNum": videoShare, "forwardNum": videoShare,
#                 "collectNum": 0, "playNum": 0, "viewNum": 0, 
#                 "rewardNum": 0, "danmakuNum": 0, "blogRepost": {},
#             }
#             # if tool type is not 1, take list
#             if self.toolType != 1:
#                 self.workList.append(self.workBase)
#         # @@..! matchUid -> accountId
#         # take base and counts data and return
#         self.profileBase = {
#             "matchUid": accountId, "userId": userId, "accountId": accountId,
#             "secId": self.sec_uid, "avatar": avatar, "qrCode": "",
#             "nickname": nickname, "field": "", "isMember": 0, "isAuth": isAuth,
#             "gender": 0, "age": "", "birth": "", "constellation": "",
#             "area": "", "notice": "", "desc": desc,
#             "memberLevel": "", "memberType": "", "memberDetail": "",
#             "authLevel": "", "authType": str(authType), "authDetail": str(authDetail),
#             "isCompany": isCompany, "isGovernmentMedia": isGovernmentMedia
#         }
#         self.profileCounts = {
#             "fansNum": fansNum, "followNum": followNum,
#             "videos": videos, "blogs": 0, "worksNum": videos,
#             "favoriteNum": favoriteNum, "collectNum": 0, "likeNum": likeNum,
#             "playNum": 0, "viewNum": 0, "rewardNum": 0
#         }

#         self.get_return(1, 1)
#         return True


    def process_profile(self) -> bool:
        # get user_id
        if self.get_profile():
            return True
        else:
            if not self.sec_uid:
                self.logger.info(f"非法user号码(*>﹏<*)【{self.user_id}】")
                return False
        # after get user_id, get profile page
        # self.homeUrl = f"https://www.iesdouyin.com/share/user/" \
        #                f"{self.user_id}?sec_uid={self.sec_uid}"
        # get info data
        self.net.url = f"https://www.iesdouyin.com/web/api/v2/" \
                       f"user/info/?sec_uid={self.sec_uid}"
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "www.iesdouyin.com",
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": self.homeUrl,
            "Accept-Encoding": "",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
        })
        if not self.net.get_response("get"):
            return False
        if not self.net.get_page("json"):
            return False
        # check user_id
        userId = self.json_first(self.net.page, "$.user_info.uid", 0)
        if not userId:
            self.logger.info("非法user号码(*>﹏<*)【page】")
            self.get_return(1, 0)
            return True
        userId = str(userId)
        # @@..! parse data, the douyin id default is not short id
        accountId = self.json_first(self.net.page, "$.user_info.unique_id", 1)
        if not accountId:
            accountId = self.json_first(self.net.page, "$.user_info.short_id", 1)
        accountId = str(accountId)
        avatar = self.json_first(
            self.net.page, "$.user_info.avatar_thumb.url_list[0]", 1)
        nickname = self.json_first(self.net.page, "$.user_info.nickname", 1)
        desc = self.json_first(self.net.page, "$.user_info.signature", 1)
        authType = self.json_number(self.net.page, "$.user_info.verification_type", 1)
        authDetail = self.json_first(self.net.page, "$.user_info.custom_verify", 1)
        isCompany = self.json_first(self.net.page, "$.user_info.is_enterprise_vip", 1)
        isGovernmentMedia = self.json_first(
            self.net.page, "$.user_info.is_gov_media_vip", 1)
        # format the data
        if authDetail:
            isAuth = 1
        else:
            isAuth = 2
        if isCompany:
            isCompany = 1
        else:
            isCompany = 2
        if isGovernmentMedia:
            isGovernmentMedia = 1
        else:
            isGovernmentMedia = 2
        # count data
        followNum = self.json_number(self.net.page, "$.user_info.following_count", 1)
        fansNum = self.json_number(self.net.page, "$.user_info.follower_count", 1)
        videos = self.json_number(self.net.page, "$.user_info.aweme_count", 1)
        favoriteNum = self.json_number(self.net.page, "$.user_info.favoriting_count", 1)
        likeNum = self.json_number(self.net.page, "$.user_info.total_favorited", 1)
#######################################################################################
        self.scrapeUrl = f"https://www.iesdouyin.com/share/user/" \
                         f"{userId}?sec_uid={self.sec_uid}"
        self.homeUrl = self.scrapeUrl
        # if certify take data and return
        if self.toolType == 1:
            self.profileCounts = {'fansNum': fansNum, 'followNum': followNum}
            self.get_return(1, 1)
            return True
        # video data
        self.net.url = f"https://www.iesdouyin.com/web/api/v2/aweme/post/?" \
                       f"sec_uid={self.sec_uid}&count=21&max_cursor=0&aid=1128" \
                       f"&_signature=eqgUTQAAGoiScjYwE-WQ53qoFF&dytk="
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "www.iesdouyin.com",
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": self.homeUrl,
            "Accept-Encoding": "",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
        })
        if not self.net.get_response("get"):
            return False
        if not self.net.get_page("json"):
            return False
        # get video ids list and take urls
        # @@..! set isUrls is 0 and isLast is 1
        self.isUrls = 0
        self.isLast = 1
        work_nums = 10
        if self.toolType == 2:
            work_nums = 5
        video_gen = JsonAct.parse_json(
            self.net.page, f"$.aweme_list.[:{work_nums}].aweme_id")
        video_list = list(video_gen)
        for i in video_list:
            self.workUrls.append(f"https://www.douyin.com/video/{i}")
        if video_list:
            self.work_id = ",".join(video_list)
            # @@..! do not return
            self.process_work()
        # @@..! matchUid -> accountId
        # take base and counts data and return
        self.profileBase = {
            "matchUid": accountId, "userId": userId, "accountId": accountId,
            "secId": self.sec_uid, "avatar": avatar, "qrCode": "",
            "nickname": nickname, "field": "", "isMember": 0, "isAuth": isAuth,
            "gender": 0, "age": "", "birth": "", "constellation": "",
            "area": "", "notice": "", "desc": desc,
            "memberLevel": "", "memberType": "", "memberDetail": "",
            "authLevel": "", "authType": str(authType), "authDetail": str(authDetail),
            "isCompany": isCompany, "isGovernmentMedia": isGovernmentMedia
        }
        self.profileCounts = {
            "fansNum": fansNum, "followNum": followNum,
            "videos": videos, "blogs": 0, "worksNum": videos,
            "favoriteNum": favoriteNum, "collectNum": 0, "likeNum": likeNum,
            "playNum": 0, "viewNum": 0, "rewardNum": 0
        }

        self.get_return(1, 1)
        return True
