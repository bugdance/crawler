#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> xiaohongshu ruler
@@..> package tasks.rules
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> base import
from dataclasses import dataclass, field
# @@..> import utils
from .base_ruler import BaseWorker, BaseAct, DomAct, NumAct, TimeAct, JsonAct, StrAct, EncryptAct


# @@..! baidu mini scrape
@dataclass
class PersHSWorker(BaseWorker):
    """
    [xiaohongshu baidu mini scrape]
    """
    asid: str = field(default_factory=str)
    retry_num: int = field(default_factory=int)

    def process_index(self) -> bool:
        # rebuild
        self.retry_num = 0
        self.header_version, self.user_agent, self.init_header = \
            self.net.set_header("xiaomi")
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
        # @@..! at least need {'timestamp2': ''}, otherwise the slider appears
        # @@..! set the blacklist and whitelist
        self.blacklist = {"video.weibo.com"}
        self.whitelist = {"xiaohongshu.com", "xhslink.com"}
        if self.process_verify(self.scrapeUrl):
            self.get_return(4, 0)
            return True
        # @@... ways of parse work_id
        if "www.xiaohongshu.com" in self.url_domain and self.url_path:
            self.work_id = self.regex_first(self.url_path, "/discovery/item/(.*)")

        elif "xhslink.com" in self.url_domain and self.url_path:
            self.net.url = self.scrapeUrl
            self.net.headers = BaseAct.format_copy(self.init_header)
            self.net.headers.update({
                "Host": "xhslink.com",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Dest": "document"
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
                self.logger.info(f"非法xhslink跳转(*>﹏<*)【{self.scrapeUrl}】")
                self.get_return(4, 0)
                return True
            if "www.xiaohongshu.com" in self.url_domain and self.url_path:
                self.work_id = self.regex_first(
                    self.url_path, "/discovery/item/(.*)")

            else:
                self.logger.info(f"非法xhslink跳转(*>﹏<*)【{self.scrapeUrl}】")
                self.get_return(4, 0)
                return True
        else:
            self.logger.info(f"非法url链接(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(4, 0)
            return True
        # check work_id
        if self.work_id is False:
            self.logger.info(f"非法work号码(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(4, 0)
            return True
        # @@..! return false is do nothing
        return False

    def process_work(self) -> bool:
        # get asid
        x_sign = "X" + EncryptAct.format_md5(
            "/fe_api/burdock/baidu/v2/shield/get_asid" + "WSUDD")
        self.net.url = "https://www.xiaohongshu.com/fe_api/burdock/" \
                       "baidu/v2/shield/get_asid"
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "asid": "[object Undefined]",
            "X-Sign": x_sign,
            "X-B3-TraceId": "90ac2ed87e44757f",
            "X-Bd-Traceid": "53d8437db6ee444fb68058d7ca8ecb13",
            "Host": "www.xiaohongshu.com",
            "Content-Type": "application/json; charset=utf-8",
            "Referer": "https://smartapps.cn/KuRdr9OR39BqyAGIg7mYK7Bytityu0Vi"
                       "/2.35.16/page-frame.html"
        })
        self.net.posts = {
            "swanId": "SNBPqVQvpvXEBSv27NcY49VLQJfEveFGLSx9qAQMQ8yfxJE6yzm"
                      "2GfDWA6SPjtxJYp3hRby5F6rnao98PEXGtujS1",
            "swanIdSignature": "cf5f8877cb896010ff2d4dc059ee1350"}
        if not self.net.get_response("post", "json"):
            return False
        if not self.net.get_page("json", False):
            return False
        asid_gen = JsonAct.parse_json(self.net.page, "$.data")
        self.asid, asid_gen = BaseAct.parse_generator(asid_gen)
        if not self.asid:
            self.logger.info("非法asid获取(*>﹏<*)【asid】")
            return False
        # after get work_id, get work page
        if not self.pass_work():
            return False
#######################################################################################
        # check work_id
        blogId = self.json_first(self.net.page, "$.data.id", 1)
        if not blogId:
            self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
            return False
        # base data
        blogUrl = f"https://www.xiaohongshu.com/discovery/item/{self.work_id}"
        blogCover = self.json_first(self.net.page, "$.data.cover.url", 1)
        if blogCover and not blogCover.startswith("http"):
            blogCover = "https:" + blogCover
        blogTitle = self.json_first(self.net.page, "$.data.title", 1)
        blogDesc = self.json_first(self.net.page, "$.data.desc", 1)
        blogCreated = self.json_first(self.net.page, "$.data.time", 1)
        blogCreated = TimeAct.parse_timestring(blogCreated, "%Y-%m-%d %H:%M")
        int_gen = StrAct.parse_integer(blogCreated.timestamp())
        blogCreated, int_gen = BaseAct.parse_generator(int_gen)
        if blogCreated is False:
            blogCreated = 0
        # type 0 pic/1 video
        blogPicUrl = []
        pic_gen = JsonAct.parse_json(
            self.net.page, "$.data.imageList.*.url")
        for i in pic_gen:
            if i.startswith("http"):
                blogPicUrl.append(i)
            else:
                blogPicUrl.append("https:" + i)
        blogPicNum = len(blogPicUrl)
        # check type
        blogType = self.json_first(self.net.page, "$.data.type", 1)
        if "video" in blogType:
            blogType = 1
            blogPicUrl = []
            blogPicNum = 0
        else:
            blogType = 0
        # video
        blogVideo = self.json_first(self.net.page, "$.data.video.url", 1)
        if blogVideo and not blogVideo.startswith("http"):
            blogVideo = "https:" + blogVideo
        blogDuration = self.json_number(
            self.net.page, "$.data.video.duration", 1)
        # count data
        blogLike = self.json_number(self.net.page, "$.data.likes", 1)
        blogComment = self.json_number(self.net.page, "$.data.comments", 1)
        blogCollect = self.json_number(self.net.page, "$.data.collects", 1)
        blogShare = self.json_number(self.net.page, "$.data.shareCount", 1)
        # take data and return
        if not self.isLast:
            self.isLast = 0
        self.workBase = {
            "id": blogId, "showId": blogId, "scrapeUrl": blogUrl,
            "url": blogUrl, "uid": "", "nickname": "",
            "type": blogType, "title": blogTitle, "cover": blogCover,
            "created": blogCreated, "source": "", "extra": "",
            "desc": blogDesc, "duration": blogDuration, "videoUrl": blogVideo,
            "picNum": blogPicNum, "picUrl": blogPicUrl,

            "likeNum": blogLike, "commentNum": blogComment, "shareNum": blogShare,
            "forwardNum": blogShare, "collectNum": blogCollect,
            "playNum": 0, "viewNum": 0,
            "rewardNum": 0, "danmakuNum": 0, "blogRepost": {}
        }
        self.get_return(4, 1)
        return True

    def get_profile(self) -> bool:
        # @@..! at least need {'timestamp2': ''}, otherwise the slider appears
        # @@..! set the blacklist and whitelist
        self.blacklist = {"video.weibo.com"}
        self.whitelist = {"xiaohongshu.com"}
        if self.process_verify(self.scrapeUrl):
            self.get_return(4, 0)
            return True
        # @@... ways of parse user_id
        if "/user/profile/" not in self.url_path:
            self.logger.info(f"非法profile页面(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(4, 0)
            return True
        # check user_id
        self.user_id = self.regex_first(self.url_path, "/profile/(.*)")
        if not self.user_id:
            self.logger.info(f"非法user号码(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(4, 0)
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
        # get asid
        x_sign = "X" + EncryptAct.format_md5(
            "/fe_api/burdock/baidu/v2/shield/get_asid" + "WSUDD")
        self.net.url = "https://www.xiaohongshu.com/fe_api/burdock/" \
                       "baidu/v2/shield/get_asid"
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "asid": "[object Undefined]",
            "X-Sign": x_sign,
            "X-B3-TraceId": "90ac2ed87e44757f",
            "X-Bd-Traceid": "53d8437db6ee444fb68058d7ca8ecb13",
            "Host": "www.xiaohongshu.com",
            "Content-Type": "application/json; charset=utf-8",
            "Referer": "https://smartapps.cn/KuRdr9OR39BqyAGIg7mYK7Bytityu0Vi"
                       "/2.35.16/page-frame.html"
        })
        self.net.posts = {
            "swanId": "SNBPqVQvpvXEBSv27NcY49VLQJfEveFGLSx9qAQMQ8yfxJE6yzm"
                      "2GfDWA6SPjtxJYp3hRby5F6rnao98PEXGtujS1",
            "swanIdSignature": "cf5f8877cb896010ff2d4dc059ee1350"}
        if not self.net.get_response("post", "json"):
            return False
        if not self.net.get_page("json", False):
            return False
        asid_gen = JsonAct.parse_json(self.net.page, "$.data")
        self.asid, asid_gen = BaseAct.parse_generator(asid_gen)
        if not self.asid:
            self.logger.info("非法asid获取(*>﹏<*)【asid】")
            return False
        # after get asid, get profile page
        if not self.pass_profile():
            return False
#######################################################################################
        # check user_id
        userId = self.json_first(self.net.page, "$.data.id", 0)
        if not userId and userId != self.user_id:
            self.logger.info("非法user号码(*>﹏<*)【page】")
            self.get_return(4, 0)
            return True
        userId = str(userId)
        # parse data
        accountId = self.json_first(self.net.page, "$.data.red_id", 1)
        accountId = str(accountId)
        nickname = self.json_first(self.net.page, "$.data.nickname", 1)
        avatar = self.json_first(self.net.page, "$.data.image", 1)
        gender = self.json_number(self.net.page, "$.data.gender", 1)
        area = self.json_first(self.net.page, "$.data.location", 1)
        desc = self.json_first(self.net.page, "$.data.desc", 1)
        memberLevel = self.json_first(self.net.page, "$.data.level.name", 1)
        isAuth = self.json_first(self.net.page, "$.data.officialVerified", 1)
        authType = self.json_first(self.net.page, "$.data.redOfficialVerifyType", 1)
        authDetail = self.json_first(self.net.page, "$.data.verifyContent", 1)
        # format the data
        if gender == 0:
            gender = 1
        elif gender == 1:
            gender = 2
        else:
            gender = 0
        if memberLevel:
            isMember = 1
        else:
            memberLevel = ""
            isMember = 2
        if isAuth:
            isAuth = 1
        else:
            isAuth = 2
        # count data
        followNum = self.json_number(self.net.page, "$.data.follows", 1)
        fansNum = self.json_number(self.net.page, "$.data.fans", 1)
        blogs = self.json_number(self.net.page, "$.data.notes", 1)
        collectNum = self.json_number(self.net.page, "$.data.collected", 1)
        likeNum = self.json_number(self.net.page, "$.data.liked", 1)
#######################################################################################
        self.scrapeUrl = f"https://www.xiaohongshu.com/user/profile/{self.user_id}"
        # if certify take data and return
        if self.toolType == 1:
            self.profileCounts = {'fansNum': fansNum, 'followNum': followNum}
            self.get_return(4, 1)
            return True
        # get work list, set retry num is 0
        self.retry_num = 0
        if not self.pass_list():
            return False
        # @@..! set isUrls is 0 and isLast is 1
        self.isLast = 1
        self.isUrls = 0
        # get blog ids list and take urls
        work_nums = 10
        if self.toolType == 2:
            work_nums = 5

        blog_gen = JsonAct.parse_json(self.net.page, f"$.data.[:{work_nums}]")
        for i in blog_gen:
            # get id and check
            blogId = self.json_first(i, "$.id", 0)
            if not blogId:
                self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
                continue
            blogUrl = f"https://www.xiaohongshu.com/discovery/item/{blogId}"
            # @@..! take url list
            self.workUrls.append(blogUrl)
            # base data
            blogCover = self.json_first(i, "$.cover.url", 1)
            if blogCover and not blogCover.startswith("http"):
                blogCover = "https:" + blogCover
            blogTitle = self.json_first(i, "$.title", 1)
            blogDesc = self.json_first(i, "$.desc", 1)
            blogCreated = self.json_first(i, "$.time", 1)
            blogCreated = TimeAct.parse_timestring(blogCreated, "%Y-%m-%d %H:%M")
            int_gen = StrAct.parse_integer(blogCreated.timestamp())
            blogCreated, int_gen = BaseAct.parse_generator(int_gen)
            if blogCreated is False:
                blogCreated = 0
            # type 0 pic/1 video
            blogPicUrl = []
            pic_gen = JsonAct.parse_json(i, "$.imageList.*.url")
            for p in pic_gen:
                if p.startswith("http"):
                    blogPicUrl.append(p)
                else:
                    blogPicUrl.append("https:" + p)
            blogPicNum = len(blogPicUrl)
            # check type
            blogType = self.json_first(i, "$.type", 1)
            if "video" in blogType:
                blogType = 1
                blogPicUrl = []
                blogPicNum = 0
            else:
                blogType = 0
            # video
            blogVideo = self.json_first(i, "$.video.url", 1)
            if blogVideo and not blogVideo.startswith("http"):
                blogVideo = "https:" + blogVideo
            blogDuration = self.json_number(i, "$.video.duration", 1)
            # count data
            blogLike = self.json_number(i, "$.likes", 1)
            blogComment = self.json_number(i, "$.comments", 1)
            blogCollect = self.json_number(i, "$.collects", 1)
            blogShare = self.json_number(i, "$.shareCount", 1)
            # take data and return
            self.workBase = {
                "id": blogId, "showId": blogId, "scrapeUrl": blogUrl,
                "url": blogUrl, "uid": "", "nickname": "",
                "type": blogType, "title": blogTitle, "cover": blogCover,
                "created": blogCreated, "source": "", "extra": "",
                "desc": blogDesc, "duration": blogDuration, "videoUrl": blogVideo,
                "picNum": blogPicNum, "picUrl": blogPicUrl,

                "likeNum": blogLike, "commentNum": blogComment, "shareNum": blogShare,
                "forwardNum": blogShare, "collectNum": blogCollect,
                "playNum": 0, "viewNum": 0,
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
            "field": "", "isMember": isMember, "isAuth": isAuth,
            "gender": gender, "age": "", "birth": "", "constellation": "",
            "area": area, "notice": "", "desc": desc,
            "memberLevel": str(memberLevel), "memberType": "", "memberDetail": "",
            "authLevel": "", "authType": str(authType), "authDetail": str(authDetail),
            "isCompany": 0, "isGovernmentMedia": 0
        }
        self.profileCounts = {
            "fansNum": fansNum, "followNum": followNum,
            "videos": 0, "blogs": blogs, "worksNum": blogs,
            "favoriteNum": 0, "collectNum": collectNum, "likeNum": likeNum,
            "playNum": 0, "viewNum": 0, "rewardNum": 0
        }

        self.get_return(4, 1)
        return True

    def pass_work(self) -> bool:
        # work flow
        x_sign = "X" + EncryptAct.format_md5(
            f"/fe_api/burdock/baidu/v2/note/{self.work_id}" + "WSUDD")
        self.net.url = f"https://www.xiaohongshu.com/fe_api/burdock/" \
                       f"baidu/v2/note/{self.work_id}"
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "asid": self.asid,
            "X-Sign": x_sign,
            "X-B3-TraceId": "90ac2ed87e44757f",
            "X-Bd-Traceid": "53d8437db6ee444fb68058d7ca8ecb13",
            "Host": "www.xiaohongshu.com",
            "Content-Type": "application/json; charset=utf-8",
            "Referer": "https://smartapps.cn/KuRdr9OR39BqyAGIg7mYK7Bytityu0Vi"
                       "/2.35.16/page-frame.html"
        })
        if not self.net.get_response("get"):
            return False
        # check 404 page
        if self.net.code in [403, 404]:
            self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(4, 0)
            return True
        if not self.net.get_page("json", False):
            return False
        success_gen = JsonAct.parse_json(self.net.page, "$.success")
        success, success_gen = BaseAct.parse_generator(success_gen)
        msg_gen = JsonAct.parse_json(self.net.page, "$.msg")
        msg, msg_gen = BaseAct.parse_generator(msg_gen)
        if success:
            return True
        else:
            if "censored" in msg:
                self.logger.info(f"请求正被审查(*>﹏<*)【{self.scrapeUrl}】")
                return False
            if self.retry_num == 3:
                self.logger.info(f"非法slider失败(*>﹏<*)【slide{self.retry_num}】")
                return False
            else:
                self.logger.info("非法slider出现(*>﹏<*)【captcha】")
                if self.pass_slider():
                    # get the work again
                    return self.pass_work()
                else:
                    return False

    def pass_profile(self) -> None:
        # profile flow
        self.homeUrl = f"https://www.xiaohongshu.com/user/profile/{self.user_id}"
        x_sign = "X" + EncryptAct.format_md5(
            f"/fe_api/burdock/baidu/v2/user/{self.user_id}" + "WSUDD")
        self.net.url = f"https://www.xiaohongshu.com/fe_api/burdock/" \
                       f"baidu/v2/user/{self.user_id}"
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "asid": self.asid,
            "X-Sign": x_sign,
            "X-B3-TraceId": "90ac2ed87e44757f",
            "X-Bd-Traceid": "53d8437db6ee444fb68058d7ca8ecb13",
            "Host": "www.xiaohongshu.com",
            "Content-Type": "application/json; charset=utf-8",
            "Referer": "https://smartapps.cn/KuRdr9OR39BqyAGIg7mYK7Bytityu0Vi"
                       "/2.35.16/page-frame.html"
        })
        if not self.net.get_response("get"):
            return False
        # check 404 page
        if self.net.code in [403, 404]:
            self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(4, 0)
            return True
        if not self.net.get_page("json", False):
            return False
        success_gen = JsonAct.parse_json(self.net.page, "$.success")
        success, success_gen = BaseAct.parse_generator(success_gen)
        msg_gen = JsonAct.parse_json(self.net.page, "$.msg")
        msg, msg_gen = BaseAct.parse_generator(msg_gen)
        if success:
            return True
        else:
            if "censored" in msg:
                self.logger.info(f"请求正被审查(*>﹏<*)【{self.scrapeUrl}】")
                return False
            if self.retry_num == 3:
                self.logger.info(f"非法slider失败(*>﹏<*)【slide{self.retry_num}】")
                return False
            else:
                self.logger.info("非法slider出现(*>﹏<*)【captcha】")
                if self.pass_slider():
                    # get the profile again
                    return self.pass_profile()
                else:
                    return False

    def pass_list(self) -> None:
        # @@..! work list of profile
        x_sign = "X" + EncryptAct.format_md5(
            f"/fe_api/burdock/baidu/v2/user/{self.user_id}/notes?page=1&pageSize=4" + "WSUDD")
        self.net.url = f"https://www.xiaohongshu.com/fe_api/burdock/" \
                       f"baidu/v2/user/{self.user_id}/notes?page=1&pageSize=4"
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "asid": self.asid,
            "X-Sign": x_sign,
            "X-B3-TraceId": "90ac2ed87e44757f",
            "X-Bd-Traceid": "53d8437db6ee444fb68058d7ca8ecb13",
            "Host": "www.xiaohongshu.com",
            "Content-Type": "application/json; charset=utf-8",
            "Referer": "https://smartapps.cn/KuRdr9OR39BqyAGIg7mYK7Bytityu0Vi"
                    "/2.35.16/page-frame.html"
        })
        if not self.net.get_response("get"):
            return False
        # check 404 page
        if self.net.code in [403, 404]:
            self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(4, 0)
            return True
        if not self.net.get_page("json", False):
            return False
        success_gen = JsonAct.parse_json(self.net.page, "$.success")
        success, success_gen = BaseAct.parse_generator(success_gen)
        msg_gen = JsonAct.parse_json(self.net.page, "$.msg")
        msg, msg_gen = BaseAct.parse_generator(msg_gen)
        if success:
            return True
        else:
            if "censored" in msg:
                self.logger.info(f"请求正被审查(*>﹏<*)【{self.scrapeUrl}】")
                return False
            if self.retry_num == 3:
                self.logger.info(f"非法slider失败(*>﹏<*)【slide{self.retry_num}】")
                return False
            else:
                self.logger.info("非法slider出现(*>﹏<*)【captcha】")
                if self.pass_slider():
                    # get the work list again
                    return self.pass_list()
                else:
                    return False

    def pass_slider(self, is_first: bool = True) -> bool:
        # slider flow
        if self.retry_num == 3:
            self.logger.info(f"非法slider失败(*>﹏<*)【slide{self.retry_num}】")
            return False
        else:
            if is_first:
                # get slider page
                self.net.url = "https://www.xiaohongshu.com/web-slider-validation" \
                               "?platform=baidu"
                self.net.headers = BaseAct.format_copy(self.init_header)
                self.net.headers.update({
                    "Host": "www.xiaohongshu.com",
                    "Upgrade-Insecure-Requests": "1",
                    "X-Requested-With": "com.baidu.searchbox",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-User": "?1",
                    "Sec-Fetch-Site": "none",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                            "image/webp,image/apng,*/*;q=0.8,"
                            "application/signed-exchange;v=b3",
                    "Accept-Encoding": "gzip, deflate",
                    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                })
                if not self.net.get_response("get"):
                    return False
                if not self.net.get_page("text", False):
                    return False
                time_now = TimeAct.format_timestamp(3)
                self.net.url = "https://captcha.fengkongcloud.cn/ca/v1/conf"
                self.net.params = (
                    ("sdkver", "1.1.3"), ("channel", "miniProgram_baidu"),
                    ("rversion", "1.0.1"), ("appId", "default"),
                    ("organization", "eR46sBuqF0fdw7KWFLYa"), ("lang", "zh-cn"),
                    ("callback", f"sm_{time_now}"), ("model", "slide")
                )
                self.net.headers = BaseAct.format_copy(self.init_header)
                self.net.headers.update({
                    "Host": "captcha.fengkongcloud.cn",
                    "Sec-Fetch-Mode": "no-cors",
                    "Accept": "*/*",
                    "X-Requested-With": "com.baidu.searchbox",
                    "Sec-Fetch-Site": "cross-site",
                    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Accept-Encoding": "gzip, deflate",
                    "Referer": "https://www.xiaohongshu.com/web-slider-validation"
                            "?platform=baidu"
                })
                if not self.net.get_response("get"):
                    return False
                if not self.net.get_page("text", False):
                    return False
            # @@..! get pic and retry pic
            time_now = TimeAct.format_timestamp(3)
            self.net.url = "https://captcha.fengkongcloud.cn/ca/v1/register"
            self.net.params = (
                ("sdkver", "1.1.3"), ("data", {}), ("channel", "miniProgram_baidu"),
                ("rversion", "1.0.1"), ("appId", "default"), ("lang", "zh-cn"),
                ("organization", "eR46sBuqF0fdw7KWFLYa"), ("model", "slide"),
                ("callback", f"sm_{time_now}")
            )
            self.net.headers = BaseAct.format_copy(self.init_header)
            self.net.headers.update({
                "Host": "captcha.fengkongcloud.cn",
                "Sec-Fetch-Mode": "no-cors",
                "Accept": "*/*",
                "X-Requested-With": "com.baidu.searchbox",
                "Sec-Fetch-Site": "cross-site",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "Accept-Encoding": "gzip, deflate",
                "Referer": "https://www.xiaohongshu.com/web-slider-validation"
                           "?platform=baidu"
            })
            if not self.net.get_response("get"):
                return False
            if not self.net.get_page("text", False):
                return False
            result_gen = StrAct.parse_regex(self.net.page, f"sm_{time_now}\\((.*)\\)")
            result_data, result_gen = BaseAct.parse_generator(result_gen)
            result_dict = JsonAct.format_json(result_data)
            # check
            riskLevel = result_dict.get("riskLevel")
            if riskLevel != "PASS":
                self.retry_num += 1
                return self.pass_slider(False)
            # get base data
            rid = result_dict.get("detail", {}).get("rid")
            bg = result_dict.get("detail", {}).get("bg")
            bg_width = result_dict.get("detail", {}).get("bg_width")
            bg_height = result_dict.get("detail", {}).get("bg_height")
            fg = result_dict.get("detail", {}).get("fg")
            bg_url = "https://castatic.fengkongcloud.cn" + bg
            fg_url = "https://castatic.fengkongcloud.cn" + fg
            # get the back pic
            self.net.url = bg_url
            self.net.params = ()
            self.net.headers["Accept"] = "image/webp,image/apng,image/*,*/*;q=0.8"
            self.net.headers["Host"] = "castatic.fengkongcloud.cn"
            if not self.net.get_response("get"):
                return False
            if not self.net.get_page("content"):
                return False
            bg_bytes = self.data.parse_io(self.net.page, False)
            # get the front pic
            self.net.url = fg_url
            if not self.net.get_response("get"):
                return False
            if not self.net.get_page("content"):
                return False
            fg_bytes = self.data.parse_io(self.net.page, False)
            # count the distance
            distance = self.data.parse_distance(fg_bytes, bg_bytes)
            distance = int(distance / bg_width * bg_height)
            tracks = self.get_tracks(distance)
            # take the args
            organization = "eR46sBuqF0fdw7KWFLYa"
            appId = "default"
            channel = "miniProgram_baidu"
            lang = "zh-cn"
            width = bg_width / 2
            height = bg_height / 2
            start_time = TimeAct.format_timestamp(3)
            slide_time = NumAct.format_random(start_num=2, end_num=4)
            slide_time += NumAct.format_random(True)
            TimeAct.format_sleep(slide_time)
            end_time = TimeAct.format_timestamp(3)
            
            zt = EncryptAct.format_des(-1, "ef982c5f", 1)
            kf = EncryptAct.format_des(0, "c038d018", 1)
            cl = EncryptAct.format_des(0, "6fb3e9cc", 1)
            de = EncryptAct.format_des(appId, "a32b83f9", 1)
            cx = EncryptAct.format_des(channel, "acb0a65b", 1)
            xq = EncryptAct.format_des(lang, "ab6acbc5", 1)
            wi = EncryptAct.format_des(width, "eee44d2f", 1)
            qy = EncryptAct.format_des(height, "791c3b23", 1)
            it = EncryptAct.format_des(round(distance / width, 2), "935a1d89", 1)
            sr = EncryptAct.format_des(tracks, "cd44fad0", 1)
            hl = EncryptAct.format_des(end_time - start_time, "2e9c3c36", 1)
            # verify
            time_now = TimeAct.format_timestamp(3)
            self.net.url = "https://captcha.fengkongcloud.cn/ca/v2/fverify"
            self.net.params = (
                ("rversion", "1.0.1"), ("sdkver", "1.1.3"), ("cx", cx),
                ("protocol", "146"), ("wi", wi), ("kf", kf), ("ostype", "web"),
                ("hl", hl), ("sr", sr), ("act.os", "web_mobile"), ("zt", zt),
                ("callback", f"sm_{time_now}"), ("de", de), ("xq", xq), ("qy", qy),
                ("rid", rid), ("cl", cl), ("it", it), ("organization", organization)
            )
            self.net.headers = BaseAct.format_copy(self.init_header)
            self.net.headers["Accept"] = "*/*"
            self.net.headers["Host"] = "captcha.fengkongcloud.cn"
            if not self.net.get_response("get"):
                return False
            if not self.net.get_page("text", False):
                return False
            # get the result
            x_sign = "X" + EncryptAct.format_md5(
                "/fe_api/burdock/baidu/v2/shield/captcha" + "WSUDD")
            self.net.url = "https://www.xiaohongshu.com/fe_api/burdock/" \
                           "baidu/v2/shield/captcha"
            self.net.params = ()
            self.net.headers = BaseAct.format_copy(self.init_header)
            self.net.headers.update({
                "asid": self.asid,
                "X-Sign": x_sign,
                "X-B3-TraceId": "90ac2ed87e44757f",
                "X-Bd-Traceid": "53d8437db6ee444fb68058d7ca8ecb13",
                "Host": "www.xiaohongshu.com",
                "Content-Type": "application/json; charset=utf-8",
                "Referer": "https://smartapps.cn/KuRdr9OR39BqyAGIg7mYK7Bytityu0Vi"
                        "/2.35.16/page-frame.html"
            })
            self.net.posts = {"rid": rid, "asid": self.asid, "status": 1}
            if not self.net.get_response("post", "json"):
                return False
            if not self.net.get_page("json", False):
                return False
            # check
            self.retry_num += 1
            message = self.net.page.get("data", {}).get("message")
            if message != "正常":
                return self.pass_slider(False)
            return True

    def get_tracks(self, distance):
        """
        生成随机的轨迹
        """
        tracks = []

        y = 0
        v = 0
        t = 1
        current = 0
        mid = distance * 3 / 4
        exceed = 20
        z = t

        tracks.append([0, 0, 1])

        while current < (distance + exceed):
            if current < mid / 2:
                a = 15
            elif current < mid:
                a = 20
            else:
                a = -30
            a /= 2
            v0 = v
            s = v0 * t + 0.5 * a * (t * t)
            current += int(s)
            v = v0 + a * t

            y += NumAct.format_random(start_num=-5, end_num=5)
            z += 100 + NumAct.format_random(start_num=0, end_num=10)

            tracks.append([min(current, (distance + exceed)), y, z])

        while exceed > 0:
            exceed -= NumAct.format_random(start_num=0, end_num=5)
            y += NumAct.format_random(start_num=-5, end_num=5)
            z += 100 + NumAct.format_random(start_num=0, end_num=10)
            tracks.append([min(current, (distance + exceed)), y, z])

        return tracks




