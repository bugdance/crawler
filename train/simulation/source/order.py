#! /usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
    written by pyleo
"""
import copy
import time


class Order:
    """
    下单占座的流程类
    """
    def __init__(self):
        # ========================类要保持的数据========================
        self.logger = None                                              # 基础日志
        self.base = None                                                # 基础类
        self.main_window = None                                         # 主窗口
        self.assistant_window = None                                    # 副窗口
        self.save_cookies: str = ""                                     # 临时保存的cookie
        self.real_message: str = ""                                     # 真实返回的信息
        self.return_message: str = "系统繁忙，请稍后重试"               # 返回接口的信息
        self.return_status: str = "false"                               # 返回结果状态
        self.proxy_status: str = "proxy_check"                          # 返回代理状态
        # ========================类要配置的数据========================
        self.redis_queue = None                                         # redis队列
        self.redis_result = None                                        # redis结果
        self.redis_machine = None                                       # redis机器
        self.machine_addr: str = ""
        self.circulation_failure = None
        self.proxy_failure = None
        self.proxy_addr: str = ""                                       # 代理服务器
        self.proxy_server: str = ""                                     # 代理地址
        self.proxy_auth: str = "yunku:123"                              # 代理认证
        self.interval = 2                                               # 打码间隔
        self.circulation = 4                                            # 循环次数
        self.page_search = 5                                            # 打开页面查找时间
        self.local_search = 5                                           # 点击按钮本页查找时间
        self.next_search = 10                                           # 点击按钮跳转查找时间
        self.order_proxy = 1                                            # 是否启用代理
        self.cookie_way = 1                                             # 是否cookie登录方式 0 不开启  1 开启
        self.login_way = 1                                              # 登录方式  0 老版登录  1 新版自适应登录  2 打码登录  3 扫码登录
        self.time_out = 5                                              # 加载超时时间
        # ========================接口传来的数据========================
        self.key_label: str = ""                                         # 接口订单编号
        self.login_name: str = ""                                       # 登录账号
        self.login_pwd: str = ""                                        # 登录密码
        self.from_station: str = ""                                     # 起始站名称
        self.to_station: str = ""                                       # 终点站名称
        self.from_abbr: str = ""                                        # 起始站三字码
        self.to_abbr: str = ""                                          # 终点站三字码
        self.train_date: str = ""                                       # 乘车日期
        self.train_code: str = ""                                       # 乘车车次
        self.pay_method: int = 2                                        # 支付方式
        self.cookie: str = ""                                           # 传入的cookie
        self.seat_type: str = ""                                        # 坐席类型
        self.passengers = None                                          # 乘客信息
        # ========================交互使用的数据========================
        self.train_id: str = ""                                         # 购买车次的标签id
        self.add_adults = None                                          # 成人信息
        # ========================需要返回的数据========================
        self.sequence_no: str = ""                                      # 12306占座成功后返回的订单编号
        self.passenger_count: int = 0                                   # 账号已通过个数
        self.consumption_space: int = 0                                 # 消耗空位数
        self.refund_online: int = 0                                     # 是否可在线退票(1可/0不可)
        self.elapsed_time: str = ""                                     # 列车历时
        self.choose_seats: str = ""                                     # 是否可以选座(可以Y/不可以空)
        self.seats_price = None                                         # 到达订单页的坐席价格{坐席：价格}
        self.passengers_all = None                                      # 返回的乘客信息
        self.order_data = None                                          # 返回的12306具体信息
        
    def clear_data(self):
        self.save_cookies: str = ""                                     # 临时保存的cookie
        self.real_message: str = ""                                     # 真实返回的信息
        self.return_message: str = "系统繁忙，请稍后重试"               # 返回接口的信息
        self.return_status: str = "false"                               # 返回结果状态
        self.proxy_status: str = "proxy_check"                          # 返回代理状态
        # ========================接口传来的数据========================
        self.login_name: str = ""                                       # 登录账号
        self.login_pwd: str = ""                                        # 登录密码
        self.from_station: str = ""                                     # 起始站名称
        self.to_station: str = ""                                       # 终点站名称
        self.from_abbr: str = ""                                        # 起始站三字码
        self.to_abbr: str = ""                                          # 终点站三字码
        self.train_date: str = ""                                       # 乘车日期
        self.train_code: str = ""                                       # 乘车车次
        self.pay_method: int = 2                                        # 支付方式
        self.cookie: str = ""                                           # 传入的cookie
        self.seat_type: str = ""                                        # 坐席类型
        self.passengers = None                                          # 乘客信息
        # ========================交互使用的数据========================
        self.train_id: str = ""                                         # 购买车次的标签id
        self.add_adults = None                                          # 成人信息
        # ========================需要返回的数据========================
        self.sequence_no: str = ""                                      # 12306占座成功后返回的订单编号
        self.passenger_count: int = 0                                   # 账号已通过个数
        self.consumption_space: int = 0                                 # 消耗空位数
        self.refund_online: int = 0                                     # 是否可在线退票(1可/0不可)
        self.elapsed_time: str = ""                                     # 列车历时
        self.choose_seats: str = ""                                     # 是否可以选座(可以Y/不可以空)
        self.seats_price = None                                         # 到达订单页的坐席价格{坐席：价格}
        self.passengers_all = None                                      # 返回的乘客信息
        self.order_data = None                                          # 返回的12306具体信息
        
    def parse_data(self, data_dict=None) -> bool:
        """
        解析数据是否成功
        :param data_dict: 外部传入数据字典
        :return: bool
        """
        try:
            if type(data_dict['passengers']) is dict:
                passenger_dict = data_dict['passengers']
            else:
                passenger_dict = eval(data_dict['passengers'])                                      # 获取passengers字段
            passenger_string = passenger_dict.get('passengerTicketStr', "")                         # 获取passengers_string字段
            passenger_list = passenger_string.split('_')
            passenger_final = []                                                                    # 分割乘客信息
            for i in passenger_list:
                passenger_final.append(i.split(','))                                                # 重新整理乘客信息
            self.passengers = passenger_final
            if len(self.passengers) < 1 or len(self.passengers) > 5:                                # 判断人数
                self.logger.info(f"接口乘客人数不符(*>﹏<*)【{len(self.passengers)}】")
                self.real_message = "提交订单失败：乘客人数不符"
                self.return_message = "提交订单失败：乘客人数不符"
                return False
            for i in self.passengers:                                                               # 校验身份证
                if len(i[5]) < 14:
                    self.logger.info(f"接口证件格式不符(*>﹏<*)【{i}】")
                    self.real_message = "提交订单失败：证件格式不对,可能是港澳"
                    self.return_message = "提交订单失败：证件格式不对"
                    return False
            self.pay_method = data_dict.get('payMethod', 2)
            self.login_name, self.login_pwd = data_dict.get('loginName', ''), data_dict.get('loginPwd', '')
            self.from_station, self.from_abbr = data_dict.get('from_station_name', ''), data_dict.get('from_station', '')
            self.to_station, self.to_abbr = data_dict.get('to_station_name', ''), data_dict.get('to_station', '')
            self.train_code, self.train_date = data_dict.get('train_code', ''), data_dict.get('train_date', '')
            self.cookie, self.seat_type = data_dict.get('cookie', ''), data_dict.get('seatTypeOf12306', '')
        except Exception as ex:
            self.logger.info(f"解析接口数据失败(*>﹏<*)【{ex}】")
            self.real_message = "提交订单失败：解析接口数据失败"
            self.return_message = "提交订单失败：乘客人数不符"
            return False
        else:
            self.logger.info(f"解析接口数据成功(*^__^*)【{self.login_name}】【{self.login_pwd}】")
            return True
        
    def execute_process(self, data_dict=None, count: int = 0) -> None:
        """
        下单占座流程函数
        :param data_dict: 外部传入数据
        :param count: 累加计数
        :return: None
        """
        if count >= self.circulation:                                   # 如果最终次数
            if self.order_proxy:                                        # 判断是否开启代理
                self.proxy_status = "proxy_check"
                self.return_proxy()                                     # 归还代理
            if "提交订单成功" in self.real_message:
                self.return_status = "true"
            else:
                self.return_status = "false"
            if "已满" in self.real_message:                         # 如果不需要换账号，停止再来
                self.circulation = 0
            self.return_result()                                        # 归还结果
            self.base.set_quit()
            self.base.set_shell("./kill_all.sh")
        else:
            self.clear_data()
            if self.parse_data(data_dict):                                          # 解析数据是否成功
                self.get_config()                                                   # 获取配置数据
                self.save_cookies = self.cookie                                     # 保存临时cookie
                if self.order_proxy:                                                # 如果开启代理
                    self.get_proxy()                                                # 获取代理
                    self.base.set_proxy(self.proxy_server, self.proxy_auth)         # 设置代理
                if self.base.set_headless(self.proxy_server, self.time_out):         # 开启新会话
                    if self.query_trains():                                         # 查询车次
                        self.main_window = self.base.get_window()                   # 记住本窗口并移动到新页
                        self.base.set_script("window.open('');")
                        self.base.set_window(self.main_window)
                        if self.login_switch():                                     # 登录
                            if self.check_persons():                                # 核验
                                self.base.set_close()
                                self.base.set_switch(self.main_window)
                                if self.query_pass():  # 查询通过
                                    if "未处理" in self.real_message:
                                        if self.verify_unfinished():
                                            return self.execute_process(data_dict, self.circulation + 1)  # 不需要循环累加到最大次数
                                    else:
                                        if self.submit_info():  # 信息确认
                                            if self.submit_pass():  # 提交订单
                                                if "未支付" in self.real_message or "未完成" in self.real_message or "排队" in self.real_message:
                                                    if self.verify_unfinished():
                                                        return self.execute_process(data_dict, self.circulation + 1)  # 不需要循环累加到最大次数
                                                else:
                                                    return self.execute_process(data_dict, self.circulation + 1)  # 不需要循环累加到最大次数
            failure_sign = 0                                                                # 如果以上都失败
            for i in self.circulation_failure:                                      # 匹配失败原因
                if i in self.real_message:                                          # 判断需不需要循环
                    failure_sign = 1
                    break
            if failure_sign:
                if count < self.circulation - 1:
                    if self.order_proxy:  # 判断是否开启代理
                        self.proxy_status = "proxy_check"
                        self.return_proxy()  # 归还代理
                return self.execute_process(data_dict, count + 1)                   # 需要循环累加次数
            else:
                return self.execute_process(data_dict, self.circulation + 1)        # 不需要循环累加到最大次数

    def query_trains(self) -> bool:
        """
        查询车次主要流程
        :return: bool
        """
        if self.base.set_url("https://kyfw.12306.cn/otn/leftTicket/init"):                    # 打开查询页
            if self.base.touch_element("#query_ticket.btn92s", self.page_search):                           # 判断标签
                self.base.set_text('#fromStationText', self.from_station)                                   # 填查询信息
                self.base.set_script(f"document.getElementById('fromStation').value='{self.from_abbr}';")
                self.base.set_script("document.getElementById('fromStationText').setAttribute('class', 'inp-txt inp_selected');")
                self.base.set_text('#toStationText', self.to_station)
                self.base.set_script(f"document.getElementById('toStation').value='{self.to_abbr}';")
                self.base.set_script(f"document.getElementById('toStationText').setAttribute('class', 'inp-txt inp_selected');")
                self.base.set_script(f"document.getElementById('train_date').value='{self.train_date}';")
                time.sleep(1)
                self.base.set_click("#query_ticket.btn92s")
                if self.base.wait_element("#queryLeftTable>tr[id^='ticket_']", self.local_search):          # 加载数据
                    return self.query_book()  # 预定车次
            if self.base.wait_element("div[id^='no_filter_ticket'][style='']"):                     # 判断是否被封
                self.real_message = self.base.get_text("div[id^='no_filter_ticket'][style=''] p")
                self.return_message = self.real_message
                return False
            else:
                if self.base.wait_element("#content_defaultwarningAlert_hearder"):                  # 判断是否错误
                    self.real_message = self.base.get_text("#content_defaultwarningAlert_hearder")
                    self.return_message = self.real_message
                    return False
        if self.base.check_error():
            self.real_message = "获取到错误的页面，网络忙"
            self.return_message = "系统繁忙，请稍后重试"
            return False
        self.real_message = "页面打开失败或操作失败"
        self.return_message = "系统繁忙，请稍后重试"
        return False

    def query_book(self) -> bool:
        """
        查询车次次要流程
        :return: bool
        """
        if self.base.find_element(f"tr[id^='price_'][datatran='{self.train_code}']"):                       # 获取要查询车次的那一行
            train_id = self.base.get_value(f"tr[id^='price_'][datatran='{self.train_code}']", "id")         # price_***
            if train_id:                                                                                    # 如果查到了获取标签ID
                train_id = train_id.split("_")                                                              # ["price", "****"]
                self.train_id = train_id[1]
                self.elapsed_time = self.base.get_text(
                    f"#ticket_{self.train_id}>td:first-child div.ls>strong")                                # 获取历时信息
                if not self.elapsed_time or "-" in self.elapsed_time:
                    self.elapsed_time = "0:00"
                if self.base.touch_element(f"#ticket_{self.train_id}>td:last-child a"):                     # 检查预订按钮是否存在
                    return self.query_tickets()                                                             # 检查余票信息
                else:
                    self.real_message = f"车次[{self.train_code}]已无余票。"
                    self.return_message = self.real_message
            else:
                self.real_message = f"在12306未获取到车次[{self.train_code}]车票预订查询结果。"
                self.return_message = self.real_message
        else:
            self.real_message = f"在12306未获取到车次[{self.train_code}]车票预订查询结果。"
            self.return_message = self.real_message
        return False

    def query_tickets(self) -> bool:
        """
        查询车次检验余票
        :return: bool
        """
        tickets_set = set()                                                                 # 余票票种去重
        tickets_list = []                                                                   # 所有购票票种
        tickets_type = self.seat_type.split("@")                                            # 票类型
        for i in self.passengers:                                                           # 循环出购买的票种
            tickets_list.append(i[0])
            tickets_set.add(i[0])
        for i in tickets_set:                                                               # 检查每种坐席需要购买多少张
            for t in tickets_type:
                ticket = t.split("#")                                                       # 票种拆分  ['P', 'tz_num', '特等座']
                if i == ticket[0]:
                    ticket_id = "#" + ticket[1].strip("num").upper() + self.train_id        # 票种标签拼接   #TZ_num
                    value_text = self.base.get_text(ticket_id)                              # 获取标签内容
                    if "有" in value_text:
                        continue
                    elif "无" in value_text:
                        self.real_message = f"座席[{ticket[2]}]已无余票。"
                        self.return_message = self.real_message
                        return False
                    elif "-" in value_text:
                        self.real_message = "此车没有此坐席"
                        self.return_message = "座席类型不匹配"
                        return False
                    elif value_text.isdigit():                                              # 如果是数字
                        count = tickets_list.count(i)
                        if count > int(value_text):                                         # 比对数字
                            self.real_message = "没有足够的票!"
                            self.return_message = self.real_message
                            return False
                    else:
                        self.real_message = "不可识别的坐席类型"
                        self.return_message = "座席类型不匹配"
                        return False
        return True
    
    def login_switch(self) -> bool:
        """
        登录主要切换流程
        :return: bool
        """
        if self.cookie_way:  # 如果cookie登录
            if self.login_cookie():
                return True
            else:
                if "网络忙" in self.real_message:  # 如果cookie登录失败
                    return False
                else:
                    if self.login_way == 0:  # 如果新版登录
                        return self.login_old()
                    elif self.login_way == 1:
                        return self.login_new()
                    elif self.login_way == 2:
                        if self.base.set_url("https://kyfw.12306.cn/otn/resources/login.html"):
                            if self.base.wait_element("li.login-hd-account", self.page_search):
                                return self.login_captcha()
                    elif self.login_way == 3:
                        if self.base.set_url("https://kyfw.12306.cn/otn/resources/login.html"):
                            if self.base.wait_element("li.login-hd-code", self.page_search):
                                return self.login_scan()
        else:
            if self.login_way == 0:  # 如果新版登录
                return self.login_old()
            elif self.login_way == 1:
                return self.login_new()
            elif self.login_way == 2:
                if self.base.set_url("https://kyfw.12306.cn/otn/resources/login.html"):
                    if self.base.wait_element("li.login-hd-account", self.page_search):
                        return self.login_captcha()
            elif self.login_way == 3:
                if self.base.set_url("https://kyfw.12306.cn/otn/resources/login.html"):
                    if self.base.touch_element("li.login-hd-code", self.page_search):
                        return self.login_scan()
        if self.base.check_error():
            self.real_message = "获取到错误的页面，网络忙"
            self.return_message = "系统繁忙，请稍后重试"
            self.base.set_close()
            self.base.set_switch(self.main_window)
            return False
        self.real_message = "页面打开失败或操作失败"
        self.return_message = "系统繁忙，请稍后重试"
        self.base.set_close()
        self.base.set_switch(self.main_window)
        return False
    
    def login_cookie(self) -> bool:
        """
        缓存登录主要流程
        :return: bool
        """
        if self.base.set_url("https://kyfw.12306.cn/otn/resources/login.html"):             # 代开登录页
            self.base.set_cookie(self.cookie)                                               # 设置cookie
            if self.base.set_url("https://kyfw.12306.cn/otn/view/index.html"):              # 刷新客户页
                if self.base.wait_element("strong.welcome-name", self.next_search):
                    if self.base.wait_element("div.mask"):                                  # 消除蒙版
                        self.base.set_style("class", "mask", "none")
                    return True
        self.base.delete_cookies()                                                          # 如果失败先删除旧cookie
        if self.base.check_error():
            self.real_message = "获取到错误的页面，网络忙"
            self.return_message = "系统繁忙，请稍后重试"
            self.base.set_close()
            self.base.set_switch(self.main_window)
            return False
        self.real_message = "页面打开失败或操作失败"
        self.return_message = "系统繁忙，请稍后重试"
        return False
    
    def login_old(self) -> bool:
        """
        老版登录是否成功
        :return: bool
        """
        if self.base.set_url("https://kyfw.12306.cn/otn/login/init"):                           # 打开老版登录页面
            if self.base.touch_element("#loginSub", self.page_search):                                            # 登录按钮是否可按
                if not self.base.wait_element("img.touclick-image", self.page_search):          # 如果不存在图片，强行登录
                    self.base.set_text("#username", self.login_name)
                    self.base.set_text("#password", self.login_pwd)
                    self.base.set_click("#loginSub")
                    if self.base.hide_element("#loginSub", self.local_search):
                        if self.base.wait_element("strong.welcome-name", self.next_search):
                            if self.base.wait_element("div.mask"):
                                self.base.set_style("class", "mask", "none")
                            return True
                else:                                                                           # 如果存在图片打码登录
                    src = self.base.get_value("img.touclick-image", "src")
                    if src:
                        self.assistant_window = self.base.get_window()                          # 保存辅助页面，打开新的页面
                        if self.assistant_window:
                            self.base.set_script("window.open('');")
                            self.base.set_window(self.main_window, self.assistant_window)       # 切换新页面，保存图骗
                            if self.base.set_url(src):
                                if self.base.wait_element("img", self.page_search):
                                    self.base.crop_image("img", "img/test.png")
                                    image_flow = self.base.transform_captcha(r"img/test.png")
                                    code_list = self.base.get_captcha(image_flow, self.interval)           # 获取打码坐标
                                    self.base.set_close()  # 关闭打码页面
                                    self.base.set_switch(self.assistant_window)
                                    if code_list:
                                        self.base.set_text("#username", self.login_name)
                                        self.base.set_text("#password", self.login_pwd)
                                        self.base.click_image(code_list, "img.touclick-image", y_increment=30)  # 点击打码图片
                                        self.base.set_click("#loginSub")
                                        if self.base.hide_element("#loginSub", self.local_search):
                                            if self.base.wait_element("strong.welcome-name", self.next_search):
                                                if self.base.wait_element("div.mask"):
                                                    self.base.set_style("class", "mask", "none")
                                                return True
        if self.base.check_error():
            self.real_message = "获取到错误的页面，网络忙"
            self.return_message = "系统繁忙，请稍后重试"
            self.base.set_close()
            self.base.set_switch(self.main_window)
            return False
        self.real_message = "页面打开失败或操作失败"
        self.return_message = "系统繁忙，请稍后重试"
        self.base.set_close()
        self.base.set_switch(self.main_window)
        return False
        
    def login_new(self) -> bool:
        """
        新版登录主要流程
        :return:
        """
        if self.base.set_url("https://kyfw.12306.cn/otn/resources/login.html"):                             # 打开新版登录页面
            if self.base.show_elements("ul.login-hd>li", self.page_search):                                 # 查询按钮群
                login_class = self.base.find_elements("ul.login-hd>li", "class")
                if login_class:
                    for i in login_class:
                        if "login-hd-account" in i:                                         # 打码登录
                            return self.login_captcha()
                    for i in login_class:
                        if "login-hd-code" in i:  # 扫码登录
                            return self.login_scan()
            self.logger.info(f"没有找到登录标签群(*>﹏<*)【强行登录】")
            if self.base.touch_element("#J-login"):                                                         # 强行登录
                self.base.set_text("#J-userName", self.login_name)
                self.base.set_text("#J-password", self.login_pwd)
                self.base.set_script("document.getElementById('J-login').click();")
                if self.base.hide_element("#J-login", self.local_search):
                    if self.base.wait_element("strong.welcome-name", self.next_search):
                        if self.base.wait_element("div.mask"):
                            self.base.set_style("class", "mask", "none")
                        return True
        if self.base.check_error():
            self.real_message = "获取到错误的页面，网络忙"
            self.return_message = "系统繁忙，请稍后重试"
            self.base.set_close()
            self.base.set_switch(self.main_window)
            return False
        self.real_message = "页面打开失败或操作失败"
        self.return_message = "系统繁忙，请稍后重试"
        self.base.set_close()
        self.base.set_switch(self.main_window)
        return False
        
    def login_scan(self) -> bool:
        """
        扫码登录验证流程
        :return: bool
        """
        self.base.set_click("li.login-hd-code")
        if self.base.wait_element("#J-qrImg", self.local_search):
            src = self.base.get_value("#J-qrImg", "src")  # 获取图片地址
            if src:
                self.assistant_window = self.base.get_window()
                if self.assistant_window:
                    self.base.set_script("window.open('');")
                    self.base.set_window(self.main_window, self.assistant_window)
                if self.base.set_url(src):
                    if self.base.wait_element("img", self.page_search):
                        self.base.crop_image("img", "img/test.png")
                        image_flow = self.base.transform_scan("img/test.png")
                        self.base.set_close()
                        self.base.set_switch(self.assistant_window)
                        if self.base.get_scan(image_flow, self.login_name, self.login_pwd):  # 获取打码坐标
                            if self.base.hide_element("li.login-hd-code", self.local_search):
                                if self.base.wait_element("strong.welcome-name", self.next_search):
                                    if self.base.wait_element("div.mask"):
                                        self.base.set_style("class", "mask", "none")  # 消除蒙版
                                    return True
        if self.base.check_error():
            self.real_message = "获取到错误的页面，网络忙"
            self.return_message = "系统繁忙，请稍后重试"
            self.base.set_close()
            self.base.set_switch(self.main_window)
            return False
        self.real_message = "页面打开失败或操作失败"
        self.return_message = "系统繁忙，请稍后重试"
        self.base.set_close()
        self.base.set_switch(self.main_window)
        return False

    def login_captcha(self) -> bool:
        """
        打码登录验证流程
        :return: bool
        """
        self.base.set_click("li.login-hd-account")
        if self.base.wait_element("#J-loginImg", self.local_search):
            src = self.base.get_value("#J-loginImg", "src")  # 获取图片地址
            if src:
                self.assistant_window = self.base.get_window()
                if self.assistant_window:
                    self.base.set_script("window.open('');")
                    self.base.set_window(self.main_window, self.assistant_window)
                if self.base.set_url(src):
                    if self.base.wait_element("img", self.page_search):
                        self.base.crop_image("img", "img/test.png")
                        image_flow = self.base.transform_captcha(r"img/test.png")
                        code_list = self.base.get_captcha(image_flow, self.interval)  # 获取打码坐标
                        self.base.set_close()
                        self.base.set_switch(self.assistant_window)
                        if code_list:
                            self.base.click_image(code_list, "img#J-loginImg.imgCode", y_increment=30)  # 点击打码图片
                            self.base.set_text("#J-userName", self.login_name)
                            self.base.set_text("#J-password", self.login_pwd)  # 输入文本
                            self.base.set_script("document.getElementById('J-login').click();")
                            if self.base.hide_element("#J-login", self.local_search):
                                if self.base.wait_element("strong.welcome-name", self.next_search):
                                    if self.base.wait_element("div.mask"):
                                        self.base.set_style("class", "mask", "none")
                                    return True
        if self.base.check_error():
            self.real_message = "获取到错误的页面，网络忙"
            self.return_message = "系统繁忙，请稍后重试"
            self.base.set_close()
            self.base.set_switch(self.main_window)
            return False
        self.real_message = "页面打开失败或操作失败"
        self.return_message = "系统繁忙，请稍后重试"
        self.base.set_close()
        self.base.set_switch(self.main_window)
        return False

    def check_persons(self) -> bool:
        """
        核验流程核验身份
        :return: bool
        """
        if self.base.set_url("https://kyfw.12306.cn/otn/view/passengers.html"):  # 打开乘客页面
            if self.base.wait_element("table.order-item-table>tbody>tr", self.page_search):
                if self.base.wait_element("div.mask"):
                    self.base.set_style("class", "mask", "none")  # 消除蒙版
                cc = self.base.count_elements("table.order-item-table>tbody>tr")  # 统计人数
                if cc:
                    self.add_adults = copy.deepcopy(self.passengers)  # 复制信息
                    if not self.base.wait_element("div.page-all>strong"):
                        self.passenger_count += cc  # 汇总人数至站位数
                        # # # 遍历乘客信息
                        persons = []
                        for i in range(1, cc + 1):
                            name = self.base.get_text(f"table.order-item-table>tbody>tr:nth-child({i})>td:nth-child(2)")
                            id_type = self.base.get_text(f"table.order-item-table>tbody>tr:nth-child({i})>td:nth-child(3)")
                            pass_id = self.base.get_text(f"table.order-item-table>tbody>tr:nth-child({i})>td:nth-child(4)")
                            name_type = self.base.get_text(f"table.order-item-table>tbody>tr:nth-child({i})>td:nth-child(6)")
                            status = self.base.get_text(f"table.order-item-table>tbody>tr:nth-child({i})>td:nth-child(7)")
                            single = {
                                "postalcode": "", "passenger_id_type_code": "", "passenger_id_no": pass_id,
                                "sex_name": "", "phone_no": "", "gat_valid_date_end": "", "passenger_name": name, "passenger_id_type_name": id_type,
                                "mobile_no": "", "gat_born_date": "", "passenger_type_name": name_type, "born_date": "", "index_id": f"{i - 1}",
                                "sex_code": "", "code": "", "passenger_type": "", "country_code": "", "first_letter": "", "passenger_flag": "",
                                "email": "", "address": "", "gat_version": "", "total_times": "", "gat_valid_date_start": ""
                            }
                            persons.append(single)
                            for j in self.add_adults:
                                if j[2] == "2":
                                    self.add_adults.remove(j)
                                else:
                                    adult_name = j[3].upper()
                                    adult_id = j[5].upper()
                                    if adult_name == name and adult_id == pass_id:
                                        if "已通过" in status:
                                            self.add_adults.remove(j)
                                        else:
                                            self.real_message = f"{adult_name}@{adult_id}@待核验"
                                            self.return_message = self.real_message
                                            self.base.set_close()
                                            self.base.set_switch(self.main_window)
                                            return False
                                    elif adult_name != name and adult_id == pass_id:
                                        if "已通过" in status:
                                            self.add_adults.remove(j)
                                            for k in self.passengers:
                                                if k[3] == adult_name and k[5] == adult_id:
                                                    m = k
                                                    self.passengers.remove(k)
                                                    m[3] = name
                                                    self.passengers.append(m)
                        self.passengers_all = persons
                    else:
                        persons = []
                        pages = self.base.get_text("div.page-all>strong")  # 获取页数
                        for p in range(1, int(pages) + 1):
                            if self.base.wait_element("div.mask"):
                                self.base.set_style("class", "mask", "none")  # 消除蒙版
                            self.base.set_style("class", "js-gotop", "none")
                            self.base.set_click(f"ul.page-num>li:nth-child({p})>a")  # 点击页面
                            time.sleep(1)  # 休息一秒，否则刷不出
                            counts = self.base.count_elements("table.order-item-table>tbody>tr")  # 统计人数
                            if counts:
                                self.passenger_count += counts  # 汇总人数至站位数
                                # # # 遍历乘客信息
                                for i in range(1, counts + 1):
                                    name = self.base.get_text(f"table.order-item-table>tbody>tr:nth-child({i})>td:nth-child(2)")
                                    id_type = self.base.get_text(f"table.order-item-table>tbody>tr:nth-child({i})>td:nth-child(3)")
                                    pass_id = self.base.get_text(f"table.order-item-table>tbody>tr:nth-child({i})>td:nth-child(4)")
                                    name_type = self.base.get_text(f"table.order-item-table>tbody>tr:nth-child({i})>td:nth-child(6)")
                                    status = self.base.get_text(f"table.order-item-table>tbody>tr:nth-child({i})>td:nth-child(7)")
                                    single = {
                                        "postalcode": "", "passenger_id_type_code": "", "passenger_id_no": pass_id,
                                        "sex_name": "", "phone_no": "", "gat_valid_date_end": "", "passenger_name": name,
                                        "passenger_id_type_name": id_type,
                                        "mobile_no": "", "gat_born_date": "", "passenger_type_name": name_type, "born_date": "",
                                        "index_id": f"{i - 1}",
                                        "sex_code": "", "code": "", "passenger_type": "", "country_code": "", "first_letter": "",
                                        "passenger_flag": "",
                                        "email": "", "address": "", "gat_version": "", "total_times": "", "gat_valid_date_start": ""
                                    }
                                    persons.append(single)
                                    for j in self.add_adults:
                                        if j[2] == "2":
                                            self.add_adults.remove(j)
                                        else:
                                            adult_name = j[3].upper()
                                            adult_id = j[5].upper()
                                            if adult_name == name and adult_id == pass_id:
                                                if "已通过" in status:
                                                    self.add_adults.remove(j)
                                                else:
                                                    self.real_message = f"{adult_name}@{adult_id}@待核验"
                                                    self.return_message = self.real_message
                                                    self.base.set_close()
                                                    self.base.set_switch(self.main_window)
                                                    return False
                                            elif adult_name != name and adult_id == pass_id:
                                                if "已通过" in status:
                                                    self.add_adults.remove(j)
                                                    for k in self.passengers:
                                                        if k[3] == adult_name and k[5] == adult_id:
                                                            m = k
                                                            self.passengers.remove(k)
                                                            m[3] = name
                                                            self.passengers.append(m)
                        self.passengers_all = persons
                    for i in self.passengers_all:
                        i["recordCount"] = f"{self.passenger_count}"
                    if len(self.add_adults) > 0:
                        self.logger.info(f"添加常旅人数(^。^)y-~~【{self.add_adults}】")
                        if self.passenger_count == 15:
                            self.real_message = "已满|空位不足"
                            self.return_message = self.real_message
                            self.base.set_close()
                            self.base.set_switch(self.main_window)
                            return False
                        if len(self.add_adults) > 15 - self.passenger_count:
                            self.real_message = "已满|乘客数超过空位数"
                            self.return_message = self.real_message
                            self.base.set_close()
                            self.base.set_switch(self.main_window)
                            return False
                        else:
                            if not self.add_persons(self.add_adults):
                                return False
                    return True
        if self.base.check_error():
            self.real_message = "获取到错误的页面，网络忙"
            self.return_message = "系统繁忙，请稍后重试"
            self.base.set_close()
            self.base.set_switch(self.main_window)
            return False
        self.real_message = "页面打开失败或操作失败"
        self.return_message = "系统繁忙，请稍后重试"
        self.base.set_close()
        self.base.set_switch(self.main_window)
        return False

    def verify_persons(self) -> bool:
        """
        核验流程核验身份
        :return: bool
        """
        if self.base.set_url("https://kyfw.12306.cn/otn/view/passengers.html"):  # 打开乘客页面
            if self.base.wait_element("table.order-item-table>tbody>tr", self.page_search):
                if self.base.wait_element("div.mask"):
                    self.base.set_style("class", "mask", "none")  # 消除蒙版
                cc = self.base.count_elements("table.order-item-table>tbody>tr")  # 统计人数
                if cc:
                    if not self.base.wait_element("div.page-all>strong"):
                        # # # 遍历乘客信息
                        for i in range(1, cc + 1):
                            name = self.base.get_text(f"table.order-item-table>tbody>tr:nth-child({i})>td:nth-child(2)")
                            pass_id = self.base.get_text(f"table.order-item-table>tbody>tr:nth-child({i})>td:nth-child(4)")
                            status = self.base.get_text(f"table.order-item-table>tbody>tr:nth-child({i})>td:nth-child(7)")
                            for j in self.add_adults:
                                adult_name = j[3].upper()
                                adult_id = j[5].upper()
                                if adult_name == name and adult_id == pass_id:
                                    if "已通过" not in status:
                                        self.real_message = f"{adult_name}@{adult_id}@待核验"
                                        self.return_message = self.real_message
                                        return False
                        return True
                    else:
                        pages = self.base.get_text("div.page-all>strong")  # 获取页数
                        for p in range(1, int(pages) + 1):
                            if self.base.wait_element("div.mask"):
                                self.base.set_style("class", "mask", "none")  # 消除蒙版
                            self.base.set_style("class", "js-gotop", "none")
                            self.base.set_click(f"ul.page-num>li:nth-child({p})>a")  # 点击页面
                            time.sleep(1)  # 休息一秒，否则刷不出
                            counts = self.base.count_elements("table.order-item-table>tbody>tr")  # 统计人数
                            # # # 遍历乘客信息
                            for i in range(1, counts + 1):
                                name = self.base.get_text(f"table.order-item-table>tbody>tr:nth-child({i})>td:nth-child(2)")
                                pass_id = self.base.get_text(f"table.order-item-table>tbody>tr:nth-child({i})>td:nth-child(4)")
                                status = self.base.get_text(f"table.order-item-table>tbody>tr:nth-child({i})>td:nth-child(7)")
                                for j in self.add_adults:
                                    adult_name = j[3].upper()
                                    adult_id = j[5].upper()
                                    if adult_name == name and adult_id == pass_id:
                                        if "已通过" not in status:
                                            self.real_message = f"{adult_name}@{adult_id}@待核验"
                                            self.return_message = self.real_message
                                            return False
                        return True
        if self.base.check_error():
            self.real_message = "获取到错误的页面，网络忙"
            self.return_message = "系统繁忙，请稍后重试"
            return False
        self.real_message = "页面打开失败或操作失败"
        self.return_message = "系统繁忙，请稍后重试"
        return False

    def add_persons(self, add_persons=None) -> bool:
        """
        核验流程添加身份
        :return: bool
        """
        for i in add_persons:
            if self.base.set_url("https://kyfw.12306.cn/otn/view/passenger_edit.html?type=add"):
                if self.base.wait_element("#save_btn", self.page_search):
                    self.base.set_script(f"document.getElementById('name').value='{i[3]}';")
                    self.base.set_script(f"document.getElementById('cardCode').value='{i[5]}';")
                    sex = int(i[5][-2:-1])
                    if sex % 2 == 0:
                        self.base.set_click("#sex_code_div>label:last-child")
                    else:
                        self.base.set_click("#sex_code_div>label:first-child")
                    if self.base.wait_element("h2.msg-tit"):
                        self.base.set_click("div.modal-ft>a:last-child")
                    self.base.set_click("#save_btn")
                    # # # 判断是否弹出待核验弹出框
                    if self.base.wait_element("h2.msg-tit", self.local_search):
                        self.real_message = self.base.get_text("h2.msg-tit")
                        self.base.set_click("div.modal-ft>a:last-child")
                        if "成功" in self.real_message:
                            self.consumption_space += 1
                            continue
                        else:
                            self.return_message = f"{i[3]}@{i[5]}@证件号码输入有误!"
                            self.base.set_close()
                            self.base.set_switch(self.main_window)
                            return False
                    if self.base.wait_element("#cardCode-error"):
                        self.real_message = self.base.get_text("#cardCode-error")
                        self.return_message = f"{i[3]}@{i[5]}@证件号码输入有误!"
                        self.base.set_close()
                        self.base.set_switch(self.main_window)
                        return False
            if self.base.check_error():
                self.real_message = "获取到错误的页面，网络忙"
                self.return_message = "系统繁忙，请稍后重试"
                self.base.set_close()
                self.base.set_switch(self.main_window)
                return False
            self.real_message = "页面打开失败或操作失败"
            self.return_message = "系统繁忙，请稍后重试"
            self.base.set_close()
            self.base.set_switch(self.main_window)
            return False
        return True
    
    def query_pass(self) -> bool:
        """
        检查预订是否继续
        :return: bool
        """
        self.base.set_click(f"#ticket_{self.train_id}>td:last-child a")  # 点击预定按钮
        if self.base.hide_element(f"#ticket_{self.train_id}>td:last-child a", self.local_search):
            if self.base.wait_element("input[id^='normalPassenger_']", self.next_search):
                return True
        else:
            if self.base.wait_element("#qd_closeDefaultWarningWindowDialog_id.btn92s"):  # 提示框是否弹出
                self.real_message = self.base.get_text("#content_defaultwarningAlert_hearder")
                self.base.set_click("#qd_closeDefaultWarningWindowDialog_id")
                if "未处理" in self.real_message:
                    return True
                else:
                    if self.base.hide_element(f"#ticket_{self.train_id}>td:last-child a", self.local_search):
                        if self.base.wait_element("input[id^='normalPassenger_']", self.next_search):
                            return True
            else:
                if self.base.wait_element("input[id^='normalPassenger_']", self.next_search):
                    return True
        if self.base.check_error():
            self.real_message = "获取到错误的页面，网络忙"
            self.return_message = "系统繁忙，请稍后重试"
            return False
        self.real_message = "页面打开失败或操作失败"
        self.return_message = "系统繁忙，请稍后重试"
        return False
    
    def submit_info(self) -> bool:
        """
        检查订单信息流程 @@包含检查乘车人流程@@ @@包含检查坐席流程@@
        :return: bool
        """
        self.submit_tickets()
        self.submit_persons()
        page_source = self.base.get_page()
        # 获取是否可以在线退款
        refund = self.base.parse_regex(r"isLimitTran=.*var CHANGETSFLAG", page_source)
        if refund:
            refund_value = self.base.parse_regex(r"['].*[']", refund)
            if refund_value:
                if refund_value[0] == "Y":
                    self.refund_online = 1
        # # # 一次提交按钮
        time.sleep(1)
        self.base.set_click("#submitOrder_id")
        if self.base.wait_element("#qr_submit_id.btn92s", self.local_search):
            # # # 获取在线选座
            self.real_message = self.base.get_text("#notice_1_id")
            if '系统将自动为您分配席位' in self.real_message:
                self.choose_seats = "Y"
            time.sleep(1)
            self.base.set_script("document.getElementById('qr_submit_id').click();")
            return True
        if self.base.wait_element("#orderResultInfo_id"):
            self.real_message = self.base.get_text("#orderResultInfo_id")
            self.real_message = self.return_message
            return False
        if self.base.check_error():
            self.real_message = "获取到错误的页面，网络忙"
            self.return_message = "系统繁忙，请稍后重试"
            return False
        self.real_message = "页面打开失败或操作失败"
        self.return_message = "系统繁忙，请稍后重试"
        return False
    
    def submit_tickets(self):
        """
        检查坐席是否符合
        :return: bool
        """
        tickets = {}
        counts = self.base.count_elements("#ticket_status_id")
        for i in range(1, counts + 1):
            seats = self.base.get_text(f"#ticket_status_id:nth-child({i})")
            if seats:
                seat = self.base.parse_sub("\r|\n|\s|\t", "", seats)
                seat_name = self.base.parse_regex(r"[^（￥.*]+", seat)
                seat_value = self.base.parse_regex(r"\d+.\d+", seat)
                seat_left = self.base.parse_regex(r"）.*$", seat)
                if seat_name and seat_value and seat_left:
                    tickets[seat_name] = seat_value
                else:
                    self.logger.info(f"匹配坐席失败（╯＾╰）【{seats}】")
        self.seats_price = tickets
    
    def submit_persons(self):
        """
        @@检查乘客是否正确@@ @@包含添加乘客@@
        :return: bool
        """
        if self.base.wait_element("div.dhx_modal_cover"):
            self.base.set_style("class", "dhx_modal_cover", "none")  # 消除蒙版
        students = []
        others = []
        click_elements = []
        for i in self.passengers:
            if i[2] == "3":
                students.append(i)
            else:
                others.append(i)
        if others:
            self.base.set_click("#normalPassenger_0")
            for i in range(1, len(others)):
                self.base.set_click("#addchild_1")
            for i in range(1, len(others) + 1):
                seats_type = others[i - 1][0]
                seats_name = ""
                aa = self.seat_type.split("@")
                for t in aa:
                    ticket = t.split("#")  # 票种拆分  ['P', 'tz_num', '特等座']
                    if seats_type == ticket[0]:
                        seats_name = ticket[2]
                tickets_type = others[i - 1][2]
                tickets_name = ""
                if tickets_type == 1:
                    tickets_name = "成人票"
                elif tickets_type == 2:
                    tickets_name = "儿童票"
                elif tickets_type == 3:
                    tickets_name = "学生票"
                elif tickets_type == 4:
                    tickets_name = "残军票"
                self.base.set_script(f"document.getElementById('passenger_name_{i}').value='{others[i - 1][3]}';")
                self.base.set_script(f"document.getElementById('passenger_id_no_{i}').value='{others[i - 1][5]}';")
                self.base.set_script(f"document.getElementById('ticketType_{i}').options[0].value='{tickets_type}';")
                self.base.set_script(f"document.getElementById('ticketType_{i}').options[0].selected='selected';")
                self.base.set_script(f"document.getElementById('ticketType_{i}').options[0].innerText='{tickets_name}';")
                self.base.set_script(f"document.getElementById('seatType_{i}').options[0].value='{seats_type}';")
                self.base.set_script(f"document.getElementById('seatType_{i}').options[0].innerText='{seats_name}';")
        if students:
            count = self.base.count_elements("label[for^='normalPassenger_']")
            for i in students:
                for j in range(count):
                    text = self.base.get_text(f"label[for^='normalPassenger_{count}']")
                    if i[3] in text and "学生" in text:
                        click_elements.append(f"label[for^='normalPassenger_{count}']")
            for i in click_elements:
                self.base.set_click(i)
                if self.base.wait_element("#dialog_xsertcj_ok", self.local_search):
                    self.base.set_click("#dialog_xsertcj_ok")
                    
    def submit_pass(self, count: int = 0, max_num: int = 5) -> bool:
        """
        二次提交等待结果
        :param count: 重试次数
        :param max_num: 重试最大次数
        :return:
        """
        if count >= max_num:  # 累计最大数
            if self.base.check_error():
                self.real_message = "获取到错误的页面，网络忙"
                self.return_message = "系统繁忙，请稍后重试"
                return False
            self.real_message = "页面打开失败或操作失败"
            self.return_message = "系统繁忙，请稍后重试"
            return False
        else:
            if self.base.wait_element("#payButton", self.local_search):
                if self.submit_done():
                    return True
                else:
                    return self.submit_pass(count + 1, max_num)
            else:
                if self.base.wait_element("#orderResultInfo_id"):
                    self.real_message = self.base.get_text("#orderResultInfo_id")
                    if self.real_message:
                        if "正在处理" in self.real_message:
                            return self.submit_pass(count + 1, max_num)
                        elif "下单成功" in self.real_message:
                            return self.submit_pass(count + 1, max_num)
                        elif "核验" in self.real_message:
                            return self.verify_persons()
                        elif "未完成" in self.real_message:
                            return True
                        elif "排队" in self.real_message:
                            return True
                        elif "未支付" in self.real_message:
                            return True
                        else:
                            self.return_message = self.real_message
                            return False
                    else:
                        return self.submit_pass(count + 1, max_num)
                else:
                    if self.base.wait_element("#content_defaultwarningAlert_hearder"):
                        self.real_message = self.base.get_text("#content_defaultwarningAlert_hearder")
                        self.base.set_click("#qd_closeDefaultWarningWindowDialog_id")
                        if "自动" in self.real_message:
                            return self.submit_pass(count + 1, max_num)
                        elif "卧代" in self.real_message:
                            return self.submit_pass(count + 1, max_num)
                        else:
                            self.return_message = self.real_message
                            return False
                    else:
                        if self.base.wait_element("#not_complete"):
                            if self.base.wait_element("div.dhx_modal_cover"):
                                self.base.set_style("class", "dhx_modal_cover", "none")  # 消除蒙版
                            if self.base.wait_element("#countdown0", self.page_search):
                                time.sleep(1)
                                self.base.set_script("document.getElementById('countdown0').click();")
                                if self.base.wait_element("#payButton", self.local_search):
                                    if self.submit_done():
                                        return True
                        return self.submit_pass(count + 1, max_num)
    
    def submit_done(self) -> bool:
        """
        提取占座数据结果
        :return: bool
        """
        page_source = self.base.get_page()
        if page_source:
            # # # 匹配页面具体占座信息
            get_page = self.base.parse_regex(r'parOrderDTOJson.+?;', page_source)
            if get_page:
                get_string = self.base.parse_regex(r"'.+?'", get_page)
                if get_string:
                    data_string = get_string.replace("'", "")
                    data_replace = data_string.replace('\\"', '"')
                    data_json = self.base.parse_json(data_replace)
                    if data_json:
                        self.order_data = self.base.get_result(data_json, self.pay_method)
                        if self.order_data:
                            self.sequence_no = data_json['orders'][0]["sequence_no"]
                            self.real_message = f"提交订单成功，12306订单号为{self.sequence_no}。"
                            self.return_message = self.real_message
                            self.save_cookies = self.base.return_cookies()
                            return True
        return False
    
    def verify_unfinished(self):
        if self.base.set_url("https://kyfw.12306.cn/otn/view/train_order.html"):  # 打开登录页
            if self.base.wait_element("#not_complete", self.page_search):
                if self.base.wait_element("div.mask"):
                    self.base.set_style("class", "mask", "none")  # 消除蒙版
                if self.base.wait_element("#countdown0", self.page_search):
                    time.sleep(1)
                    self.base.set_script("document.getElementById('countdown0').click()")
                    if self.base.wait_element("#payButton", self.next_search):
                        if self.base.wait_element("#content_defaultwarningAlert_hearder"):
                            self.base.set_script("document.getElementById('qd_closeDefaultWarningWindowDialog_id').click();")
                        if self.submit_done():
                            return True
                else:
                    if self.base.wait_element("#paiduizhong", self.page_search):
                        self.base.set_script("document.getElementById('cencle_paidui_btn').click()")
                        self.real_message = "订单排队"
                        self.return_message = "订单已经提交，最新预估等待时间1分，请耐心等待。"
                        return False
        if self.base.check_error():
            self.real_message = "获取到错误的页面，网络忙"
            self.return_message = "系统繁忙，请稍后重试"
            return False
        self.real_message = "页面打开失败或操作失败"
        self.return_message = "系统繁忙，请稍后重试"
        return False
    
    def return_data(self, status) -> str:
        """
        回调接口最终格式
        :param status: true成功，false失败
        :return: str
        """
        # # # 共有参数
        result_data = {
            "consumptionVacancySum": self.consumption_space, "refund_online": self.refund_online,
            "lishi": self.elapsed_time, "accountPassengerCount": self.passenger_count,
            "price12306": self.seats_price, "ChooseSeatsTypes": self.choose_seats,
            "msg": self.return_message, "ChooseBerthTypres": "N", "success": status,
            "cookie": self.save_cookies, "12306": self.order_data,
            "normal_passengers": self.passengers_all, "sequence_no": self.sequence_no
        }
        json_return = self.base.parse_dump(result_data)
        json_return = json_return.replace(r'\\\"', r'\"')
        return json_return

    def get_config(self) -> bool:
        """
        获取配置是否成功
        :return: bool
        """
        try:
            config_data = self.redis_queue.hgetall("config_name")  # 获取配置
        except Exception as ex:
            self.logger.info(f"获取配置数据失败(*>﹏<*)【{ex}】")
            return False
        else:
            if config_data:
                self.interval = int(config_data.get("interval", 2))
                self.circulation = int(config_data.get("circulation", 4))
                self.page_search = int(config_data.get("page_search", 5))
                self.local_search = int(config_data.get("local_search", 5))
                self.next_search = int(config_data.get("next_search", 10))
                self.order_proxy = int(config_data.get("order_proxy", 1))
                self.login_way = int(config_data.get("login_way", 1))
                self.cookie_way = int(config_data.get("cookie_way", 1))
                self.time_out = int(config_data.get("time_out", 10))
                self.logger.info("获取配置数据成功(*^__^*)【OK】")
                return True
            else:
                self.logger.info("获取配置数据为空(*>﹏<*)【NO】")
                return False

    def get_proxy(self) -> bool:
        """
        获取代理是否成功
        :return: bool
        """
        try:
            self.proxy_addr = self.redis_queue.rpop("proxy_leisure")
        except Exception as ex:
            self.logger.info(f"代理队列获取失败(*>﹏<*)【{ex}】")
            return False
        else:
            if not self.proxy_addr:
                self.logger.info("代理队列获取为空(*>﹏<*)【NO】")
                return False
            else:
                try:
                    proxy_data = self.redis_machine.hgetall(self.proxy_addr)
                except Exception as ex:
                    self.logger.info(f"代理获取数据失败(*>﹏<*)【{ex}】")
                    return False
                else:
                    if proxy_data:
                        self.proxy_server = proxy_data.get('proxy_server', '')
                        self.proxy_auth = proxy_data.get('proxy_auth', 'yunku:123')
                        self.logger.info(f"代理获取数据成功(*^__^*)【{self.proxy_server}】【{self.proxy_auth}】")
                        return True
                    else:
                        self.logger.info(f"代理获取数据为空(*>﹏<*)【{self.proxy_addr}】")
                        return False

    def return_proxy(self) -> bool:
        """
        归还代理是否成功
        :return: bool
        """
        try:
            self.redis_queue.lpush(self.proxy_status, self.proxy_addr)
        except Exception as ex:
            self.logger.info(f"归还代理数据失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"归还代理数据成功(*^__^*)【{self.proxy_status}】【{self.proxy_addr}】")
            return True

    def return_result(self) -> bool:
        """
        归还结果是否成功
        :return:
        """
        try:
            send_data = {"ip": self.machine_addr, "data": self.return_data(self.return_status),
                         "proxy": self.proxy_addr, "circulation": self.circulation,
                         "real_message": self.real_message, "return_message": self.return_message}
            self.redis_result.hmset(self.key_label, send_data)
            self.redis_queue.lpush("machines", self.machine_addr)
        except Exception as ex:
            self.logger.info(f"归还结果失败(*>﹏<*)【{ex}】")
            return False
        else:
            self.logger.info(f"归还结果成功(*^__^*)【{self.key_label}】")
            return True
