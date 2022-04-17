#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@@..> base tools
@@..> package utils
@@..> author pyleo <lihao@372163.com>

@@..> descriptive
@@..? uncertain
@@..! important
@@..x discarded
@@... unfinished
"""
#######################################################################################
# @@..> base import
from dataclasses import dataclass, field
from typing import Iterable
from functools import wraps
# @@..> BaseAct
from pprint import pprint
from copy import deepcopy
from itertools import tee
# @@..> LogAct
import logging


#######################################################################################
class BaseAct:
    """
    [base functions]
    """

    @classmethod
    def format_print(cls, source_data: any = None) -> any:
        """
        [print object]

        Args:
            source_data (any, optional): [nothing.]. Defaults to None.

        Returns:
            any: [nothing.]
        """
        if isinstance(source_data, (str, list, tuple, set, dict)):
            pprint(source_data)
        else:
            print(source_data)

    @classmethod
    def format_copy(cls, source_data: any = None) -> any:
        """
        [copy object]

        Args:
            source_data (any, optional): [nothing.]. Defaults to None.

        Returns:
            any: [nothing.]
        """
        source_data = deepcopy(source_data)
        return source_data

    @classmethod
    def format_generator(cls, source_data: Iterable = None) -> tuple:
        """
        [copy generate object]

        Args:
            source_data (Iterable, optional): [iterable]. Defaults to None.

        Returns:
            tuple: [two generator]
        """
        if isinstance(source_data, Iterable):
            gen_default, gen_copy = tee(source_data)
            return gen_default, gen_copy
        else:
            return (x for x in range(0)), (x for x in range(0))

    @classmethod
    def parse_generator(cls, source_data: Iterable = None,
                        is_last: bool = False) -> tuple:
        """
        [parse generator]

        Args:
            source_data (Iterable, optional): [iterable]. Defaults to None.

        Returns:
            tuple: [first value/generator]
        """
        default_value = False
        gen_default, gen_copy = cls.format_generator(source_data)
        if is_last:
            for i in gen_copy:
                default_value = i
        else:
            for i in gen_copy:
                default_value = i
                break
        return default_value, gen_default


#######################################################################################
class LogAct:
    """
    [custom log tool]
    """

    @classmethod
    def init_log(cls, log_path: str = "init.log", is_print: bool = True) -> tuple:
        """
        [start log]

        Args:
            log_path (str, optional): [log file]. Defaults to init.log.
            is_print (bool, optional): [print log or not]. Defaults to True.

        Returns:
            tuple: [logger, handler]
        """
        if not isinstance(log_path, str) or not log_path:
            log_path = "init.log"
        if not isinstance(is_print, bool):
            is_print = True
        # setup
        logger = logging.getLogger(log_path)
        logger.setLevel(level=logging.INFO)
        # load handler
        handler = logging.StreamHandler()
        if not is_print:
            handler = logging.FileHandler(log_path, encoding='utf-8')

        handler.setFormatter(logging.Formatter('[%(asctime)s]%(message)s'))
        logger.addHandler(handler)
        return logger, handler

    @classmethod
    def unload_log(cls, logger: logging.Logger = None, handler: any = None) -> bool:
        """
        [end log]

        Args:
            logger (logging.Logger, optional): [logger]. Defaults to None.
            handler (logging.handlers, optional): [handler]. Defaults to None.

        Returns:
            bool: [nothing.]
        """
        if isinstance(logger, logging.Logger) and \
                isinstance(handler, (logging.StreamHandler, logging.FileHandler)):
            logger.removeHandler(handler)
            return True
        else:
            return False


#######################################################################################
# @@... decorator
@dataclass
class ErrorMessage:
    """
    [error message]
    """
    __message: str = field(default_factory=str)

    def __call__(self, func):

        @wraps(func)
        def wrapped_function(*args, **kwargs):
            try:
                func(*args, **kwargs)
                return False
            except Exception as ex:
                return f"{self.__message}(*>﹏<*)【{ex}】"
        return wrapped_function


def error_async(message: str = ""):
    def wrapper(func):
        async def wrapped_function(*args, **kwargs):
            try:
                await func(*args, **kwargs)
                return False
            except Exception as ex:
                return f"{message}(*>﹏<*)【{ex}】"
        return wrapped_function
    return wrapper