# # @@..! web scrape
# class PersHSWorker(BaseWorker):
#     """
#     [xiaohongshu web scrape]
#     """
#     def process_index(self) -> bool:
#         # index flow
#         if self.flowType == 1:
#             return self.process_profile()
#         elif self.flowType == 2:
#             if self.get_work():
#                 return True
#             else:
#                 if not self.work_id:
#                     self.logger.info(f"非法work号码(*>﹏<*)【{self.work_id}】")
#                     return False
#                 return self.process_work()
#         else:
#             self.logger.info(f"非法flow类型(*>﹏<*)【{self.flowType}】")
#             return False

#     def get_work(self) -> bool:
#         # @@..! at least need {'timestamp2': ''}, otherwise the slider appears
#         # @@..! set the blacklist and whitelist
#         self.blacklist = {"video.weibo.com"}
#         self.whitelist = {"xiaohongshu.com", "xhslink.com"}
#         if self.process_verify(self.scrapeUrl):
#             self.get_return(4, 0)
#             return True
#         # @@... ways of parse work_id
#         if "www.xiaohongshu.com" in self.url_domain and self.url_path:
#             self.work_id = self.regex_first(self.url_path, "/discovery/item/(.*)")

#         elif "xhslink.com" in self.url_domain and self.url_path:
#             self.net.url = self.scrapeUrl
#             self.net.headers = BaseAct.format_copy(self.init_header)
#             self.net.headers.update({
#                 "Host": "xhslink.com",
#                 "Upgrade-Insecure-Requests": "1",
#                 "Sec-Fetch-Site": "none",
#                 "Sec-Fetch-Mode": "navigate",
#                 "Sec-Fetch-Dest": "document"
#             })
#             if not self.net.get_response("get"):
#                 return False
#             if not self.net.get_page("text", False):
#                 return False
#             # parse next jump
#             html_dom = DomAct.parse_dom(self.net.page)
#             redirect_gen = DomAct.parse_selector(html_dom, "a", "href")
#             redirect_url, redirect_gen = BaseAct.parse_generator(redirect_gen)
#             if redirect_url is False or self.process_verify(redirect_url):
#                 self.logger.info(f"非法xhslink跳转(*>﹏<*)【{self.scrapeUrl}】")
#                 self.get_return(4, 0)
#                 return True
#             if "www.xiaohongshu.com" in self.url_domain and self.url_path:
#                 self.work_id = self.regex_first(
#                     self.url_path, "/discovery/item/(.*)")

