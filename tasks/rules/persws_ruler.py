#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> weishi ruler
@@..> package tasks.rules
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> base import
from dataclasses import dataclass, field
# @@..> import utils
from .base_ruler import BaseWorker, BaseAct, DomAct, TimeAct, JsonAct, StrAct


@dataclass
class PersWSWorker(BaseWorker):
    """
    [weishi web scrape]
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
        self.whitelist = {"weishi.qq.com"}
        if self.process_verify(self.scrapeUrl):
            self.get_return(9, 0)
            return True
        # @@... ways of parse work_id
        if "/weishi/feed/" in self.url_path:
            self.work_id = self.regex_first(self.url_path, "/feed/(.*)/wsfeed")
        else:
            self.logger.info(f"非法work号码(*>﹏<*)【{self.scrapeUrl}】")
            return False
        # check work_id
        if not self.work_id:
            self.logger.info(f"非法work号码(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(9, 0)
            return True
        # @@..! return false is do nothing
        return False

    def process_work(self):
        # after get work_id, get work page
        self.net.url = f"https://h5.weishi.qq.com/weishi/feed/{self.work_id}/wsfeed?wxplay=1&id={self.work_id}&spid="
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "h5.weishi.qq.com",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
            "Referer": "https://isee.weishi.qq.com/"
        })
        if not self.net.get_response("get", is_redirect=True):
            return False
        if not self.net.get_page("text", False):
            return False

        self.net.url = "https://h5.weishi.qq.com/webapp/json/weishi/WSH5GetPlayPage?g_tk="
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "h5.weishi.qq.com",
            "Accept": "*/*",
            "Content-type": "application/json",
            "Origin": "https://isee.weishi.qq.com",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://isee.weishi.qq.com/"
        })
        self.net.posts = {"feedid": self.work_id, "recommendtype": 0,
                          "datalvl": "all", "_weishi_mapExt": {}}
        if not self.net.get_response("post", "json"):
            return False
        if not self.net.get_page("json", False):
            return False
        # check 404 page
        result = self.json_first(self.net.page, "$.data.feeds[0]", 0)
        if not result:
            self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(9, 0)
            return True
#######################################################################################
        # parse data and check
        videoId = self.json_first(result, "$.id", 0)
        if not videoId:
            self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
            return False
        videoUrl = f"https://h5.weishi.qq.com/weishi/feed/{videoId}/wsfeed?wxplay=1&id={videoId}&spid="
        # base data
        videoCover = self.json_first(result, "$.video_cover.smart_cover.url", 0)
        if not videoCover:
            videoCover = self.json_first(result, "$.video_cover.static_cover.url", 1)
        videoTitle = self.json_first(result, "$.feed_desc", 1)
        videoTitle = StrAct.format_clear(videoTitle, True)
        videoStream = self.json_first(result, "$.video_url", 1)
        videoDuration = self.json_number(result, "$.video.duration", 1)
        videoCreated = self.json_number(result, "$.createtime", 1)
        videoExtra = self.json_first(result, "$.content_tags", 1)
        if videoExtra and isinstance(videoExtra, list):
            extra_list = []
            for t in videoExtra:
                extra_list.append(t.get("name"))
            videoExtra = ",".join(extra_list)
        else:
            videoExtra = ""
        # count data
        videoPlay = self.json_first(result, "$.playNum", 1)
        videoLike = self.json_first(result, "$.ding_count", 1)
        videoComment = self.json_first(result, "$.total_comment_num", 1)
        videoShare = self.json_number(result, "$.share_info.share_num", 1)
        # take data and return
        if not self.isLast:
            self.isLast = 0
        self.workBase = {
            "id": videoId, "showId": videoId, "scrapeUrl": videoUrl,
            "url": videoUrl, "uid": "", "nickname": "",
            "type": 1, "title": videoTitle, "cover": videoCover,
            "created": videoCreated, "source": "", "extra": videoExtra, 
            "desc": "", "duration": videoDuration, "videoUrl": videoStream,
            "picNum": 0, "picUrl": [],
            
            "likeNum": videoLike, "commentNum": videoComment,
            "shareNum": videoShare, "forwardNum": videoShare,
            "collectNum": 0, "playNum": videoPlay, "viewNum": 0, 
            "rewardNum": 0, "danmakuNum": 0, "blogRepost": {},
        }
        self.get_return(9, 1)
        return True

    def get_profile(self) -> bool:
        # @@..! set the blacklist and whitelist
        self.blacklist = {"creator.douyin.com"}
        self.whitelist = {"weishi.qq.com"}
        if self.process_verify(self.scrapeUrl):
            self.get_return(9, 0)
            return True
        # @@... ways of parse user_id
        if self.url_path and "/weishi/personal/" in self.url_path:
            pass
        else:
            self.logger.info(f"非法profile页面(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(9, 0)
            return True
        # check user_id
        counts = self.url_path.count("/")
        if counts == 3:
            self.user_id = self.regex_first(self.url_path, "/weishi/personal/(\\d+)")
        else:
            self.user_id = self.regex_first(self.url_path, "/weishi/personal/(\\d+)/")
        if not self.user_id:
            self.logger.info(f"非法user号码(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(9, 0)
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
        # after get user_id, get profile page
        self.homeUrl = f"https://h5.weishi.qq.com/weishi/personal/{self.user_id}" \
                       f"/wspersonal?_wv=1&id={self.user_id}"
        self.net.url = self.homeUrl
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "h5.weishi.qq.com",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
        })
        if not self.net.get_response("get"):
            return False
        if not self.net.get_page("text", False):
            return False
        self.net.url = f"https://h5.weishi.qq.com/weishi/personal/{self.user_id}" \
                       f"/wspersonal?_wv=1&id={self.user_id}&from=pc&orifrom="
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "h5.weishi.qq.com",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "iframe",
            "Referer": f"https://h5.weishi.qq.com/weishi/personal/{self.user_id}"
                       f"/wspersonal?_wv=1&id={self.user_id}"
        })
        if not self.net.get_response("get"):
            return False
        if not self.net.get_page("text", False):
            return False
        # get api data
        self.net.url = "https://api.weishi.qq.com/trpc.weishi.weishi_h5_proxy" \
                       ".weishi_h5_proxy/GetPersonalHomePage?t=&g_tk="
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "api.weishi.qq.com",
            "Accept": "application/json",
            "Content-type": "multipart/form-data",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Origin": "https://h5.weishi.qq.com",
            "Referer": "https://h5.weishi.qq.com/"
        })
        self.net.posts = {
            "req_body": {"personID": self.user_id},
            "req_header": {
                "personId": "",
                "authInfo": {
                    "refreshToken": "", "accessToken": "", "sessionKey": "",
                    "authType": 0, "thrAppId": "", "uid": ""}, "channelId": 4
            }}
        if not self.net.get_response("post", "json"):
            return False
        if not self.net.get_page("json", False):
            return False
        # check 404 page
        result = self.json_first(self.net.page, "$.rsp_body", 0)
        if not result:
            self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(9, 0)
            return True
#######################################################################################
        # @@..! check user_id
        userId = self.json_first(
            self.net.page, "$.rsp_body.person.id", 0)
        if not userId:
            self.logger.info("非法user号码(*>﹏<*)【page】")
            self.get_return(9, 0)
            return True
        userId = str(userId)
        # parse data
        accountId = self.json_first(
            self.net.page, "$.rsp_body.person.extern_info.weishiId", 1)
        nickname = self.json_first(self.net.page, "$.rsp_body.person.nick", 1)
        avatar = self.json_first(self.net.page, "$.rsp_body.person.avatar", 1)
        gender = self.json_number(self.net.page, "$.rsp_body.person.sex", 1)
        age = self.json_first(self.net.page, "$.rsp_body.person.age", 1)
        area = self.json_first(self.net.page, "$.rsp_body.person.address", 1)
        desc = self.json_first(self.net.page, "$.rsp_body.person.status", 1)
        desc = StrAct.format_clear(desc, True)
        authDetail = self.json_first(
            self.net.page, "$.rsp_body.person.certif_desc", 1)
        # format the data
        if gender == 0:
            gender = 2
        elif gender == 1:
            gender = 1
        else:
            gender = 0
        if authDetail:
            isAuth = 1
        else:
            isAuth = 2
        # count data
        followNum = self.json_number(
            self.net.page, "$.rsp_body.numeric.interest_num", 1)
        fansNum = self.json_number(self.net.page, "$.rsp_body.numeric.fans_num", 1)
        likeNum = self.json_number(
            self.net.page, "$.rsp_body.numeric.receivepraise_num", 1)
        favoriteNum = self.json_number(
            self.net.page, "$.rsp_body.numeric.praise_num", 1)
        videos = self.json_number(self.net.page, "$.rsp_body.numeric.feed_num", 1)
#######################################################################################
        self.scrapeUrl = self.homeUrl
        # if certify take data and return
        if self.toolType == 1:
            self.profileCounts = {'fansNum': fansNum, 'followNum': followNum}
            self.get_return(9, 1)
            return True
        # get work list
        self.net.url = "https://api.weishi.qq.com/trpc.weishi.weishi_h5_proxy" \
                       ".weishi_h5_proxy/GetPersonalFeedList?t=&g_tk="
        self.net.posts = {
            "req_body": {"attchInfo": "", "type": 1, "personID": self.user_id}, 
            "req_header": {
                "personId": "",
                "authInfo": {
                    "refreshToken": "", "accessToken": "", "sessionKey": "",
                    "authType": 0, "thrAppId": "", "uid": ""},
                "channelId": 4
            }}
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
            self.net.page, f"$.rsp_body.feeds[:{work_nums}]")
        for i in video_gen:
            # get id and check
            videoId = self.json_first(i, "$.id", 0)
            if not videoId:
                self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
                continue
            videoUrl = f"https://h5.weishi.qq.com/weishi/feed/{videoId}/wsfeed?wxplay=1&id={videoId}&spid="
            # @@..! take url list
            self.workUrls.append(videoUrl)
            # base data
            videoCover = self.json_first(i, "$.video_cover.smart_cover.url", 0)
            if not videoCover:
                videoCover = self.json_first(i, "$.video_cover.static_cover.url", 1)
            videoTitle = self.json_first(i, "$.feed_desc", 1)
            videoTitle = StrAct.format_clear(videoTitle, True)
            videoStream = self.json_first(i, "$.video_url", 1)
            videoDuration = self.json_number(i, "$.video.duration", 1)
            videoCreated = self.json_number(i, "$.createtime", 1)
            videoExtra = self.json_first(i, "$.content_tags", 1)
            if videoExtra and isinstance(videoExtra, list):
                extra_list = []
                for t in videoExtra:
                    extra_list.append(t.get("name"))
                videoExtra = ",".join(extra_list)
            else:
                videoExtra = ""
            # count data
            videoPlay = self.json_first(i, "$.playNum", 1)
            videoLike = self.json_first(i, "$.ding_count", 1)
            videoComment = self.json_first(i, "$.total_comment_num", 1)
            videoShare = self.json_number(i, "$.share_info.share_num", 1)
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
            "secId": "", "avatar": avatar, "qrCode": "", "nickname": nickname,
            "field": "", "isMember": 0, "isAuth": isAuth,
            "gender": gender, "age": age, "birth": "", "constellation": "",
            "area": area, "notice": "", "desc": desc,
            "memberLevel": "", "memberType": "", "memberDetail": "",
            "authLevel": "", "authType": "", "authDetail": str(authDetail),
            "isCompany": 0, "isGovernmentMedia": 0
        }
        self.profileCounts = {
            "fansNum": fansNum, "followNum": followNum,
            "videos": videos, "blogs": 0, "worksNum": videos,
            "favoriteNum": favoriteNum, "collectNum": 0, "likeNum": likeNum,
            "playNum": 0, "viewNum": 0, "rewardNum": 0
        }

        self.get_return(9, 1)
        return True


