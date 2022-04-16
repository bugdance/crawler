#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> zhihu ruler
@@..> package tasks.rules
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> base import
from dataclasses import dataclass, field
# @@..> import utils
from .base_ruler import BaseWorker, BaseAct, DomAct, TimeAct, JsonAct, StrAct


@dataclass
class PersZHWorker(BaseWorker):
    """
    [zhihu web scrape]
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
        self.whitelist = {"zhuanlan.zhihu.com"}
        if self.process_verify(self.scrapeUrl):
            self.get_return(7, 0)
            return True
        # @@... ways of parse work_id
        if "/p/" in self.url_path:
            self.work_id = self.regex_first(self.url_path, "/p/(\\d+)")
        else:
            self.logger.info(f"非法work号码(*>﹏<*)【{self.scrapeUrl}】")
            return False
        # check work_id
        if not self.work_id:
            self.logger.info(f"非法work号码(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(7, 0)
            return True
        # @@..! return false is do nothing
        return False

    def process_work(self):
        # after get work_id, get work page
        self.net.url = f"https://zhuanlan.zhihu.com/p/{self.work_id}"
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "zhuanlan.zhihu.com",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
        })
        if not self.net.get_response("get", is_redirect=True):
            return False
        # check 404 page
        if self.net.code == 404:
            self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(7, 0)
            return True
        if not self.net.get_page("text", False):
            return False
        html_dom = DomAct.parse_dom(self.net.page)
        parse_gen = DomAct.parse_selector(html_dom, ".ErrorPage", "class")
        error, parse_gen = BaseAct.parse_generator(parse_gen)
        if error:
            self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(7, 0)
            return True
#######################################################################################
        # parse data and check
        result_data = self.regex_first(self.net.page, '{"initialState".*"}')
        if not result_data:
            self.logger.info(f"非法解析数据(*>﹏<*)【{self.scrapeUrl}】")
            return False
        result_dict = JsonAct.format_json(result_data)
        result_blog = self.json_first(
            result_dict, f"$.initialState.entities.articles.{self.work_id}", 0)
        if not result_blog:
            self.logger.info(f"非法解析数据(*>﹏<*)【{self.scrapeUrl}】")
            return False
#######################################################################################
        # parse data and check
        blogId = self.json_first(result_blog, "$.id", 0)
        if not blogId:
            self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
            return False
        blogUrl = f"http://zhuanlan.zhihu.com/p/{blogId}"
        # base data
        blogUserId = self.json_first(result_blog, "$.author.urlToken", 1)
        blogUserName = self.json_first(result_blog, "$.author.name", 1)
        blogCover = self.json_first(result_blog, "$.imageUrl", 1)
        blogTitle = self.json_first(result_blog, "$.title", 1)
        blogDesc = self.json_first(result_blog, "$.excerpt", 1)
        blogDesc = StrAct.format_html(blogDesc)
        blogDesc = StrAct.format_clear(blogDesc, True)
        blogCreated = self.json_number(result_blog, "$.created", 1)
        # check type
        blogType = 0
        # count data
        blogLike = self.json_number(result_blog, "$.voteupCount", 1)
        blogComment = self.json_number(result_blog, "$.commentCount", 1)
        # take data and return
        if not self.isLast:
            self.isLast = 0
        self.workBase = {
            "id": blogId, "showId": blogId, "scrapeUrl": blogUrl,
            "url": blogUrl, "uid": blogUserId, "nickname": blogUserName,
            "type": blogType, "title": blogTitle, "cover": blogCover,
            "created": blogCreated, "source": "", "extra": "",
            "desc": blogDesc, "duration": 0, "videoUrl": "",
            "picNum": 0, "picUrl": [],
            "likeNum": blogLike, "commentNum": blogComment, 
            "shareNum": 0, "forwardNum": 0, 
            "collectNum": 0, "playNum": 0, "viewNum": 0,
            "rewardNum": 0, "danmakuNum": 0, "blogRepost": {}
        }
        self.get_return(7, 1)
        return True

    def get_profile(self) -> bool:
        # @@..! set the blacklist and whitelist
        self.blacklist = {"creator.douyin.com"}
        self.whitelist = {"www.zhihu.com"}
        if self.process_verify(self.scrapeUrl):
            self.get_return(7, 0)
            return True
        # @@... ways of parse user_id
        if self.url_path and ("/org/" in self.url_path or "/people/" in self.url_path):
            pass
        else:
            self.logger.info(f"非法profile页面(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(7, 0)
            return True
        # check user_id
        counts = self.url_path.count("/")
        if counts == 2:
            self.user_id = self.regex_first(self.url_path, "/.*/(.*)")
        else:
            if "/org/" in self.url_path:
                self.user_id = self.regex_first(self.url_path, "/org/(.*)/")
            elif "/people/" in self.url_path:
                self.user_id = self.regex_first(self.url_path, "/people/(.*)/")
        if not self.user_id:
            self.logger.info(f"非法user号码(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(7, 0)
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
        if "/org/" in self.url_path:
            self.homeUrl = f"https://www.zhihu.com/org/{self.user_id}"
            self.net.url = f"https://www.zhihu.com/org/{self.user_id}/posts"
        elif "/people/" in self.url_path:
            self.homeUrl = f"https://www.zhihu.com/people/{self.user_id}"
            self.net.url = f"https://www.zhihu.com/people/{self.user_id}/posts"
        
        self.net.headers = BaseAct.format_copy(self.init_header)
        self.net.headers.update({
            "Host": "www.zhihu.com",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
        })
        if not self.net.get_response("get", is_redirect=True):
            return False
        # check 404 page
        if self.net.code == 404:
            self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(7, 0)
            return True
        if not self.net.get_page("text", False):
            return False
        html_dom = DomAct.parse_dom(self.net.page)
        parse_gen = DomAct.parse_selector(html_dom, ".ErrorPage", "class")
        error, parse_gen = BaseAct.parse_generator(parse_gen)
        if error:
            self.logger.info(f"非法404页面(*>﹏<*)【{self.scrapeUrl}】")
            self.get_return(7, 0)
            return True
        
        result_data = self.regex_first(self.net.page, '{"initialState".*"}')
        if not result_data:
            self.logger.info(f"非法解析数据(*>﹏<*)【{self.scrapeUrl}】")
            return False
        result_dict = JsonAct.format_json(result_data)
        result_user = self.json_first(
            result_dict, "$.initialState.entities.users", 0)
        if not result_user and isinstance(result_user, dict):
            self.logger.info(f"非法解析数据(*>﹏<*)【{self.scrapeUrl}】")
            return False
#######################################################################################
        # check user_id
        for k, v in result_user.items():
            userId = self.json_first(v, "$.urlToken", 0)
            if not userId and k != v:
                self.logger.info("非法user号码(*>﹏<*)【page】")
                self.get_return(7, 0)
                return True
            userId = str(userId)
            if "/org/" in self.url_path:
                self.homeUrl = f"https://www.zhihu.com/org/{userId}"
            elif "/people/" in self.url_path:
                self.homeUrl = f"https://www.zhihu.com/people/{userId}"
            # parse data
            nickname = self.json_first(v, "$.name", 1)
            avatar = self.json_first(v, "$.avatarUrl", 1)
            gender = self.json_number(v, "$.gender", 1)
            area = self.json_first(v, "$.locations[0].name", 1)
            desc = self.json_first(v, "$.description", 1)
            desc = StrAct.format_html(desc)
            desc = StrAct.format_clear(desc, True)
            notice = self.json_first(v, "$.headline", 1)
            notice = StrAct.format_html(notice)
            notice = StrAct.format_clear(notice, True)
            isMember = self.json_first(v, "$.vipInfo.isVip", 1)
            authDetail = self.json_first(v, "$.badge[0].description", 1)
            isGovernmentMedia = self.json_first(v, "$.isOrg", 1)
            # fields
            fields_list = []
            fields_gen = JsonAct.parse_json(v, "$.badge[0].topics.*.name")
            for i in fields_gen:
                fields_list.append(i)
            if fields_list:
                fields = ",".join(fields_list)
            else:
                fields = ""
            # format the data
            if gender == 0:
                gender = 1
            elif gender == 1:
                gender = 2
            else:
                gender = 0
            if isMember:
                isMember = 1
            else:
                isMember = 2
            if authDetail:
                isAuth = 1
            else:
                isAuth = 2
            if isGovernmentMedia:
                isGovernmentMedia = 1
            else:
                isGovernmentMedia = 2
            # count data
            followNum = self.json_number(v, "$.followingCount", 1)
            fansNum = self.json_number(v, "$.followerCount", 1)
            collectNum = self.json_number(v, "$.favoriteCount", 1)
            likeNum = self.json_number(v, "$.voteupCount", 1)
            # videos = self.json_number(v, "$.zvideoCount", 1)
            blogs = self.json_number(v, "$.articlesCount", 1)
            # favorite equals sum
            followColumns = self.json_number(v, "$.followingColumnsCount", 1)
            followFavlists = self.json_number(v, "$.followingFavlistsCount", 1)
            followQuestion = self.json_number(v, "$.followingQuestionCount", 1)
            followTopic = self.json_number(v, "$.followingTopicCount", 1)
            favoriteNum = followColumns + followFavlists + followQuestion + followTopic
#######################################################################################
        self.scrapeUrl = self.homeUrl
        # if certify take data and return
        if self.toolType == 1:
            self.profileCounts = {'fansNum': fansNum, 'followNum': followNum}
            self.get_return(7, 1)
            return True
        # get work list
        # result_video = self.json_first(
        #     result_dict, "$.initialState.entities.zvideos", 0)
        result_blog = self.json_first(
            result_dict, "$.initialState.entities.articles", 0)
        # @@..! set isUrls is 0 and isLast is 1
        self.isLast = 1
        self.isUrls = 0
        # get blog ids list and take urls
        if result_blog and isinstance(result_blog, dict):
            for k, v in result_blog.items():
                # get id and check
                blogId = self.json_first(v, "$.id", 0)
                if not blogId:
                    self.logger.info(f"非法work数据(*>﹏<*)【{self.scrapeUrl}】")
                    continue
                blogUrl = f"http://zhuanlan.zhihu.com/p/{blogId}"
                # @@..! take url list
                self.workUrls.append(blogUrl)
                # base data
                blogUserId = self.json_first(v, "$.author.urlToken", 1)
                blogUserName = self.json_first(v, "$.author.name", 1)
                blogCover = self.json_first(v, "$.imageUrl", 1)
                blogTitle = self.json_first(v, "$.title", 1)
                blogDesc = self.json_first(v, "$.excerpt", 1)
                blogDesc = StrAct.format_html(blogDesc)
                blogDesc = StrAct.format_clear(blogDesc, True)
                blogCreated = self.json_number(v, "$.created", 1)
                # check type
                blogType = 0
                # count data
                blogLike = self.json_number(v, "$.voteupCount", 1)
                blogComment = self.json_number(v, "$.commentCount", 1)
                # take data and return
                self.workBase = {
                    "id": blogId, "showId": blogId, "scrapeUrl": blogUrl,
                    "url": blogUrl, "uid": blogUserId, "nickname": blogUserName,
                    "type": blogType, "title": blogTitle, "cover": blogCover,
                    "created": blogCreated, "source": "", "extra": "",
                    "desc": blogDesc, "duration": 0, "videoUrl": "",
                    "picNum": 0, "picUrl": [],
                    "likeNum": blogLike, "commentNum": blogComment, 
                    "shareNum": 0, "forwardNum": 0, 
                    "collectNum": 0, "playNum": 0, "viewNum": 0,
                    "rewardNum": 0, "danmakuNum": 0, "blogRepost": {}
                }
                # if tool type is not 1, take list
                if self.toolType != 1:
                    self.workList.append(self.workBase)
        # set numbers
        work_nums = 10
        if self.toolType == 2:
            work_nums = 5
        if self.workList:
            self.workList.reverse()
            self.workList = self.workList[:work_nums]
        if self.workUrls:
            self.workUrls.reverse()
            self.workUrls = self.workUrls[:work_nums]
        # @@..! matchUid -> userId
        # take base and counts data and return
        self.profileBase = {
            "matchUid": userId, "userId": userId, "accountId": userId,
            "secId": "", "avatar": avatar, "qrCode": "", "nickname": nickname,
            "field": fields, "isMember": isMember, "isAuth": isAuth,
            "gender": gender, "age": "", "birth": "", "constellation": "",
            "area": area, "notice": notice, "desc": desc,
            "memberLevel": "", "memberType": "", "memberDetail": "",
            "authLevel": "", "authType": "", "authDetail": str(authDetail),
            "isCompany": 0, "isGovernmentMedia": isGovernmentMedia
        }
        self.profileCounts = {
            "fansNum": fansNum, "followNum": followNum,
            "videos": 0, "blogs": blogs, "worksNum": blogs,
            "favoriteNum": favoriteNum, "collectNum": collectNum, "likeNum": likeNum,
            "playNum": 0, "viewNum": 0, "rewardNum": 0
        }

        self.get_return(7, 1)
        return True


