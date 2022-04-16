# # 无头浏览器下单
# import requests
# from urllib import request as requ
# from urllib import parse
# import time
#
#
# def CreateOrderMethod(param):
#
#     #
#     result = requests.post(url="http://headless.hangtian123.com/orders/", data=param)
#     print(result.text)
#     #
#     # result = requests.post(url="http://127.0.0.1/orders/", data=param)
#     # print(result.text)
#
#
# if __name__ == '__main__':
#     # a = """\ufeff{"isAutoCreateOrder":false,"orderType":"","queryLink":"leftTicket/query","getPayUrlFlag":true,"seatTypeOf12306":"P#tz_num#特等座@M#zy_num#一等座@O#ze_num#二等座@F#dw_num#动卧@E#qt_num#特等软座@A#qt_num#高级动卧@9#swz_num#商务座@8#ze_num#二等软座@7#zy_num#一等软座@6#gr_num#高级软卧@4#rw_num#软卧@3#yw_num#硬卧@2#rz_num#软座@1#yz_num#硬座@0#wz_num#无座","CustomerAccount":false,"from_station_name":"北京","dontBindingPassengers":false,"goAliOcs":false,"to_station_name":"唐山","cookie":"JSESSIONID=0A01E841600665A24B1EED7CD340EB785F5DCE1921;+BIGipServerotn=1105723658.24610.0000; current_captcha_type=Z;+AccountVirtualCookie=1","passengers":{"oldPassengerStr":"丁桂贤,1,32102719571109361x,1_","prices":"242.0","choose_seats":"","zwcodes":"3","passengerTicketStr":"O,0,1,康继曾+ +,1,412824197612046814,15677543184,N"},"to_station":"TSP","train_date":"2019-02-28","from_station":"BJP","loginPwd":"22In06jA8","isBindingPassengers":true,"orderId":1354529123,"train_code":"G8919","payMethod":2,"loginName":"13084233827"}"""
#     # b = parse.quote_plus(a)
#     # c = b.encode('utf-8')
#     # print(c)
#
#
#     param = b'%EF%BB%BF%7B%22isAutoCreateOrder%22%3Afalse%2C%22orderType%22%3A%22%22%2C%22queryLink%22%3A%22leftTicket%2Fquery%22%2C%22getPayUrlFlag%22%3Atrue%2C%22seatTypeOf12306%22%3A%22P%23tz_num%23%E7%89%B9%E7%AD%89%E5%BA%A7%40M%23zy_num%23%E4%B8%80%E7%AD%89%E5%BA%A7%40O%23ze_num%23%E4%BA%8C%E7%AD%89%E5%BA%A7%40F%23dw_num%23%E5%8A%A8%E5%8D%A7%40E%23qt_num%23%E7%89%B9%E7%AD%89%E8%BD%AF%E5%BA%A7%40A%23qt_num%23%E9%AB%98%E7%BA%A7%E5%8A%A8%E5%8D%A7%409%23swz_num%23%E5%95%86%E5%8A%A1%E5%BA%A7%408%23ze_num%23%E4%BA%8C%E7%AD%89%E8%BD%AF%E5%BA%A7%407%23zy_num%23%E4%B8%80%E7%AD%89%E8%BD%AF%E5%BA%A7%406%23gr_num%23%E9%AB%98%E7%BA%A7%E8%BD%AF%E5%8D%A7%404%23rw_num%23%E8%BD%AF%E5%8D%A7%403%23yw_num%23%E7%A1%AC%E5%8D%A7%402%23rz_num%23%E8%BD%AF%E5%BA%A7%401%23yz_num%23%E7%A1%AC%E5%BA%A7%400%23wz_num%23%E6%97%A0%E5%BA%A7%22%2C%22CustomerAccount%22%3Afalse%2C%22from_station_name%22%3A%22%E5%8C%97%E4%BA%AC%22%2C%22dontBindingPassengers%22%3Afalse%2C%22goAliOcs%22%3Afalse%2C%22to_station_name%22%3A%22%E5%94%90%E5%B1%B1%22%2C%22cookie%22%3A%22JSESSIONID%3D0A01E841600665A24B1EED7CD340EB785F5DCE1921%3B%2BBIGipServerotn%3D1105723658.24610.0000%3B+current_captcha_type%3DZ%3B%2BAccountVirtualCookie%3D1%22%2C%22passengers%22%3A%7B%22oldPassengerStr%22%3A%22%E4%B8%81%E6%A1%82%E8%B4%A4%2C1%2C32102719571109361x%2C1_%22%2C%22prices%22%3A%22242.0%22%2C%22choose_seats%22%3A%22%22%2C%22zwcodes%22%3A%223%22%2C%22passengerTicketStr%22%3A%22O%2C0%2C1%2C%E5%BA%B7%E7%BB%A7%E6%9B%BE%2B+%2B%2C1%2C412824197612046814%2C15677543184%2CN%22%7D%2C%22to_station%22%3A%22TSP%22%2C%22train_date%22%3A%222019-02-28%22%2C%22from_station%22%3A%22BJP%22%2C%22loginPwd%22%3A%2222In06jA8%22%2C%22isBindingPassengers%22%3Atrue%2C%22orderId%22%3A1354529123%2C%22train_code%22%3A%22G8919%22%2C%22payMethod%22%3A2%2C%22loginName%22%3A%2213084233827%22%7D'
#     CreateOrderMethod(param)

import datetime

now = datetime.datetime.now()

if now.hour > 5 and now.minute > 23:
    if now.hour < 8:
        print(1)
