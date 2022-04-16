#! /usr/local/bin/python3
# -*- coding: utf-8 -*-
"""
    written by pyleo
"""
import sys
sys.path.append('..')  # 导入环境当前目录
from receive import config
from flask import Flask, request, jsonify
from urllib.parse import unquote_plus
import os
import pymongo
import redis
import logging
import time
import json
import re


app = Flask(__name__)  # app实例
app.config['JSON_AS_ASCII'] = False  # 字符
redis_queue = redis.StrictRedis(
    connection_pool=redis.ConnectionPool(
        host=config.QUEUE_HOST, port=config.QUEUE_PORT, password=config.QUEUE_PASS,
        decode_responses=True, socket_connect_timeout=config.REDIS_TIMEOUT, socket_timeout=config.REDIS_TIMEOUT))  # redis队列
redis_result = redis.StrictRedis(
    connection_pool=redis.ConnectionPool(
        host=config.RESULT_HOST, port=config.RESULT_PORT, password=config.RESULT_PASS,
        decode_responses=True, socket_connect_timeout=config.REDIS_TIMEOUT, socket_timeout=config.REDIS_TIMEOUT))  # redis结果
redis_machine = redis.StrictRedis(
    connection_pool=redis.ConnectionPool(
        host=config.MACHINE_HOST, port=config.MACHINE_PORT, password=config.MACHINE_PASS,
        decode_responses=True, socket_connect_timeout=config.REDIS_TIMEOUT, socket_timeout=config.REDIS_TIMEOUT))  # redis机器
mongo_client = pymongo.MongoClient("mongodb://172.16.188.42:27017/")

# # # 日志格式化
logger = logging.getLogger("flask")
logger.setLevel(level=logging.INFO)
formatter = logging.Formatter('【%(asctime)s】%(message)s')
handler = logging.FileHandler("flask.log")  # 日志存放地址
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)
app.logger.addHandler(handler)


def return_data(method: str = "") -> str:
    """
    失败返回数据
    :return: str
    """
    failure = {}
    if method == "order":
        failure = {
            "consumptionVacancySum": 0, "refund_online": 0, "lishi": "", "price12306": {},
            "accountPassengerCount": 0, "ChooseSeatsTypes": "", "success": "false",
            "msg": "下单失败", "ChooseBerthTypres": "N"
        }
    elif method == "pay":
        failure = {
            "result": "支付失败", "cookie": ""
        }
    elif method == "audit":
        failure = {
            "result": "审核失败", "cookie": ""
        }
    else:
        pass
    return jsonify(failure)