#             else:
#                 self.logger.info(f"非法xhslink跳转(*>﹏<*)【{self.scrapeUrl}】")
#                 self.get_return(4, 0)
#                 return True
#         else:
#             self.logger.info(f"非法url链接(*>﹏<*)【{self.scrapeUrl}】")
#             self.get_return(4, 0)
#             return True
#         # check work_id
#         if self.work_id is False:
#             self.logger.info(f"非法work号码(*>﹏<*)【{self.scrapeUrl}】")
#             self.get_return(4, 0)
#             return True
#         # @@..! return false is do nothing
#         return False

#     def process_work(self) -> bool:
#         # after get work_id, get work page
#         if not self.pass_work():
#             return False
#         # check 404 page
#         if self.net.code in [403, 404]:
#             self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
#             self.get_return(4, 0)
#             return True
#         # check slider
#         if "redirectPath" in self.net.response.url:
#             if not self.pass_slider():
#                 return False
#             # get work page again
#             if not self.pass_work():
#                 return False
#             # check 404 page
#             if self.net.code in [403, 404]:
#                 self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
#                 self.get_return(4, 0)
#                 return True
#             # check slider again
#             if "redirectPath" in self.net.response.url:
#                 self.logger.info("非法cookies二次(*>﹏<*)【captcha】")
#                 return False
# #######################################################################################
#         # parse data and check
#         regex_string = self.regex_first(
#             self.net.page, "__INITIAL_SSR_STATE__\\s{0,}=\\s{0,}({.*})\\s{0,}")
#         regex_dict = JsonAct.format_json(regex_string)
#         if not regex_dict:
#             self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
#             return False
#         blogId = self.json_first(regex_dict, "$.NoteView.noteInfo.id", 0)
#         if not blogId:
#             self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
#             return False
#         # base data
#         blogUrl = f"https://www.xiaohongshu.com/discovery/item/{self.work_id}"
#         blogCover = self.json_first(regex_dict, "$.NoteView.noteInfo.cover.url", 1)
#         if blogCover and not blogCover.startswith("http"):
#             blogCover = "https:" + blogCover
#         blogTitle = self.json_first(regex_dict, "$.NoteView.noteInfo.title", 1)
#         blogDesc = self.json_first(regex_dict, "$.NoteView.noteInfo.desc", 1)
#         blogCreated = self.json_first(regex_dict, "$.NoteView.noteInfo.time", 1)
#         blogCreated = TimeAct.parse_timestring(blogCreated, "%Y-%m-%d %H:%M")
#         int_gen = StrAct.parse_integer(blogCreated.timestamp())
#         blogCreated, int_gen = BaseAct.parse_generator(int_gen)
#         if blogCreated is False:
#             blogCreated = 0
#         # type 0 pic/1 video
#         blogType = self.json_first(regex_dict, "$.NoteView.noteInfo.type", 1)
#         if "video" in blogType:
#             blogType = 1
#         else:
#             blogType = 0
#         # pic
#         blogPicUrl = []
#         pic_gen = JsonAct.parse_json(
#             regex_dict, "$.NoteView.noteInfo.imageList.*.url")
#         for i in pic_gen:
#             if i.startswith("http"):
#                 blogPicUrl.append(i)
#             else:
#                 blogPicUrl.append("https:" + i)
#         blogPicNum = len(blogPicUrl)
#         # video
#         blogVideo = self.json_first(regex_dict, "$.NoteView.noteInfo.video.url", 1)
#         if blogVideo and not blogVideo.startswith("http"):
#             blogVideo = "https:" + blogVideo
#         blogDuration = self.json_number(
#             regex_dict, "$.NoteView.noteInfo.video.duration", 1)
#         # count data
#         blogLike = self.json_number(regex_dict, "$.NoteView.noteInfo.likes", 1)
#         blogComment = self.json_number(regex_dict, "$.NoteView.noteInfo.comments", 1)
#         blogCollect = self.json_number(regex_dict, "$.NoteView.noteInfo.collects", 1)
#         blogShare = self.json_number(regex_dict, "$.NoteView.noteInfo.shareCount", 1)
#         # take data and return
#         if not self.isLast:
#             self.isLast = 0
#         self.workBase = {
#             "id": blogId, "url": blogUrl, "scrapeUrl": blogUrl,
#             "cover": blogCover, "title": blogTitle,
#             "desc": blogDesc, "type": blogType,
#             "likeNum": blogLike, "commentNum": blogComment,
#             "shareNum": blogShare, "collectNum": blogCollect,
#             "created": blogCreated,
#             "picNum": blogPicNum, "picUrl": blogPicUrl,
#             "videoUrl": blogVideo, "duration": blogDuration
#         }
#         self.get_return(4, 1)
#         return True

