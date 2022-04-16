#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> xigua ruler
@@..> package tasks.rules
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> base import
from dataclasses import dataclass, field
# @@..> import utils
from .base_ruler import BaseWorker, BaseAct, DomAct, TimeAct, JsonAct, StrAct, UrlAct


@dataclass
class PersXGWorker(BaseWorker):
    """
    [xigua web scrape]
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
            self.get_return(10, 0)
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
        self.get_return(10, 1)
        return True

    def get_profile(self) -> bool:
        # @@..! set the blacklist and whitelist
        self.blacklist = {"creator.douyin.com"}
        self.whitelist = {"www.ixigua.com"}
        if self.process_verify(self.scrapeUrl):
            self.get_return(10, 0)
            return True
        # @@... ways of parse user_id
        if self.url_path and "/home/" in self.url_path:
            pass
        else:
            self.logger.info(f"非法profile页面(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(10, 0)
            return True
        # check user_id
        self.user_id = self.regex_first(self.url_path, "/home/(\\d+)")
        if not self.user_id:
            self.logger.info(f"非法user号码(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(10, 0)
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
        self.homeUrl = f"https://www.ixigua.com/home/{self.user_id}/?list_entrance=homepage&video_card_type=shortvideo"
        self.net.url = self.homeUrl
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "www.ixigua.com",
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document"
        })
        if not self.net.get_response("get"):
            return False
        if not self.net.get_page("text", False):
            return False
        self.net.url = "https://ttwid.bytedance.com/ttwid/union/register/"
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "ttwid.bytedance.com",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/x-www-form-urlencoded",
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            "Origin": "https://www.ixigua.com",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://www.ixigua.com/"
        })
        self.net.posts = {"region": "cn", "aid": 1768, "needFid": False, "service": "www.ixigua.com",
                          "migrate_info": {"ticket": "", "source": "node"}, "cbUrlProtocol": "https", "union": True}
        if not self.net.get_response("post", "json"):
            return False
        if not self.net.get_page("json", False):
            return False
        redirect_url = self.json_first(
            self.net.page, "$.redirect_url", 1)
        
        self.net.url = redirect_url
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "www.ixigua.com",
            "Accept": "application/json, text/plain, */*",
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": f"https://www.ixigua.com/home/{self.user_id}/?list_entrance=homepage&video_card_type=shortvideo"
        })
        if not self.net.get_response("get"):
            return False
        if not self.net.get_page("json", False):
            return False

        self.net.url = f"https://www.ixigua.com/home/{self.user_id}/?list_entrance=homepage&video_card_type=shortvideo&wid_try=1"
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "www.ixigua.com",
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
            "Referer": f"https://www.ixigua.com/home/{self.user_id}/?list_entrance=homepage&video_card_type=shortvideo"
        })
        if not self.net.get_response("get"):
            return False
        # check 404 page
        if self.net.code == 404:
            self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(10, 0)
            return True
        if not self.net.get_page("text", False):
            return False
        html_dom = DomAct.parse_dom(self.net.page)
        parse_gen = DomAct.parse_selector(html_dom, "script#SSR_HYDRATED_DATA", "text")
        result_data, parse_gen = BaseAct.parse_generator(parse_gen)
        result_data = self.regex_first(result_data, "{.*}")
        if not result_data:
            self.logger.info(f"非法解析数据(*>﹏<*)【{self.scrapeUrl}】")
            return False
        result_dict = JsonAct.format_json(result_data)
#######################################################################################
        # @@..! check user_id
        userId = self.json_first(
            result_dict, "$.AuthorDetailInfo.user_id", 0)
        if not userId:
            self.logger.info("非法user号码(*>﹏<*)【page】")
            self.get_return(10, 0)
            return True
        userId = str(userId)
        # parse data
        accountId = self.json_first(
            result_dict, "$.AuthorDetailInfo.media_id", 1)
        nickname = self.json_first(result_dict, "$.AuthorDetailInfo.name", 1)
        avatar = self.json_first(result_dict, "$.AuthorDetailInfo.avatar", 1)
        desc = self.json_first(result_dict, "$.AuthorDetailInfo.introduce", 1)
        desc = StrAct.format_clear(desc, True)
        # count data
        followNum = self.json_number(
            result_dict, "$.AuthorDetailInfo.followNum", 1)
        fansNum = self.json_number(result_dict, "$.AuthorDetailInfo.fansNum", 1)
        likeNum = self.json_number(
            result_dict, "$.AuthorDetailInfo.diggNum", 1)
        videos = self.json_number(result_dict, "$.AuthorTabsCount.videoCnt", 1)
#######################################################################################
        self.scrapeUrl = self.homeUrl
        # if certify take data and return
        if self.toolType == 1:
            self.profileCounts = {'fansNum': fansNum, 'followNum': followNum}
            self.get_return(10, 1)
            return True
        # get work list
        # @@..! set isUrls is 0 and isLast is 1
        self.isUrls = 0
        self.isLast = 1
        # get video ids list and take urls
        work_nums = 10
        if self.toolType == 2:
            work_nums = 5
        # preview_url
        video_gen = JsonAct.parse_json(
            result_dict, f"$.AuthorHomeVideoList.videos[:{work_nums}]")
        for i in video_gen:
            # get id and check
            videoId = self.json_first(i, "$.groupId", 0)
            if not videoId:
                self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
                continue
            videoUrl = f"https://www.ixigua.com/{videoId}"
            # @@..! take url list
            self.workUrls.append(videoUrl)
            # base data
            videoCover = self.json_first(i, "$.coverUrl", 0)
            videoTitle = self.json_first(i, "$.title", 1)
            videoTitle = StrAct.format_clear(videoTitle, True)
            videoStream = self.json_first(i, "$.preview_url", 1)
            videoDuration = self.json_number(i, "$.duration", 1)
            videoCreated = self.json_number(i, "$.publishTime", 1)
            # count data
            videoPlay = self.json_first(i, "$.playNum", 1)
            # videoLike = self.json_first(i, "$.ding_count", 1)
            # videoComment = self.json_first(i, "$.total_comment_num", 1)
            # videoShare = self.json_number(i, "$.share_info.share_num", 1)
            # take data and return
            self.workBase = {
                "id": videoId, "showId": videoId, "scrapeUrl": videoUrl,
                "url": videoUrl, "uid": "", "nickname": "",
                "type": 1, "title": videoTitle, "cover": videoCover,
                "created": videoCreated, "source": "", "extra": "", 
                "desc": "", "duration": videoDuration, "videoUrl": videoStream,
                "picNum": 0, "picUrl": [],
                
                "likeNum": 0, "commentNum": 0,
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
            "secId": "", "avatar": avatar, "qrCode": "", "nickname": nickname,
            "field": "", "isMember": 0, "isAuth": 0,
            "gender": 0, "age": 0, "birth": "", "constellation": "",
            "area": "", "notice": "", "desc": desc,
            "memberLevel": "", "memberType": "", "memberDetail": "",
            "authLevel": "", "authType": "", "authDetail": "",
            "isCompany": 0, "isGovernmentMedia": 0
        }
        self.profileCounts = {
            "fansNum": fansNum, "followNum": followNum,
            "videos": videos, "blogs": 0, "worksNum": videos,
            "favoriteNum": 0, "collectNum": 0, "likeNum": likeNum,
            "playNum": 0, "viewNum": 0, "rewardNum": 0
        }

        self.get_return(10, 1)
        return True