@app.route('/orders/', methods=['POST'])
def get_orders():
    """
    下单请求方法
    :return: str
    """
    start_time = time.time()    # 记录开始时间
    if not request.get_data():  # 检查是否有请求数据
        app.logger.info("接口接收数据为空(*>﹏<*)【order】")
        return return_data("order")
    else:
        try:
            request_string = request.get_data().decode('utf-8-sig')  # 数据解码, 数据解析
            first_unquote = unquote_plus(request_string, encoding='utf-8-sig')
            second_unquote = unquote_plus(first_unquote, encoding='utf-8-sig')
            re_data = re.sub("\r|\n|\t|\s", "", second_unquote)
            result_dict = json.loads(re_data, encoding='utf-8-sig')
            order_id = result_dict.get('orderId', '')  # 获取订单号
            if not order_id:  # 检查是否有订单号
                run_time = round(time.time() - start_time, 2)
                db = mongo_client['statistics']
                db['monitor'].insert_one({"status": "order", "key": "", "start_time": int(start_time), "run_time": run_time,
                                       "ip": "", "proxy": "", "real_msg": "接口数据没有单号", "return_msg": "下单失败"})
                app.logger.info(f"接口数据没有单号(*>﹏<*)【order】【{run_time}】")
                return return_data("order")
            order_key = f"order{order_id}"  # 拼接存储key
            result_data = redis_result.hgetall(order_key)  # 先查询结果库有没有
            if result_data:  # 如果有结果
                get_ip = result_data.get('ip', '')  # 取出机器地址
                get_data = result_data.get('data', '')  # 取出返回数据
                get_proxy = result_data.get('proxy', '')
                get_circulation = int(result_data.get('circulation', 0))  # 取出循环次数
                if not get_data:  # 如果没数据
                    run_time = round(time.time() - start_time, 2)
                    db = mongo_client['statistics']
                    db['monitor'].insert_one({"status": "order", "key": order_id, "start_time": int(start_time), "run_time": run_time,
                                           "ip": get_ip, "proxy": get_proxy, "real_msg": "再次查询数据为空", "return_msg": "下单失败"})
                    app.logger.info(f"再次查询数据为空(*>﹏<*)【order】【{run_time}】【{order_id}】【{get_ip}】")
                    return return_data("order")
                else:  # 如果有数据
                    if get_circulation:  # 如果循环
                        return get_data  # 直接返回数据
                    else:  # 如果不循环
                        redis_result.delete(order_key)  # 删除数据
            else:  # 如果没有结果
                pass
            machine = ""
            for i in range(3):  # 超时时间多少，间隔1秒去查询
                time.sleep(1)
                machine = redis_queue.rpop(config.MACHINE_QUEUE)
                if machine:
                    if os.system(f"ping -w2 -c1 {machine}"):
                        redis_queue.lpush("machine_broken", machine)
                        continue
                    else:
                        break
            if not machine:
                run_time = round(time.time() - start_time, 2)
                db = mongo_client['statistics']
                db['monitor'].insert_one({"status": "order", "key": order_id, "start_time": int(start_time), "run_time": run_time,
                                       "ip": "", "proxy": "", "real_msg": "获取不到下单机器", "return_msg": "下单失败"})
                app.logger.info(f"获取不到下单机器(*>﹏<*)【order】【{run_time}】【{order_id}】")
                return return_data("order")
            send_data = {"key_label": order_key, "key_data": result_dict}  # 拼接数据
            redis_machine.hmset(machine, send_data)  # 发送消息
            for x in range(config.MAX_NUM):  # 超时时间多少，间隔1秒去查询
                time.sleep(1)
                result_data = redis_result.hgetall(order_key)  # 查询数据库
                if result_data:  # 如果有结果
                    get_ip = result_data.get('ip', '')  # 取出机器地址
                    get_data = result_data.get('data', '')  # 取出返回数据
                    get_proxy = result_data.get('proxy', '')
                    get_real = result_data.get('real_message', '')
                    get_return = result_data.get('return_message', '')
                    if not get_data:  # 如果没数据
                        run_time = round(time.time() - start_time, 2)
                        db = mongo_client['statistics']
                        db['monitor'].insert_one({"status": "order", "key": order_id, "start_time": int(start_time), "run_time": run_time,
                                               "ip": get_ip, "proxy": get_proxy, "real_msg": "首次查询数据为空", "return_msg": "下单失败"})
                        app.logger.info(f"首次查询数据为空(*>﹏<*)【order】【{run_time}】【{order_id}】【{get_ip}】")
                        return return_data("order")
                    else:  # 如果有数据
                        run_time = round(time.time() - start_time, 2)
                        db = mongo_client['statistics']
                        db['monitor'].insert_one({"status": "order", "key": order_id, "start_time": int(start_time), "run_time": run_time,
                                               "ip": get_ip, "proxy": get_proxy, "real_msg": get_real, "return_msg": get_return})
                        app.logger.info(f"下单数据返回成功(*^__^*)【order】【{run_time}】【{order_id}】【{get_ip}】【{get_proxy}】【{get_real}】")
                        return get_data  # 直接返回数据
        except Exception as ex:
            app.logger.info(f"下单程序返回失败(*>﹏<*)【order】【{ex}】")
            return return_data("order")
        else:
            run_time = round(time.time() - start_time, 2)
            db = mongo_client['statistics']
            db['monitor'].insert_one({"status": "order", "key": order_id, "start_time": int(start_time), "run_time": run_time,
                                   "ip": "", "proxy": "", "real_msg": "下单程序返回超时", "return_msg": "下单失败"})
            app.logger.info(f"下单程序返回超时(⊙﹏⊙)【order】【{run_time}】【{order_id}】【{machine}】")
            return return_data("order")


