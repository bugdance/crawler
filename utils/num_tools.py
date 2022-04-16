#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> num tools
@@..> package utils
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> base import
from typing import Generator
# @@..> NumAct
from random import random, randint
from ctypes import c_uint32
# @@..> TimeAct
from datetime import datetime, timedelta
from calendar import monthrange
import time
# import pytz


#######################################################################################
# @@... to be continue
class NumAct:
    """
    [about num object]
    """
    logger: any = False

    @classmethod
    def format_random(cls, is_decimals: bool = False, decimal_num: int = 2,
                      start_num: int = 0, end_num: int = 1) -> any:
        """
        [return a random number]

        Args:
            is_decimals (bool, optional): [if decimals or integers].
                Defaults to False.
            decimal_num (int, optional): [num of decimals]. Defaults to 2.
            start_num (int, optional): [nothing.]. Defaults to 0.
            end_num (int, optional): [nothing.]. Defaults to 1.

        Returns:
            any: [int/float. Defaults to int]
        """
        if is_decimals:
            if isinstance(decimal_num, int) and decimal_num:
                return round(random(), decimal_num)
            else:
                cls.logger.info("格式Random数据失败(*>﹏<*)【float】")
                return 0.0
        else:
            if isinstance(start_num, int) and isinstance(end_num, int):
                return randint(start_num, end_num)
            else:
                cls.logger.info("格式Random数据失败(*>﹏<*)【int】")
                return 0

    @classmethod
    def parse_average(cls, source_data: any = None,
                      decimal_num: int = 2, end_index: int = 2) -> float:
        """
        [average list of numbers]

        Args:
            source_data (any, optional): [list/tuple]. Defaults to None.
            decimal_num (int, optional): [num of decimals]. Defaults to 2.
            end_index (int, optional): [the index]. Defaults to 2.

        Returns:
            float: [nothing.]
        """
        if isinstance(source_data, (list, tuple)) \
                and isinstance(decimal_num, int) and isinstance(end_index, int):

            source_data = source_data[:end_index]
            if len(source_data):
                result_num = sum(source_data) / len(source_data)
                return round(float(result_num), decimal_num)
            else:
                return 0.0
        else:
            cls.logger.info("解析Average数据失败(*>﹏<*)【type】")
            return 0.0

    @classmethod
    def format_overflow(cls, source_data: any = 0) -> int:
        """
        [java 32 bits integer type overflow]

        Args:
            source_data (any, optional): [int/float]. Defaults to 0.

        Returns:
            int: [nothing.]
        """
        if isinstance(source_data, (int, float)):
            source_data = int(source_data)
        else:
            cls.logger.info("格式Overflow溢出失败(*>﹏<*)【type】")
            return 0
        # @@..> maximum java int
        max_int = 2147483647
        if not -max_int - 1 <= source_data <= max_int:
            source_data = (source_data + (max_int + 1)) \
                % (2 * (max_int + 1)) - max_int - 1
        else:
            source_data = source_data

        return source_data

    @classmethod
    def format_rightshift(cls, source_data: int = 0, shift_num: int = 0) -> int:
        """
        [unsigned right shift]

        Args:
            source_data (int, optional): [nothing.]. Defaults to 0.
            shift_num (int, optional): [numbers of right shift]. Defaults to 0.

        Returns:
            int: [nothing.]
        """
        if isinstance(source_data, int) and \
                isinstance(shift_num, int):
            pass
        else:
            cls.logger.info("格式Rightshift右移失败(*>﹏<*)【type】")
            return 0

        # @@..! if number is less than 0 then convert to 32-bit unsigned uint.
        if source_data < 0:
            source_data = c_uint32(source_data).value
        # @@..! in order to be compatible with js and things like that,
        # @@..! the negative number shifts to the left.
        if shift_num < 0:
            source_data = -cls.format_overflow(source_data << abs(shift_num))
        else:
            source_data = cls.format_overflow(source_data >> shift_num)

        return source_data


