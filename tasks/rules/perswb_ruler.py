#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> weibo ruler
@@..> package tasks.rules
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> base import
from dataclasses import dataclass, field
# @@..> import utils
from .base_ruler import BaseWorker, BaseAct, DomAct, TimeAct, JsonAct, StrAct


@dataclass
class PersWBWorker(BaseWorker):
    """
    [weibo web scrape]
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
        self.blacklist = {"video.weibo.com"}
        self.whitelist = {"weibo.com", "weibo.cn", "t.sina.com.cn"}
        if self.process_verify(self.scrapeUrl):
            self.get_return(5, 0)
            return True
        # @@... ways of parse work_id
        if self.url_path.count("/") == 2:
            self.work_id = self.regex_first(self.url_path, "/.*/(.*)")
        else:
            self.logger.info(f"非法work号码(*>﹏<*)【{self.scrapeUrl}】")
            return False
        # check work_id
        if not self.work_id:
            self.logger.info(f"非法work号码(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(5, 0)
            return True
        # @@..! return false is do nothing
        return False

    def process_work(self):
        # after get work_id, get work page
        self.net.url = f"https://m.weibo.cn/detail/{self.work_id}"
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "m.weibo.cn",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "same-origin",
            "Sec-Fetch-Dest": "empty",
        })
        if not self.net.get_response("get"):
            return False
        if not self.net.get_page("text"):
            return False
#######################################################################################
        # parse data and check
        regex_string = self.regex_first(
            self.net.page, "\\$render_data\\s{0,}=\\s{0,}(\\[{.*\\}])\\s{0,}")
        regex_dict = JsonAct.format_json(regex_string)
        if not regex_dict:
            self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
            return False
        blogId = self.json_first(regex_dict, "$.*.status.id", 0)
        if not blogId:
            self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
            return False
        # base data
        blogShowId = self.json_first(regex_dict, "$.*.status.bid", 1)
        blogUserId = self.json_first(regex_dict, "$.*.status.user.id", 1)
        blogUserName = self.json_first(regex_dict, "$.*.status.user.screen_name", 1)
        blogUrl = f"https://weibo.com/{blogUserId}/{blogShowId}?type=comment"
        blogScrape = f"https://m.weibo.cn/{blogUserId}/{blogId}"
        blogTitle = self.json_first(regex_dict, "$.*.status.text", 1)
        blogTitle = StrAct.format_html(blogTitle)
        blogTitle = StrAct.format_clear(blogTitle, True)
        blogCover = self.json_first(regex_dict, "$.*.status.pics.[0].url", 1)
        blogSource = self.json_first(regex_dict, "$.*.status.source", 1)
        blogDesc = self.json_first(regex_dict, "$.*.status.text", 1)
        blogDesc = StrAct.format_html(blogDesc)
        blogDesc = StrAct.format_clear(blogDesc, True)
        blogCreated = self.json_first(regex_dict, "$.*.status.created_at", 1)
        blogCreated = TimeAct.parse_timestring(
            blogCreated, "%a %b %d %H:%M:%S +0800 %Y")
        int_gen = StrAct.parse_integer(blogCreated.timestamp())
        blogCreated, int_gen = BaseAct.parse_generator(int_gen)
        if blogCreated is False:
            blogCreated = 0
        # type 0 pic/1 video
        blogType = 0
        blogPicNum = self.json_first(regex_dict, "$.*.status.pic_num", 1)
        blogPicUrl = []
        pic_gen = JsonAct.parse_json(regex_dict, "$.*.status.pics.*.url")
        for j in pic_gen:
            if j.startswith("http"):
                blogPicUrl.append(j)
            else:
                blogPicUrl.append("https:" + j)
        # check video
        blogVideo = self.json_first(regex_dict, "$.*.status.page_info.urls.mp4_hd_mp4", 1)
        if blogVideo:
            blogType = 1
            blogPicNum = 0
            blogPicUrl = []
            sub_place = self.regex_first(blogVideo, "&Expires=\\d+")
            blogVideo = StrAct.parse_replace(blogVideo, sub_place, "&Expires=")
            blogCover = self.json_first(
                regex_dict, "$.*.status.page_info.page_pic.url", 1)
        # count data
        blogLike = self.json_first(regex_dict, "$.*.status.attitudes_count", 1)
        if isinstance(blogLike, str):
            blogLike = StrAct.parse_millions(blogLike)
        blogComment = self.json_first(regex_dict, "$.*.status.comments_count", 1)
        if isinstance(blogComment, str):
            blogComment = StrAct.parse_millions(blogComment)
        blogForward = self.json_first(regex_dict, "$.*.status.reposts_count", 1)
        if isinstance(blogForward, str):
            blogForward = StrAct.parse_millions(blogForward)
        # @@..! retweet data and get id first
        retweetBlog = {}
        retweetId = self.json_first(regex_dict, "$.*.status.retweeted_status.id", 0)
        if retweetId:
            retweetUserId = self.json_first(
                regex_dict, "$.*.status.retweeted_status.user.id", 1)
            retweetUserName = self.json_first(
                regex_dict, "$.*.status.retweeted_status.user.screen_name", 1)
            retweetShowId = self.json_first(
                regex_dict, "$.*.status.retweeted_status.bid", 1)
            retweetUrl = f"https://weibo.com/{retweetUserId}/" \
                         f"{retweetShowId}?type=comment"
            retweetScrape = f"https://m.weibo.cn/{retweetUserId}/{retweetId}"
            retweetTitle = self.json_first(
                regex_dict, "$.*.status.retweeted_status.text", 1)
            retweetTitle = StrAct.format_html(retweetTitle)
            retweetTitle = StrAct.format_clear(retweetTitle, True)
            retweetCover = self.json_first(
                regex_dict, "$.*.status.retweeted_status.pics.[0].url", 1)
            retweetSource = self.json_first(
                regex_dict, "$.*.status.retweeted_status.source", 1)
            retweetDesc = self.json_first(
                regex_dict, "$.*.status.retweeted_status.text", 1)
            retweetDesc = StrAct.format_html(retweetDesc)
            retweetDesc = StrAct.format_clear(retweetDesc, True)
            retweetCreated = self.json_first(
                regex_dict, "$.*.status.retweeted_status.created_at", 1)
            retweetCreated = TimeAct.parse_timestring(
                retweetCreated, "%a %b %d %H:%M:%S +0800 %Y")
            int_gen = StrAct.parse_integer(retweetCreated.timestamp())
            retweetCreated, int_gen = BaseAct.parse_generator(int_gen)
            if retweetCreated is False:
                retweetCreated = 0
            # type 0 pic/1 video
            retweetType = 0
            retweetPicNum = self.json_first(
                regex_dict, "$.*.status.retweeted_status.pic_num", 1)
            retweetPicUrl = []
            pic_gen = JsonAct.parse_json(
                regex_dict, "$.*.status.retweeted_status.pics.*.url")
            for j in pic_gen:
                if j.startswith("http"):
                    retweetPicUrl.append(j)
                else:
                    retweetPicUrl.append("https:" + j)
            # check video
            retweetVideo = self.json_first(
                regex_dict, "$.*.status.retweeted_status.page_info.urls.mp4_hd_mp4", 1)
            if retweetVideo:
                retweetType = 1
                retweetPicNum = 0
                retweetPicUrl = []
                sub_place = self.regex_first(retweetVideo, "&Expires=\\d+")
                retweetVideo = StrAct.parse_replace(
                    retweetVideo, sub_place, "&Expires=")
                retweetCover = self.json_first(
                    regex_dict, "$.*.status.retweeted_status.page_info.page_pic.url", 1)
            # count data
            retweetLike = self.json_first(
                regex_dict, "$.*.status.retweeted_status.attitudes_count", 1)
            if isinstance(retweetLike, str):
                retweetLike = StrAct.parse_millions(retweetLike)
            retweetComment = self.json_first(
                regex_dict, "$.*.status.retweeted_status.comments_count", 1)
            if isinstance(retweetComment, str):
                retweetComment = StrAct.parse_millions(retweetComment)
            retweetForward = self.json_first(
                regex_dict, "$.*.status.retweeted_status.reposts_count", 1)
            if isinstance(retweetForward, str):
                retweetForward = StrAct.parse_millions(retweetForward)
            retweetBlog = {
                "id": retweetId, "showId": retweetShowId, "scrapeUrl": retweetScrape,
                "url": retweetUrl, "uid": retweetUserId, "nickname": retweetUserName,
                "type": retweetType, "title": retweetTitle, "cover": retweetCover,
                "created": retweetCreated, "source": retweetSource, "extra": "",
                "desc": retweetDesc, "duration": 0, "videoUrl": retweetVideo,
                "picNum": retweetPicNum, "picUrl": retweetPicUrl,
                
                "likeNum": retweetLike, "commentNum": retweetComment,
                "shareNum": retweetForward, "forwardNum": retweetForward,
                "collectNum": 0, "playNum": 0, "viewNum": 0,
                "rewardNum": 0, "danmakuNum": 0
            }
        # take data and return
        if not self.isLast:
            self.isLast = 0
        self.workBase = {
            "id": blogId, "showId": blogShowId, "scrapeUrl": blogScrape,
            "url": blogUrl, "uid": blogUserId, "nickname": blogUserName,
            "type": blogType, "title": blogTitle, "cover": blogCover,
            "created": blogCreated, "source": blogSource, "extra": "",
            "desc": blogDesc, "duration": 0, "videoUrl": blogVideo,
            "picNum": blogPicNum, "picUrl": blogPicUrl,

            "likeNum": blogLike, "commentNum": blogComment, "shareNum": blogForward,
            "forwardNum": blogForward, "collectNum": 0, "playNum": 0, "viewNum": 0,
            "rewardNum": 0, "danmakuNum": 0, "blogRepost": retweetBlog
        }
        self.get_return(5, 1)
        return True

    def get_profile(self) -> bool:
        # @@..! weibo.com need {'SUB': ''}, status=0 dataBase={} 为失效账号
        # @@..! set the blacklist and whitelist
        self.blacklist = {"video.weibo.com"}
        self.whitelist = {"weibo.com", "weibo.cn", "sina.com.cn", "t.cn"}
        if self.process_verify(self.scrapeUrl):
            self.get_return(5, 0)
            return True
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
                self.get_return(5, 0)
                return True
            # @@..! get scrape url
            self.scrapeUrl = redirect_url
        # @@... ways of parse user_id
        if "weibo" in self.url_domain and self.url_path.startswith("/u/"):
            self.user_id = self.regex_first(self.url_path, "/u/(\\d+)")

        elif "m.weibo.cn" in self.url_domain and not self.url_path.startswith("/u/"):
            self.user_id = self.regex_first(self.url_path, "/(\\d+)")

        elif "weibo.com" in self.url_domain or "t.sina.com.cn" in self.url_domain:
            jump_id = self.regex_first(self.url_path, "/(.*)")
            # get user id
            self.net.url = f"https://m.weibo.cn/{jump_id}?&jumpfrom=weibocom"
            self.net.headers = BaseAct.format_copy(self.init_header)
            self.net.headers.update({
                "Host": "m.weibo.cn",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "same-origin",
                "Sec-Fetch-Dest": "empty"
            })
            if not self.net.get_response("get", is_redirect=True):
                return False
            if not self.net.get_page("text"):
                return False
            if not self.net.response.url or self.process_verify(self.net.response.url):
                self.logger.info(f"非法jumpfrom跳转(*>﹏<*)【{self.scrapeUrl}】")
                self.get_return(5, 0)
                return True
            if "m.weibo.cn" not in self.url_domain and not self.url_path.startswith("/u/"):
                self.logger.info(f"非法jumpfrom跳转(*>﹏<*)【{self.scrapeUrl}】")
                self.get_return(5, 0)
                return True
            self.user_id = self.regex_first(self.url_path, "/u/(\\d+)")
            
        else:
            self.logger.info(f"非法url链接(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(5, 0)
            return True
        # check user_id
        if not self.user_id:
            self.logger.info(f"非法user号码(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(5, 0)
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
        self.homeUrl = f"https://weibo.com/u/{self.user_id}?is_all=1"

        self.net.url = f"https://m.weibo.cn/u/{self.user_id}"
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "m.weibo.cn",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "same-origin",
            "Sec-Fetch-Dest": "empty",
        })
        if not self.net.get_response("get"):
            return False
        if not self.net.get_page("text"):
            return False
        # get token and main_container
        cookies = self.net.get_cookie()
        token = cookies.get("XSRF-TOKEN", "")
        container = cookies.get("M_WEIBOCN_PARAMS", "")
        main_container = self.regex_first(container, "fid%3D(.*?)%26")
        # get info data
        self.net.url = "https://m.weibo.cn/api/config"
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "m.weibo.cn",
            "Accept": "application/json, text/plain, */*",
            "MWeibo-Pwa": "1",
            "X-XSRF-TOKEN": token,
            "X-Requested-With": "XMLHttpRequest",
            "Referer": f"https://m.weibo.cn/u/{self.user_id}",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
        })
        if not self.net.get_response("get"):
            return False
        if not self.net.get_page("json"):
            return False
        self.net.url = f"https://m.weibo.cn/api/container/getIndex?type=uid&" \
                       f"value={self.user_id}&containerid={main_container}"
        if not self.net.get_response("get"):
            return False
        if not self.net.get_page("json"):
            return False
#######################################################################################
        # check user_id
        userId = self.json_first(self.net.page, "$.data.userInfo.id", 0)
        if not userId and userId != self.user_id:
            self.logger.info("非法user号码(*>﹏<*)【page】")
            self.get_return(5, 0)
            return True
        userId = str(userId)
        # parse data
        avatar = self.json_first(self.net.page, "$.data.userInfo.profile_image_url", 1)
        nickname = self.json_first(self.net.page, "$.data.userInfo.screen_name", 1)
        gender = self.json_first(self.net.page, "$.data.userInfo.gender", 1)
        desc = self.json_first(self.net.page, "$.data.userInfo.description", 1)
        memberType = self.json_first(self.net.page, "$.data.userInfo.mbtype", 1)
        memberLevel = self.json_first(self.net.page, "$.data.userInfo.mbrank", 1)
        isAuth = self.json_first(self.net.page, "$.data.userInfo.verified", 1)
        authType = self.json_first(self.net.page, "$.data.userInfo.verified_type", 1)
        authDetail = self.json_first(self.net.page, "$.data.userInfo.verified_reason", 1)
        if "f" in gender:
            gender = 2
        elif "m" in gender:
            gender = 1
        else:
            gender = 0
        if memberLevel:
            isMember = 1
        else:
            isMember = 2
        if isAuth:
            isAuth = 1
        else:
            isAuth = 2
        # count data
        followNum = self.json_first(self.net.page, "$.data.userInfo.follow_count", 1)
        if isinstance(followNum, str):
            followNum = StrAct.parse_millions(followNum)
        fansNum = self.json_first(self.net.page, "$.data.userInfo.followers_count", 1)
        if isinstance(fansNum, str):
            fansNum = StrAct.parse_millions(fansNum)
        blogs = self.json_first(self.net.page, "$.data.userInfo.statuses_count", 1)
        if isinstance(blogs, str):
            blogs = StrAct.parse_millions(blogs)
#######################################################################################
        self.scrapeUrl = f"https://m.weibo.cn/u/{self.user_id}"
        # if certify take data and return
        if self.toolType == 1:
            self.profileCounts = {'fansNum': fansNum, 'followNum': followNum}
            self.get_return(5, 1)
            return True
        # get tabs
        tabs_info = self.json_first(self.net.page, "$.data.tabsInfo.tabs", 1)
        profile_container = ""
        blog_container = ""
        if isinstance(tabs_info, list):
            for t in tabs_info:
                if t.get("tab_type") == "profile":
                    profile_container = t.get("containerid")
                if t.get("tab_type") == "weibo":
                    blog_container = t.get("containerid")
        # get profile tab and get area
        area = ""
        if profile_container:
            self.net.url = f"https://m.weibo.cn/api/container/getIndex?type=uid&" \
                           f"value={self.user_id}&containerid={profile_container}"
            if not self.net.get_response("get"):
                return False
            if not self.net.get_page("json"):
                return False
            area = self.json_first(
                self.net.page, "$.data.cards[*].card_group[*].item_content", 1)
#######################################################################################
        # @@..! set isUrls is 0 and isLast is 1
        self.isUrls = 0
        self.isLast = 1
        # get blog ids list and take urls
        if blog_container:
            self.net.url = f"https://m.weibo.cn/api/container/getIndex?type=uid&" \
                           f"value={self.user_id}&containerid={blog_container}"
            if not self.net.get_response("get"):
                return False
            if not self.net.get_page("json"):
                return False
            # get blog ids list and take urls
            work_nums = 10
            if self.toolType == 2:
                work_nums = 5
            blog_gen = JsonAct.parse_json(
                self.net.page, f"$.data.cards[:{work_nums}]")
            for i in blog_gen:
                # get id and check
                blogId = self.json_first(i, "$.mblog.id", 0)
                if not blogId:
                    self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
                    continue
                blogShowId = self.json_first(i, "$.mblog.bid", 1)
                blogUserId = self.user_id
                blogUserName = nickname
                blogUrl = f"https://weibo.com/{self.user_id}/{blogShowId}?type=comment"
                # @@..! take url list
                self.workUrls.append(blogUrl)
                blogScrape = f"https://m.weibo.cn/{self.user_id}/{blogId}"
                blogTitle = self.json_first(i, "$.mblog.text", 1)
                blogTitle = StrAct.format_html(blogTitle)
                blogTitle = StrAct.format_clear(blogTitle, True)
                blogCover = self.json_first(i, "$.mblog.pics.[0].url", 1)
                blogSource = self.json_first(i, "$.mblog.source", 1)
                blogDesc = self.json_first(i, "$.mblog.text", 1)
                blogDesc = StrAct.format_html(blogDesc)
                blogDesc = StrAct.format_clear(blogDesc, True)
                blogCreated = self.json_first(i, "$.mblog.created_at", 1)
                blogCreated = TimeAct.parse_timestring(
                    blogCreated, "%a %b %d %H:%M:%S +0800 %Y")
                int_gen = StrAct.parse_integer(blogCreated.timestamp())
                blogCreated, int_gen = BaseAct.parse_generator(int_gen)
                if blogCreated is False:
                    blogCreated = 0
                # type 0 pic/1 video
                blogType = 0
                blogPicNum = self.json_first(i, "$.mblog.pic_num", 1)
                blogPicUrl = []
                pic_gen = JsonAct.parse_json(i, "$.mblog.pics.*.url")
                for j in pic_gen:
                    if j.startswith("http"):
                        blogPicUrl.append(j)
                    else:
                        blogPicUrl.append("https:" + j)
                # check video
                blogVideo = self.json_first(i, "$.mblog.page_info.urls.mp4_hd_mp4", 1)
                if blogVideo:
                    blogType = 1
                    blogPicNum = 0
                    blogPicUrl = []
                    sub_place = self.regex_first(blogVideo, "&Expires=\\d+")
                    blogVideo = StrAct.parse_replace(blogVideo, sub_place, "&Expires=")
                    blogCover = self.json_first(
                        i, "$.mblog.page_info.page_pic.url", 1)
                # count data
                blogLike = self.json_first(i, "$.mblog.attitudes_count", 1)
                if isinstance(blogLike, str):
                    blogLike = StrAct.parse_millions(blogLike)
                blogComment = self.json_first(i, "$.mblog.comments_count", 1)
                if isinstance(blogComment, str):
                    blogComment = StrAct.parse_millions(blogComment)
                blogForward = self.json_first(i, "$.mblog.reposts_count", 1)
                if isinstance(blogForward, str):
                    blogForward = StrAct.parse_millions(blogForward)
                # @@..! retweet data and get id first
                retweetBlog = {}
                retweetId = self.json_first(i, "$.mblog.retweeted_status.id", 0)
                if retweetId:
                    retweetUserId = self.json_first(
                        i, "$.mblog.retweeted_status.user.id", 1)
                    retweetUserName = self.json_first(
                        i, "$.mblog.retweeted_status.user.screen_name", 1)
                    retweetShowId = self.json_first(i, "$.mblog.retweeted_status.bid", 1)
                    retweetUrl = f"https://weibo.com/{retweetUserId}/" \
                                 f"{retweetShowId}?type=comment"
                    retweetScrape = f"https://m.weibo.cn/{retweetUserId}/{retweetId}"
                    retweetTitle = self.json_first(
                        i, "$.mblog.retweeted_status.text", 1)
                    retweetTitle = StrAct.format_html(retweetTitle)
                    retweetTitle = StrAct.format_clear(retweetTitle, True)
                    retweetCover = self.json_first(
                        i, "$.mblog.retweeted_status.pics.[0].url", 1)
                    retweetSource = self.json_first(i, "$.mblog.retweeted_status.source", 1)
                    retweetDesc = self.json_first(i, "$.mblog.retweeted_status.text", 1)
                    retweetDesc = StrAct.format_html(retweetDesc)
                    retweetDesc = StrAct.format_clear(retweetDesc, True)
                    retweetCreated = self.json_first(
                        i, "$.mblog.retweeted_status.created_at", 1)
                    retweetCreated = TimeAct.parse_timestring(
                        retweetCreated, "%a %b %d %H:%M:%S +0800 %Y")
                    int_gen = StrAct.parse_integer(retweetCreated.timestamp())
                    retweetCreated, int_gen = BaseAct.parse_generator(int_gen)
                    if retweetCreated is False:
                        retweetCreated = 0
                    # type 0 pic/1 video
                    retweetType = 0
                    retweetPicNum = self.json_first(
                        i, "$.mblog.retweeted_status.pic_num", 1)
                    retweetPicUrl = []
                    pic_gen = JsonAct.parse_json(
                        i, "$.mblog.retweeted_status.pics.*.url")
                    for j in pic_gen:
                        if j.startswith("http"):
                            retweetPicUrl.append(j)
                        else:
                            retweetPicUrl.append("https:" + j)
                    # check video
                    retweetVideo = self.json_first(
                        i, "$.mblog.retweeted_status.page_info.urls.mp4_hd_mp4", 1)
                    if retweetVideo:
                        retweetType = 1
                        retweetPicNum = 0
                        retweetPicUrl = []
                        sub_place = self.regex_first(retweetVideo, "&Expires=\\d+")
                        retweetVideo = StrAct.parse_replace(
                            retweetVideo, sub_place, "&Expires=")
                        retweetCover = self.json_first(
                            i, "$.mblog.retweeted_status.page_info.page_pic.url", 1)
                    # count data
                    retweetLike = self.json_first(
                        i, "$.mblog.retweeted_status.attitudes_count", 1)
                    if isinstance(retweetLike, str):
                        retweetLike = StrAct.parse_millions(retweetLike)
                    retweetComment = self.json_first(
                        i, "$.mblog.retweeted_status.comments_count", 1)
                    if isinstance(retweetComment, str):
                        retweetComment = StrAct.parse_millions(retweetComment)
                    retweetForward = self.json_first(
                        i, "$.mblog.retweeted_status.reposts_count", 1)
                    if isinstance(retweetForward, str):
                        retweetForward = StrAct.parse_millions(retweetForward)
                    retweetBlog = {
                        "id": retweetId, "showId": retweetShowId, "scrapeUrl": retweetScrape,
                        "url": retweetUrl, "uid": retweetUserId, "nickname": retweetUserName,
                        "type": retweetType, "title": retweetTitle, "cover": retweetCover,
                        "created": retweetCreated, "source": retweetSource, "extra": "",
                        "desc": retweetDesc, "duration": 0, "videoUrl": retweetVideo,
                        "picNum": retweetPicNum, "picUrl": retweetPicUrl,
                        
                        "likeNum": retweetLike, "commentNum": retweetComment,
                        "shareNum": retweetForward, "forwardNum": retweetForward,
                        "collectNum": 0, "playNum": 0, "viewNum": 0,
                        "rewardNum": 0, "danmakuNum": 0
                    }
                # take data and return
                self.workBase = {
                    "id": blogId, "showId": blogShowId, "scrapeUrl": blogScrape,
                    "url": blogUrl, "uid": blogUserId, "nickname": blogUserName,
                    "type": blogType, "title": blogTitle, "cover": blogCover,
                    "created": blogCreated, "source": blogSource, "extra": "",
                    "desc": blogDesc, "duration": 0, "videoUrl": blogVideo,
                    "picNum": blogPicNum, "picUrl": blogPicUrl,

                    "likeNum": blogLike, "commentNum": blogComment, "shareNum": blogForward,
                    "forwardNum": blogForward, "collectNum": 0, "playNum": 0, "viewNum": 0,
                    "rewardNum": 0, "danmakuNum": 0, "blogRepost": retweetBlog
                }
                # if tool type is not 1, take list
                if self.toolType != 1:
                    self.workList.append(self.workBase)
        # @@..! matchUid -> userId
        # take base and counts data and return
        self.profileBase = {
            "matchUid": userId, "userId": userId, "accountId": userId,
            "secId": "", "avatar": avatar, "qrCode": "", "nickname": nickname,
            "field": "", "isMember": isMember, "isAuth": isAuth,
            "gender": gender, "age": "", "birth": "", "constellation": "",
            "area": area, "notice": "", "desc": desc,
            "memberLevel": str(memberLevel), "memberType": str(memberType),
            "memberDetail": "", "authLevel": "", 
            "authType": str(authType), "authDetail": str(authDetail),
            "isCompany": 0, "isGovernmentMedia": 0
        }
        self.profileCounts = {
            "fansNum": fansNum, "followNum": followNum,
            "videos": 0, "blogs": blogs, "worksNum": blogs,
            "favoriteNum": 0, "collectNum": 0, "likeNum": 0,
            "playNum": 0, "viewNum": 0, "rewardNum": 0
        }

        self.get_return(5, 1)
        return True