@app.route('/payments/', methods=['POST'])
def get_pays():
    """
    支付链接请求方法
    :return: str
    """
    start_time = time.time()    # 记录开始时间
    if not request.get_data():  # 检查是否有请求数据
        app.logger.info("接口接收数据为空(*>﹏<*)【pay】")
        return return_data("pay")
    try:
        request_string = request.get_data().decode('utf-8-sig')  # 数据解码, 数据解析
        first_unquote = unquote_plus(request_string, encoding='utf-8-sig')
        second_unquote = unquote_plus(first_unquote, encoding='utf-8-sig')
        re_data = re.sub("\r|\n|\t|\s", "", second_unquote)
        decode_list = re_data.split('&')  # 解析数据
        decode_dict = {}
        for i in decode_list:
            i = i.split("=")
            decode_dict[i[0]] = i[1]
        pay_id = decode_dict.get('ticket_code', '')  # 获取12306订单号
        if not pay_id:  # 检查是否有订单号
            run_time = round(time.time() - start_time, 2)
            db = mongo_client['statistics']
            db['monitor'].insert_one({"status": "pay", "key": "", "start_time": int(start_time), "run_time": run_time,
                                   "ip": "", "proxy": "", "real_msg": "接口数据没有单号", "return_msg": "支付失败"})
            app.logger.info(f"接口数据没有单号(*>﹏<*)【pay】【{run_time}】")
            return return_data("pay")
        pay_key = f"pay{pay_id}"  # 拼接存储key
        result_data = redis_result.hgetall(pay_key)  # 先查询结果库有没有
        if result_data:  # 如果有结果
            get_ip = result_data.get('ip', '')  # 取出机器地址
            get_data = result_data.get('data', '')  # 取出返回数据
            get_proxy = result_data.get('proxy', '')
            get_circulation = int(result_data.get('circulation', 0))  # 取出循环次数
            if not get_data:  # 如果没数据
                run_time = round(time.time() - start_time, 2)
                db = mongo_client['statistics']
                db['monitor'].insert_one({"status": "pay", "key": pay_id, "start_time": int(start_time), "run_time": run_time,
                                       "ip": get_ip, "proxy": get_proxy, "real_msg": "再次查询数据为空", "return_msg": "下单失败"})
                app.logger.info(f"再次查询数据为空(*>﹏<*)【pay】【{run_time}】【{pay_id}】【{get_ip}】")
                return return_data("pay")
            else:  # 如果有数据
                if get_circulation:  # 如果循环
                    return get_data  # 直接返回数据
                else:  # 如果不循环
                    redis_result.delete(pay_key)  # 删除数据
        else:  # 如果没有结果
            pass
        machine = ""
        for i in range(config.MAX_NUM):  # 超时时间多少，间隔1秒去查询
            time.sleep(1)
            machine = redis_queue.rpop(config.MACHINE_QUEUE)
            if machine:
                if os.system(f"ping -w2 -c1 {machine}"):
                    redis_queue.lpush("machine_broken", machine)
                    continue
                else:
                    break
        if not machine:
            run_time = round(time.time() - start_time, 2)
            db = mongo_client['statistics']
            db['monitor'].insert_one({"status": "pay", "key": pay_id, "start_time": int(start_time), "run_time": run_time,
                                   "ip": "", "proxy": "", "real_msg": "获取不到支付机器", "return_msg": "支付失败"})
            app.logger.info(f"获取不到支付机器(*>﹏<*)【pay】【{run_time}】【{pay_id}】")
            return return_data("pay")
        send_data = {"key_label": pay_key, "key_data": decode_dict}  # 拼接数据
        redis_machine.hmset(machine, send_data)  # 发送消息
        for x in range(config.MAX_NUM):  # 超时时间多少，间隔1秒去查询
            time.sleep(1)
            result_data = redis_result.hgetall(pay_key)  # 查询数据库
            if result_data:  # 如果有结果
                get_ip = result_data.get('ip', '')  # 取出机器地址
                get_data = result_data.get('data', '')  # 取出返回数据
                get_proxy = result_data.get('proxy', '')
                get_real = result_data.get('real_message', '')
                get_return = result_data.get('return_message', '')
                if not get_data:  # 如果没数据
                    run_time = round(time.time() - start_time, 2)
                    db = mongo_client['statistics']
                    db['monitor'].insert_one({"status": "pay", "key": pay_id, "start_time": int(start_time), "run_time": run_time,
                                           "ip": get_ip, "proxy": get_proxy, "real_msg": "首次查询数据为空", "return_msg": "支付失败"})
                    app.logger.info(f"首次查询数据为空(*>﹏<*)【pay】【{run_time}】【{pay_id}】【{get_ip}】")
                    return return_data("pay")
                else:  # 如果有数据
                    run_time = round(time.time() - start_time, 2)
                    db = mongo_client['statistics']
                    db['monitor'].insert_one({"status": "pay", "key": pay_id, "start_time": int(start_time), "run_time": run_time,
                                           "ip": get_ip, "proxy": get_proxy, "real_msg": get_real, "return_msg": get_return})
                    app.logger.info(f"支付数据返回成功(*^__^*)【pay】【{run_time}】【{get_ip}】【{get_proxy}】【{get_real}】")
                    return get_data  # 直接返回数据
    except Exception as ex:
        app.logger.info(f"支付程序返回失败(*>﹏<*)【pay】【{ex}】")
        return return_data("pay")
    else:
        run_time = round(time.time() - start_time, 2)
        db = mongo_client['statistics']
        db['monitor'].insert_one({"status": "pay", "key": pay_id, "start_time": int(start_time), "run_time": run_time,
                               "ip": "", "proxy": "", "real_msg": "支付程序返回超时", "return_msg": "支付失败"})
        app.logger.info(f"支付程序返回超时(⊙﹏⊙)【pay】【{run_time}】【{pay_id}】【{machine}】")
        return return_data("pay")
    

