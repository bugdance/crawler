#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> kuaishou ruler
@@..> package tasks.rules
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> base import
from dataclasses import dataclass, field
# @@..> import utils
from .base_ruler import BaseWorker, BaseAct, DomAct, JsonAct, StrAct


@dataclass
class PersKSWorker(BaseWorker):
    """
    [kuaishou web scrape]
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
        self.blacklist = {"douyin.com"}
        self.whitelist = {"live.kuaishou.com"}
        if self.process_verify(self.scrapeUrl):
            self.get_return(2, 0)
            return True
        # @@... ways of parse work_id
        if "/u/" in self.url_path and self.url_path.count("/") == 3:
            self.work_id = self.regex_first(self.url_path, "/.*/(.*)")
        else:
            self.logger.info(f"非法work号码(*>﹏<*)【{self.scrapeUrl}】")
            return False
        # check work_id
        if not self.work_id:
            self.logger.info(f"非法work号码(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(2, 0)
            return True
        # @@..! return false is do nothing
        return False

    def process_work(self):
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
        self.net.url = self.scrapeUrl
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "live.kuaishou.com",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
        })
        if not self.net.get_response("get"):
            return False
        if not self.net.get_page("text"):
            return False
#######################################################################################
        # parse data and check
        regex_string = self.regex_first(
            self.net.page, "__APOLLO_STATE__\\s{0,}=\\s{0,}({.*?})\\s{0,};")
        regex_dict = JsonAct.format_json(regex_string)
        if not regex_dict:
            self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
            return False
        root_data = self.json_first(
            regex_dict, "$.clients.graphqlServerClient", 0)
        if not root_data or not isinstance(root_data, dict):
            self.logger.info(f"非法client解析(*>﹏<*)【{self.scrapeUrl}】")
            return False
        # @@..! check if url is correct
        video_none = root_data.get("VideoFeed:null")
        if video_none:
            self.logger.info(f"非法work地址(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(2, 0)
            return True
        # query str join
        video_query = f'VideoFeed:{self.work_id}'
        video_info = root_data.get(video_query)
        counts_query = f'$VideoFeed:{self.work_id}.counts'
        counts_info = root_data.get(counts_query)
        if not video_info or not counts_info:
            self.logger.info("非法user登录(*>﹏<*)【cookies】")
            return False
#######################################################################################
        # parse data and check
        videoId = self.json_first(video_info, "$.id", 0)
        if not videoId:
            self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
            return False
        # @@..! videoUserId = accountId
        videoUserId = self.json_first(video_info, "$.user.id", 1)
        videoUserId = StrAct.parse_replace(videoUserId, "User:", "")
        videoUrl = f"https://live.kuaishou.com/u/{videoUserId}/{videoId}?did="
        # base data
        videoCover = self.json_first(video_info, "$.thumbnailUrl", 1)
        videoTitle = self.json_first(video_info, "$.caption", 1)
        videoCreated = self.json_number(video_info, "$.timestamp", 1)
        videoCreated = int(videoCreated / 1000)
        # count data
        videoPlay = self.json_first(counts_info, "$.displayView", 1)
        videoLike = self.json_first(counts_info, "$.displayLike", 1)
        videoComment = self.json_first(counts_info, "$.displayComment", 1)
        videoPlay = StrAct.parse_millions(videoPlay)
        videoLike = StrAct.parse_millions(videoLike)
        videoComment = StrAct.parse_millions(videoComment)
        # take data and return
        if not self.isLast:
            self.isLast = 0
        self.workBase = {
            "id": videoId, "showId": videoId, "scrapeUrl": videoUrl,
            "url": videoUrl, "uid": "", "nickname": "",
            "type": 1, "title": videoTitle, "cover": videoCover,
            "created": videoCreated, "source": "", "extra": "", 
            "desc": "", "duration": 0, "videoUrl": "",
            "picNum": 0, "picUrl": [],
            
            "likeNum": videoLike, "commentNum": videoComment,
            "shareNum": 0, "forwardNum": 0,
            "collectNum": 0, "playNum": videoPlay, "viewNum": 0, 
            "rewardNum": 0, "danmakuNum": 0, "blogRepost": {},
        }
        self.get_return(2, 1)
        return True

    def get_profile(self) -> bool:
        # @@..! need login cookie
        # @@..! set the blacklist and whitelist
        self.blacklist = {"douyin.com"}
        self.whitelist = {
            "kuaishou.com", "kuaishouapp.com", "yxixy.com",
            "chenzhongtech.com", "gifshow.com", "svo9cxiey8azgb.com"}
        if self.process_verify(self.scrapeUrl, ):
            self.get_return(2, 0)
            return True
        # @@... ways of parse user_id
        # @@..! check url if is profile page or not
        if "live.kuaishou.com" in self.url_domain and \
                self.url_path.startswith("/profile/"):
            pass
        else:
            # @@..! check url if has /fw/uesr or not
            if "/fw/user/" in self.url_path:
                redirect_url = self.scrapeUrl
            else:
                # parse first jump
                self.net.url = self.scrapeUrl
                self.net.headers = BaseAct.format_copy(self.init_header)
                self.net.headers.update({
                    "Host": self.url_domain,
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Dest": "document",
                })
                if not self.net.get_response("get"):
                    return False
                if not self.net.get_page("text", False, 302):
                    return False
                # check 404 page
                if self.net.code == 404:
                    self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
                    self.get_return(2, 0)
                    return True
                # parse jump url
                redirect_url = self.net.response.headers.get("Location")
                if not redirect_url or self.process_verify(redirect_url):
                    self.logger.info(f"非法/fw/user/跳转(*>﹏<*)【{self.scrapeUrl}】")
                    self.get_return(2, 0)
                    return True
                # if /fw/user not in url, parse second jump
                if "/fw/user/" not in self.url_path:
                    self.net.url = redirect_url
                    self.net.headers.update({
                        "Host": self.url_domain,
                    })
                    if not self.net.get_response("get"):
                        return False
                    if not self.net.get_page("text", False, 302):
                        return False
                    # check 404 page
                    if self.net.code == 404:
                        self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
                        self.get_return(2, 0)
                        return True
                    # parse jump url
                    redirect_url = self.net.response.headers.get("Location")
                    if not redirect_url or self.process_verify(redirect_url):
                        self.logger.info(f"非法/fw/user/跳转(*>﹏<*)【{self.scrapeUrl}】")
                        self.get_return(2, 0)
                        return True
                    # if /fw/user not in url, end
                    if "/fw/user/" not in self.url_path:
                        self.logger.info(self.net.response.url)
                        self.logger.info(f"非法/fw/user/滑块(*>﹏<*)【{self.scrapeUrl}】")
                        return False
            # parse /fw/user url
            self.net.url = redirect_url
            self.net.headers = BaseAct.format_copy(self.init_header)
            self.net.headers.update({
                "Host": self.url_domain,
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Dest": "document",
            })
            if not self.net.get_response("get"):
                return False
            if not self.net.get_page("text", False, 302):
                return False
            # check 404 page
            if self.net.code == 404:
                self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
                self.get_return(2, 0)
                return True
            # check if profile page or not
            redirect_url = self.net.response.headers.get("Location")
            if not redirect_url or self.process_verify(redirect_url):
                self.logger.info(f"非法profile解析(*>﹏<*)【{self.scrapeUrl}】")
                self.get_return(2, 0)
                return True
            if "live.kuaishou.com" in self.url_domain and \
                    self.url_path.startswith("/profile/"):
                pass
            else:
                self.logger.info(self.net.response.url)
                self.logger.info(f"非法profile滑块(*>﹏<*)【{self.scrapeUrl}】")
                return False
        # parse profile, check how many / in url
        self.url_path = StrAct.parse_replace(self.url_path, "^/profile", "")
        if self.url_path.count("/") == 1:
            self.user_id = self.regex_first(self.url_path, "/(.*)")
        else:
            self.user_id = self.regex_first(self.url_path, "/(.*?)/")
        # check user_id
        if not self.user_id:
            self.logger.info(f"非法user号码(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(2, 0)
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
        # after get user_id, get profile page
        self.homeUrl = f"https://live.kuaishou.com/profile/{self.user_id}"

        self.net.url = self.homeUrl
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "live.kuaishou.com",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
        })
        if not self.net.get_response("get"):
            return False
        if not self.net.get_page("text"):
            return False
        # check 404 page
        if self.net.code == 404:
            self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(2, 0)
            return True
        # @@..! save profile page
        account_page = self.net.page
        # get info data
        self.net.url = 'https://live.kuaishou.com/m_graphql'
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Accept": "*/*",
            'Content-Type': 'application/json',
            "Host": "live.kuaishou.com",
            "Origin": "https://live.kuaishou.com",
            "Referer": self.scrapeUrl,
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
        })
        self.net.posts = {
            "operationName": "sensitiveUserInfoQuery",
            "variables": {"principalId": self.user_id},
            "query": "query sensitiveUserInfoQuery($principalId: String) "
                     "{\n  sensitiveUserInfo(principalId: $principalId) "
                     "{\n    kwaiId\n    originUserId\n    constellation\n"
                     "    cityName\n    counts {\n      fan\n      follow\n"
                     "      photo\n      liked\n      open\n      playback\n"
                     "      private\n      __typename\n    }\n    "
                     "__typename\n  }\n}\n"}
        if not self.net.get_response("post", "json"):
            return False
        if not self.net.get_page("json", False):
            return False
#######################################################################################
        # @@..! parse no data, kwaiId is not parse
        no_login = self.json_first(self.net.page, "$.data.sensitiveUserInfo", 0)
        if not no_login or no_login is None:
            self.logger.info("非法user登录(*>﹏<*)【cookies】")
            return False
        # @@..! check user_id, userId != user_id, user_id = accountId
        userId = self.json_first(
            self.net.page, "$.data.sensitiveUserInfo.originUserId", 0)
        if not userId:
            self.logger.info("非法user号码(*>﹏<*)【page】")
            return False
        userId = str(userId)
        # @@..! check fansNum, already login and cookies fail
        fansNum = self.json_first(
            self.net.page, "$.data.sensitiveUserInfo.counts.fan", 0)
        followNum = self.json_first(
            self.net.page, "$.data.sensitiveUserInfo.counts.follow", 0)
        videos = self.json_first(
            self.net.page, "$.data.sensitiveUserInfo.counts.photo", 0)
        if fansNum is False:
            self.logger.info("非法fans数据(*>﹏<*)【cookies】")
            return False
        fansNum = StrAct.parse_millions(fansNum)
        followNum = StrAct.parse_millions(followNum)
        videos = StrAct.parse_millions(videos)
#######################################################################################
        self.scrapeUrl = f"https://live.kuaishou.com/profile/{self.user_id}"
        # if certify take data and return
        if self.toolType == 1:
            self.profileCounts = {'fansNum': fansNum, 'followNum': followNum}
            self.get_return(2, 1)
            return True
        # parse data
        constellation = self.json_first(
            self.net.page, "$.data.sensitiveUserInfo.constellation", 1)
        area = self.json_first(
            self.net.page, "$.data.sensitiveUserInfo.cityName", 1)
        # @@..! parse profile page
        account_data = self.regex_first(
            account_page, "__APOLLO_STATE__\\s{0,}=\\s{0,}({.*?})\\s{0,};")
        query_dict = JsonAct.format_json(account_data)
        query_data = self.json_first(query_dict, "$.clients.graphqlServerClient", 0)
        root_data = self.json_first(
            query_dict, "$.clients.graphqlServerClient.ROOT_QUERY", 0)
        if not query_data or not root_data or not isinstance(query_data, dict) \
                or not isinstance(root_data, dict):
            self.logger.info(f"非法client解析(*>﹏<*)【{self.scrapeUrl}】")
            return False
        # query str join
        root_query = f'userInfo({{"principalId":"{self.user_id}"}})'
        root_info = root_data.get(root_query)
        user_query = self.json_first(root_info, "$.id", 1)
        if "User:" not in user_query or "null" in user_query:
            self.logger.info("非法user映射(*>﹏<*)【root】")
            return False
        verify_query = f"${user_query}.verifiedStatus"
        user_info = query_data.get(user_query)
        verify_info = query_data.get(verify_query)
        # parse query data
        secId = self.json_first(user_info, "$.eid", 1)
        accountId = self.json_first(user_info, "$.id", 1)
        avatar = self.json_first(user_info, "$.avatar", 1)
        nickname = self.json_first(user_info, "$.name", 1)
        gender = self.json_first(user_info, "$.sex", 1)
        desc = self.json_first(user_info, "$.description", 1)
        isAuth = self.json_first(verify_info, "$.verified", 1)
        authType = self.json_first(verify_info, "$.type", 1)
        authDetail = self.json_first(verify_info, "$.description", 1)
        # format the data
        if "F" in gender:
            gender = 2
        elif "M" in gender:
            gender = 1
        else:
            gender = 0
        if isAuth:
            isAuth = 1
        else:
            isAuth = 2
        # video data
        self.net.posts = {
            "operationName": "privateFeedsQuery",
            "variables": {"principalId": self.user_id, "pcursor": "", "count": 24},
            "query": "query privateFeedsQuery($principalId: String, "
                     "$pcursor: String, $count: Int) "
                     "{\n  privateFeeds(principalId: $principalId, "
                     "pcursor: $pcursor, count: $count) {\n    pcursor\n"
                     "    list {\n      id\n      thumbnailUrl\n      poster\n"
                     "      workType\n      type\n      useVideoPlayer\n"
                     "      imgUrls\n      imgSizes\n      magicFace\n"
                     "      musicName\n      caption\n      location\n"
                     "      liked\n      onlyFollowerCanComment\n"
                     "      relativeHeight\n      timestamp\n      width\n"
                     "      height\n      counts {\n        displayView\n"
                     "        displayLike\n        displayComment\n"
                     "        __typename\n      }\n      user {\n        id\n"
                     "        eid\n        name\n        avatar\n"
                     "        __typename\n      }\n      expTag\n"
                     "      isSpherical\n      __typename\n    }\n"
                     "    __typename\n  }\n}\n"}
        if not self.net.get_response("post", "json"):
            return False
        if not self.net.get_page("json", False):
            return False
        # @@..! set isUrls is 0 and isLast is 1
        self.isUrls = 0
        self.isLast = 1
        # get video ids list and take urls
        work_nums = 10
        if self.toolType == 2:
            work_nums = 5
        video_gen = JsonAct.parse_json(
            self.net.page, f"$.data.privateFeeds.list[:{work_nums}]")
        for i in video_gen:
            # get id and check
            videoId = self.json_first(i, "$.id", 0)
            if not videoId:
                self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
                continue
            videoUrl = f"https://live.kuaishou.com/u/{self.user_id}/{videoId}?did="
            # @@..! take url list
            self.workUrls.append(videoUrl)
            # base data
            videoCover = self.json_first(i, "$.thumbnailUrl", 1)
            videoTitle = self.json_first(i, "$.caption", 1)
            videoCreated = self.json_number(i, "$.timestamp", 1)
            videoCreated = int(videoCreated / 1000)
            # count data
            videoPlay = self.json_first(i, "$.counts.displayView", 1)
            videoLike = self.json_first(i, "$.counts.displayLike", 1)
            videoComment = self.json_first(i, "$.counts.displayComment", 1)
            videoPlay = StrAct.parse_millions(videoPlay)
            videoLike = StrAct.parse_millions(videoLike)
            videoComment = StrAct.parse_millions(videoComment)
            # take data and return
            self.workBase = {
                "id": videoId, "showId": videoId, "scrapeUrl": videoUrl,
                "url": videoUrl, "uid": "", "nickname": "",
                "type": 1, "title": videoTitle, "cover": videoCover,
                "created": videoCreated, "source": "", "extra": "", 
                "desc": "", "duration": 0, "videoUrl": "",
                "picNum": 0, "picUrl": [],
                
                "likeNum": videoLike, "commentNum": videoComment,
                "shareNum": 0, "forwardNum": 0,
                "collectNum": 0, "playNum": videoPlay, "viewNum": 0, 
                "rewardNum": 0, "danmakuNum": 0, "blogRepost": {},
            }
            # if tool type is not 1, take list
            if self.toolType != 1:
                self.workList.append(self.workBase)
        # @@..! matchUid -> userId
        # take base and counts data and return
        self.profileBase = {
            "matchUid": userId, "userId": userId, "accountId": accountId,
            "secId": secId, "avatar": avatar, "qrCode": "", "nickname": nickname,
            "field": "", "isMember": 0, "isAuth": isAuth,
            "gender": gender, "age": "", "birth": "", "constellation": constellation,
            "area": area, "notice": "", "desc": desc,
            "memberLevel": "", "memberType": "", "memberDetail": "",
            "authLevel": "", "authType": str(authType), "authDetail": str(authDetail),
            "isCompany": 0, "isGovernmentMedia": 0
        }
        self.profileCounts = {
            "fansNum": fansNum, "followNum": followNum,
            "videos": videos, "blogs": 0, "worksNum": videos,
            "favoriteNum": 0, "collectNum": 0, "likeNum": 0,
            "playNum": 0, "viewNum": 0, "rewardNum": 0
        }

        self.get_return(2, 1)
        return True