#     def get_profile(self) -> bool:
#         # @@..! at least need {'timestamp2': ''}, otherwise the slider appears
#         # @@..! set the blacklist and whitelist
#         self.blacklist = {"video.weibo.com"}
#         self.whitelist = {"xiaohongshu.com"}
#         if self.process_verify(self.scrapeUrl):
#             self.get_return(4, 0)
#             return True
#         # @@... ways of parse user_id
#         if "/user/profile/" not in self.url_path:
#             self.logger.info(f"非法profile页面(*>﹏<*)【{self.scrapeUrl}】")
#             self.get_return(4, 0)
#             return True
#         # check user_id
#         self.user_id = self.regex_first(self.url_path, "/profile/(.*)")
#         if not self.user_id:
#             self.logger.info(f"非法user号码(*>﹏<*)【{self.scrapeUrl}】")
#             self.get_return(4, 0)
#             return True
#         # @@..! return false is do nothing
#         return False

#     def process_profile(self) -> bool:
#         # get user_id
#         if self.get_profile():
#             return True
#         else:
#             if not self.user_id:
#                 self.logger.info(f"非法user号码(*>﹏<*)【{self.user_id}】")
#                 return False
#         # @@..! set cookie
#         self.net.url = "http://api.lolqq.xyz/api/device/"
#         self.net.headers = {}
#         if not self.net.get_response("get"):
#             return False
#         if not self.net.get_page("json"):
#             return False
#         device_cookie = self.json_first(self.net.page, "$.timestamp2", 1)
#         self.net.set_cookie({"timestamp2": device_cookie})
#         # after get user_id, get profile page
#         if not self.pass_profile():
#             return False
#         # check 404 page
#         if self.net.code in [403, 404]:
#             self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
#             self.get_return(4, 0)
#             return True
#         # check slider
#         if "redirectPath" in self.net.response.url:
#             if not self.pass_slider():
#                 return False
#             # get profile page again
#             if not self.pass_profile():
#                 return False
#             # check slider again
#             if "redirectPath" in self.net.response.url:
#                 self.logger.info("非法cookies二次(*>﹏<*)【captcha】")
#                 return False
# #######################################################################################
#         # @@... get info data, the second page undone
#         result_data = self.regex_first(
#             self.net.page, "__INITIAL_SSR_STATE__\\s{0,}=\\s{0,}({.*})\\s{0,}")
#         result_dict = JsonAct.format_json(result_data)
#         if not result_dict:
#             self.logger.info(f"非法page数据(*>﹏<*)【{self.scrapeUrl}】")
#             return False
#         user_info = self.json_first(result_dict, "$.Main.userDetail", 0)
#         # check second page data
#         if user_info is False:
#             self.logger.info(f"非法json一次(*>﹏<*)【{self.scrapeUrl}】")
#             user_info = self.json_first(
#                 result_dict, "$.ProfileLayout.userInfo", 0)
#             if user_info is False:
#                 self.logger.info(f"非法json二次(*>﹏<*)【{self.scrapeUrl}】")
#                 self.logger.info(self.net.page)
#                 return False
#             else:
#                 self.logger.info(f"获取json二次(*>﹏<*)【{self.scrapeUrl}】")
#                 self.logger.info(user_info)
#                 return False
#         # check user_id
#         userId = self.json_first(user_info, "$.id", 0)
#         if not userId and userId != self.user_id:
#             self.logger.info("非法user号码(*>﹏<*)【page】")
#             self.get_return(4, 0)
#             return True
#         userId = str(userId)
#         # parse data
#         accountId = self.json_first(user_info, "$.redId", 1)
#         accountId = str(accountId)
#         nickname = self.json_first(user_info, "$.nickname", 1)
#         avatar = self.json_first(user_info, "$.image", 1)
#         gender = self.json_number(user_info, "$.gender", 1)
#         area = self.json_first(user_info, "$.location", 1)
#         desc = self.json_first(user_info, "$.desc", 1)
#         memberLevel = self.json_first(user_info, "$.level.name", 1)
#         isAuth = self.json_first(user_info, "$.officialVerified", 1)
#         authType = self.json_first(user_info, "$.redOfficialVerifyType", 1)
#         authDetail = self.json_first(user_info, "$.verifyContent", 1)
#         # format the data
#         if gender == 0:
#             gender = 1
#         elif gender == 1:
#             gender = 2
#         else:
#             gender = 0
#         if memberLevel:
#             isMember = 1
#         else:
#             memberLevel = ""
#             isMember = 2
#         if isAuth:
#             isAuth = 1
#         else:
#             isAuth = 2
#         # count data
#         followNum = self.json_number(user_info, "$.follows", 1)
#         fansNum = self.json_number(user_info, "$.fans", 1)
#         blogs = self.json_number(user_info, "$.notes", 1)
#         collectNum = self.json_number(user_info, "$.collected", 1)
#         likeNum = self.json_number(user_info, "$.liked", 1)
# #######################################################################################
#         self.scrapeUrl = f"https://www.xiaohongshu.com/user/profile/{self.user_id}"
#         # if certify take data and return
#         if self.toolType == 1:
#             self.profileCounts = {'fansNum': fansNum, 'followNum': followNum}
#             self.get_return(4, 1)
#             return True