#######################################################################################
# @@... to be continue
class TimeAct:
    """
    [about time object]
    """
    logger: any = False

    @classmethod
    def format_sleep(cls, sleep_seconds: int = 10) -> bool:
        """
        [sleep x seconds]

        Args:
            sleep_seconds (int, optional): [nothing.]. Defaults to 10.

        Returns:
            bool: [nothing.]
        """
        if isinstance(sleep_seconds, (int, float)):
            time.sleep(sleep_seconds)
            return True
        else:
            cls.logger.info("格式Sleep睡眠失败(*>﹏<*)【type】")
            time.sleep(10)
            return False

    @classmethod
    def format_now(cls) -> datetime:
        """
        [return datetime now]

        Returns:
            datetime: [datetime]
        """
        return datetime.now()

    @classmethod
    def format_timestamp(cls, bit_num: int = 0) -> int:
        """
        [return timestamp]

        Args:
            bit_num (int, optional): [number of bits]. Defaults to 0.

        Returns:
            int: [timestamp.]
        """
        if isinstance(bit_num, int):
            bit_num = 10 ** bit_num
        else:
            cls.logger.info("格式Timestamp数字失败(*>﹏<*)【type】")
            bit_num = 10 ** 0

        timestamp = int(time.time() * bit_num)
        return timestamp

    @classmethod
    def parse_timestamp(cls, source_data: int = 0) -> datetime:
        """
        [turn timestamp into datetime]

        Args:
            source_data (int, optional): [timestamp]. Defaults to 0.

        Returns:
            datetime: [datetime]
        """
        if isinstance(source_data, int) and len(str(source_data)) == 10:
            return datetime(1970, 1, 1) + timedelta(seconds=source_data)
        else:
            cls.logger.info("解析Timestamp时间失败(*>﹏<*)【type】")
            return datetime.now()

    @classmethod
    def parse_datetime(cls, source_data: datetime = None) -> int:
        """
        [turn datetime into timestamp]

        Args:
            source_data (datetime, optional): [datetime]. Defaults to None.

        Returns:
            int: [timestamp]
        """
        if isinstance(source_data, datetime):
            pass
        else:
            cls.logger.info("解析Timestamp时间失败(*>﹏<*)【type】")
            source_data = datetime.now()

        timestamp = time.mktime(source_data.timetuple())
        return int(timestamp)

    @classmethod
    def parse_timestring(cls, source_data: str = "",
                         time_format: str = "") -> datetime:
        """
        [turn string into datetime]

        Args:
            source_data (str, optional): [time string]. Defaults to nothing.
            time_format (str, optional): [formatter]. Defaults to nothing.

        Returns:
            datetime: [datetime]
        """
        try:
            return datetime.strptime(source_data, time_format)
        except Exception as ex:
            cls.logger.info(f"解析Timestring时间失败(*>﹏<*)【{ex}】")
            return datetime.now()

    @classmethod
    def parse_custom(cls, source_time: datetime = None,
                     days: any = 0, hours: any = 0,
                     minutes: any = 0, seconds: any = 0) -> datetime:
        """
        [custom datetime]

        Args:
            source_data (datetime, optional): [datetime]. Defaults to None.
            days (any, optional): [int/float]. Defaults to 0.
            hours (any, optional): [int/float]. Defaults to 0.
            minutes (any, optional): [int/float]. Defaults to 0.
            seconds (any, optional): [int/float]. Defaults to 0.

        Returns:
            datetime: [datetime]
        """
        try:
            return source_time + timedelta(
                days=days, hours=hours, minutes=minutes, seconds=seconds)
        except Exception as ex:
            cls.logger.info(f"解析Customs时间失败(*>﹏<*)【{ex}】")
            return datetime.now()

    @classmethod
    def parse_lastday(cls, source_year: int = 0, source_month: int = 0) -> int:
        """
        [the last day of the month]

        Args:
            source_year (int, optional): [nothing.]. Defaults to 0.
            source_month (int, optional): [nothing.]. Defaults to 0.

        Returns:
            int: [nothing.]
        """
        try:
            return monthrange(source_year, source_month)[1]
        except Exception as ex:
            cls.logger.info(f"解析Lastday时间失败(*>﹏<*)【{ex}】")
            return 31

    @classmethod
    def format_datelist(
            cls, start_date: str = "", end_date: str = "",
            date_step: int = 1, date_format: str = "%Y-%m-%d") -> Generator:
        """
        [summary]

        Args:
            start_date (str, optional): [nothing.]. Defaults to nothing.
            end_date (str, optional): [nothing.]. Defaults to nothing.
            date_step (int, optional): [nothing.]. Defaults to 1.
            date_format (str, optional): [nothing.]. Defaults to %Y-%m-%d.

        Returns:
            [Generator]: [nothing.]
        """
        try:
            start_time = datetime.strptime(start_date, date_format)
            end_time = datetime.strptime(end_date, date_format)
            days = (end_time - start_time).days + 1

            for i in range(0, days, date_step):
                yield datetime.strftime(start_time + timedelta(i), date_format)
        except Exception as ex:
            cls.logger.info(f"解析Lastday时间失败(*>﹏<*)【{ex}】")
            return (x for x in range(0))