@app.route('/audits/', methods=['POST'])
def get_audits():
    """
    审核请求方法
    :return: str
    """
    start_time = time.time()    # 记录开始时间
    if not request.get_data():  # 检查是否有请求数据
        app.logger.info("接口接收数据为空(*>﹏<*)【audit】")
        return return_data("audit")
    try:
        request_string = request.get_data().decode('utf-8-sig')  # 数据解码, 数据解析
        first_unquote = unquote_plus(request_string, encoding='utf-8-sig')
        second_unquote = unquote_plus(first_unquote, encoding='utf-8-sig')
        re_data = re.sub("\r|\n|\t|\s", "", second_unquote)
        decode_list = re_data.split('&')  # 解析数据
        decode_dict = {}
        for i in decode_list:
            i = i.split("=")
            decode_dict[i[0]] = i[1]
        audit_id = decode_dict.get('ticket_code', '')  # 获取12306订单号
        if not audit_id:  # 检查是否有订单号
            run_time = round(time.time() - start_time, 2)
            db = mongo_client['statistics']
            db['monitor'].insert_one({"status": "audit", "key": "", "start_time": int(start_time), "run_time": run_time,
                                   "ip": "", "proxy": "", "real_msg": "接口数据没有单号", "return_msg": "审核失败"})
            app.logger.info(f"接口数据没有单号(*>﹏<*)【audit】【{run_time}】")
            return return_data("audit")
        audit_key = f"audit{audit_id}"  # 拼接存储key
        result_data = redis_result.hgetall(audit_key)  # 先查询结果库有没有
        if result_data:  # 如果有结果
            get_ip = result_data.get('ip', '')  # 取出机器地址
            get_data = result_data.get('data', '')  # 取出返回数据
            get_proxy = result_data.get('proxy', '')
            get_circulation = int(result_data.get('circulation', 0))  # 取出循环次数
            if not get_data:  # 如果没数据
                run_time = round(time.time() - start_time, 2)
                db = mongo_client['statistics']
                db['monitor'].insert_one({"status": "aduit", "key": audit_id, "start_time": int(start_time), "run_time": run_time,
                                       "ip": get_ip, "proxy": get_proxy, "real_msg": "再次查询数据为空", "return_msg": "下单失败"})
                app.logger.info(f"再次查询数据为空(*>﹏<*)【audit】【{run_time}】【{audit_id}】【{get_ip}】")
                return return_data("audit")
            else:  # 如果有数据
                if get_circulation:  # 如果循环
                    return get_data  # 直接返回数据
                else:  # 如果不循环
                    redis_result.delete(audit_key)  # 删除数据
        else:  # 如果没有结果
            pass
        machine = ""
        for i in range(config.MAX_NUM):  # 超时时间多少，间隔1秒去查询
            time.sleep(1)
            machine = redis_queue.rpop(config.MACHINE_QUEUE)
            if machine:
                if os.system(f"ping -w2 -c1 {machine}"):
                    redis_queue.lpush("machine_broken", machine)
                    continue
                else:
                    break
        if not machine:
            run_time = round(time.time() - start_time, 2)
            db = mongo_client['statistics']
            db['monitor'].insert_one({"status": "audit", "key": audit_id, "start_time": int(start_time), "run_time": run_time,
                                   "ip": "", "proxy": "", "real_msg": "获取不到审核机器", "return_msg": "审核失败"})
            app.logger.info(f"获取不到审核机器(*>﹏<*)【audit】【{run_time}】【{audit_id}】")
            return return_data("audit")
        send_data = {"key_label": audit_key, "key_data": decode_dict}  # 拼接数据
        redis_machine.hmset(machine, send_data)  # 发送消息
        for x in range(config.MAX_NUM):  # 超时时间多少，间隔1秒去查询
            time.sleep(1)
            result_data = redis_result.hgetall(audit_key)  # 查询数据库
            if result_data:  # 如果有结果
                get_ip = result_data.get('ip', '')  # 取出机器地址
                get_data = result_data.get('data', '')  # 取出返回数据
                get_proxy = result_data.get('proxy', '')
                get_real = result_data.get('real_message', '')
                get_return = result_data.get('return_message', '')
                if not get_data:  # 如果没数据
                    run_time = round(time.time() - start_time, 2)
                    db = mongo_client['statistics']
                    db['monitor'].insert_one({"status": "audit", "key": audit_id, "start_time": int(start_time), "run_time": run_time,
                                           "ip": get_ip, "proxy": get_proxy, "real_msg": "首次查询数据为空", "return_msg": "审核失败"})
                    app.logger.info(f"首次查询数据为空(*>﹏<*)【audit】【{run_time}】【{audit_id}】【{get_ip}】")
                    return return_data("audit")
                else:  # 如果有数据
                    run_time = round(time.time() - start_time, 2)
                    db = mongo_client['statistics']
                    db['monitor'].insert_one({"status": "audit", "key": audit_id, "start_time": int(start_time), "run_time": run_time,
                                           "ip": get_ip, "proxy": get_proxy, "real_msg": get_real, "return_msg": get_return})
                    app.logger.info(f"审核数据返回成功(*^__^*)【audit】【{run_time}】【{audit_id}】【{get_ip}】【{get_proxy}】【{get_real}】")
                    return get_data  # 直接返回数据
    except Exception as ex:
        app.logger.info(f"审核程序返回失败(*>﹏<*)【audit】【{ex}】")
        return return_data("audit")
    else:
        run_time = round(time.time() - start_time, 2)
        db = mongo_client['statistics']
        db['monitor'].insert_one({"status": "audit", "key": audit_id, "start_time": int(start_time), "run_time": run_time,
                               "ip": "", "proxy": "", "real_msg": "审核程序返回超时", "return_msg": "审核失败"})
        app.logger.info(f"审核程序返回超时(⊙﹏⊙)【audit】【{run_time}】【{audit_id}】【{machine}】")
        return return_data("audit")


if __name__ == '__main__':
    app.run(debug=False)