#         # @@..! new get work
#         # @@..! set isUrls is 0 and isLast is 1
#         self.isUrls = 0
#         self.isLast = 1
#         # get blog ids list and take urls
#         work_nums = 10
#         if self.toolType == 2:
#             work_nums = 5
#         blog_gen = JsonAct.parse_json(result_dict, f"$.Main.notesDetail.[:{work_nums}]")
#         for i in blog_gen:
#             # get id and check
#             blogId = self.json_first(i, "$.id", 0)
#             if not blogId:
#                 self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
#                 continue
#             blogUrl = f"https://www.xiaohongshu.com/discovery/item/{blogId}"
#             # @@..! take url list
#             self.workUrls.append(blogUrl)
#             # base data
#             blogCover = self.json_first(i, "$.cover.url", 1)
#             if blogCover and not blogCover.startswith("http"):
#                 blogCover = "https:" + blogCover
#             blogTitle = self.json_first(i, "$.title", 1)
#             blogDesc = self.json_first(i, "$.desc", 1)
#             blogCreated = self.json_first(i, "$.time", 1)
#             blogCreated = TimeAct.parse_timestring(blogCreated, "%Y-%m-%d %H:%M")
#             int_gen = StrAct.parse_integer(blogCreated.timestamp())
#             blogCreated, int_gen = BaseAct.parse_generator(int_gen)
#             if blogCreated is False:
#                 blogCreated = 0
#             # type 0 pic/1 video
#             blogType = self.json_first(i, "$.type", 1)
#             if "video" in blogType:
#                 blogType = 1
#             else:
#                 blogType = 0
#             # pic
#             blogPicUrl = []
#             pic_gen = JsonAct.parse_json(i, "$.imageList.*.url")
#             for i in pic_gen:
#                 if i.startswith("http"):
#                     blogPicUrl.append(i)
#                 else:
#                     blogPicUrl.append("https:" + i)
#             blogPicNum = len(blogPicUrl)
#             # video
#             blogVideo = self.json_first(i, "$.video.url", 1)
#             if blogVideo and not blogVideo.startswith("http"):
#                 blogVideo = "https:" + blogVideo
#             blogDuration = self.json_number(i, "$.video.duration", 1)
#             # count data
#             blogLike = self.json_number(i, "$.likes", 1)
#             blogComment = self.json_number(i, "$.comments", 1)
#             blogCollect = self.json_number(i, "$.collects", 1)
#             blogShare = self.json_number(i, "$.shareCount", 1)
#             # take data and return
#             self.workBase = {
#                 "id": blogId, "url": blogUrl, "scrapeUrl": blogUrl,
#                 "cover": blogCover, "title": blogTitle,
#                 "desc": blogDesc, "type": blogType,
#                 "likeNum": blogLike, "commentNum": blogComment,
#                 "shareNum": blogShare, "collectNum": blogCollect,
#                 "created": blogCreated,
#                 "picNum": blogPicNum, "picUrl": blogPicUrl,
#                 "videoUrl": blogVideo, "duration": blogDuration
#             }
#             # if tool type is not 1, take list
#             if self.toolType != 1:
#                 self.workList.append(self.workBase)
#         # @@..! matchUid -> userId
#         # take base and counts data and return
#         self.profileBase = {
#             'userId': userId, 'accountId': accountId, "matchUid": userId, 
#             'avatar': avatar, 'nickname': nickname,
#             "gender": gender, 'area': area, 'desc': desc,
#             "isMember": isMember, "memberLevel": memberLevel, "isAuth": isAuth,
#             "authType": authType, 'authDetail': authDetail}
#         self.profileCounts = {
#             'fansNum': fansNum, 'worksNum': blogs,
#             'followNum': followNum, 'blogs': blogs,
#             "likeNum": likeNum, "collectNum": collectNum}

#         # @@..! new get work must set isLast is 1
#         self.isLast = 1

#         self.get_return(4, 1)
#         return True

#     def pass_work(self) -> bool:
#         # work flow
#         self.net.url = f"https://www.xiaohongshu.com/discovery/item/{self.work_id}"
#         self.net.headers = BaseAct.format_copy(self.init_header)
#         self.net.headers.update({
#             "Host": "www.xiaohongshu.com",
#             "Upgrade-Insecure-Requests": "1",
#             "Sec-Fetch-Site": "none",
#             "Sec-Fetch-User": "?1",
#             "Sec-Fetch-Mode": "navigate",
#             "Sec-Fetch-Dest": "document"
#         })
#         if not self.net.get_response("get", is_redirect=True):
#             return False
#         if not self.net.get_page("text", False):
#             return False

#         return True

#     def pass_profile(self) -> None:
#         # profile flow
#         self.homeUrl = f"https://www.xiaohongshu.com/user/profile/{self.user_id}"
#         self.net.url = self.homeUrl
#         self.net.headers = BaseAct.format_copy(self.init_header)
#         self.net.headers.update({
#             "Host": "www.xiaohongshu.com",
#             "Upgrade-Insecure-Requests": "1",
#             "Sec-Fetch-Site": "none",
#             "Sec-Fetch-User": "?1",
#             "Sec-Fetch-Mode": "navigate",
#             "Sec-Fetch-Dest": "document"
#         })
#         if not self.net.get_response("get", is_redirect=True):
#             return False
#         if not self.net.get_page("text", False):
#             return False

#         return True

#     def pass_slider(self) -> bool:
#         # slider flow
#         self.logger.info("非法slider出现(*>﹏<*)【captcha】")
#         self.net.url = "https://www.xiaohongshu.com/fe_api/burdock/" \
#                        "v2/shield/registerCanvas?p=cc"
#         self.net.headers = BaseAct.format_copy(self.init_header)
#         self.net.headers.update({
#             "Host": "www.xiaohongshu.com",
#             "Content-Type": "application/json",
#             "Accept": "*/*",
#             "Origin": "https://www.xiaohongshu.com",
#             "Referer": self.net.response.url,
#             "Sec-Fetch-Site": "same-origin",
#             "Sec-Fetch-Mode": "cors",
#             "Sec-Fetch-Dest": "empty"
#         })
#         self.net.posts = {
#             "id": "801123fcb37ae83d6085534482bcde42",
#             "sign": f"{self.user_agent}~~~false~~~zh-CN~~~24~~~8~~~8~~~-480~~~"
#                     f"Asia/Shanghai~~~1~~~1~~~1~~~1~~~unknown~~~Win32~~~Chrome "
#                     f"PDF Plugin::Portable Document Format::"
#                     f"application/x-google-chrome-pdf~pdf,Chrome PDF "
#                     f"Viewer::::application/pdf~pdf,"
#                     f"Native Client::::application/x-nacl~,"
#                     f"application/x-pnacl~~~~canvas winding:yes~canvas "
#                     f"fp:af63627abb7f6d68a8cd864315e785a9~~~false~~~false~~~"
#                     f"false~~~false~~~false~~~0;false;"
#                     f"false~~~4;7;8~~~124.04347527516074"}
#         if not self.net.get_response("post", "json"):
#             return False
#         if not self.net.get_page("json"):
#             return False
#         canvas_cookie = self.json_first(self.net.page, "$.data.canvas", 1)
#         if canvas_cookie:
#             self.net.set_cookie({"timestamp2": canvas_cookie})
#         else:
#             self.logger.info("非法cookies刷新(*>﹏<*)【captcha】")
#             return False

#         return True