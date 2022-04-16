#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
@@..> data tools
@@..> package utils
@@..> author pyLeo <lihao@372163.com>
"""
#######################################################################################
# @@..> base import
from dataclasses import dataclass, field
from typing import Iterable
# @@..> DataAct
from io import StringIO, BytesIO
import numpy as np
import cv2
# import pandas as pd
# import tensorflow as tf


#######################################################################################
# @@... to be continue
@dataclass
class DataAct:
    """
    [data object]
    """
    __logger: any = field(default_factory=bool)

    @property
    def logger(self):
        return self.__logger

    @logger.setter
    def logger(self, value):
        self.__logger = value

    def parse_io(self, source_data: any = None, is_string: bool = True) -> any:
        """
        [turn into the io]

        Args:
            source_data (any, optional): [nothing.]. Defaults to None.
            is_string (bool, optional): [nothing.]. Defaults to True.

        Returns:
            any: [nothing.]
        """
        if is_string:
            if not isinstance(source_data, str):
                self.logger.info("解析IO数据失败(*>﹏<*)【type】")
                return ""
            return StringIO(source_data)
        else:
            if not isinstance(source_data, bytes):
                self.logger.info("解析IO数据失败(*>﹏<*)【type】")
                return b""
            return BytesIO(source_data)

    def parse_distance(self, front_pic: bytes = b"", back_pic: bytes = b"") -> int:
        """
        [count the slide distance]

        Args:
            front_pic (bytes, optional): [front picture]. Defaults to nothing.
            back_pic (bytes, optional): [back picture]. Defaults to nothing.

        Returns:
            int: [nothing.]
        """
        try:
            target = cv2.imdecode(
                np.asarray(bytearray(front_pic.read()), dtype=np.uint8), 0)
            template = cv2.imdecode(
                np.asarray(bytearray(back_pic.read()), dtype=np.uint8), 0)
            result = cv2.matchTemplate(target, template, cv2.TM_CCORR_NORMED)
            _, distance = np.unravel_index(result.argmax(), result.shape)
            return distance
        except Exception as ex:
            self.logger.info(f"解析Distance数据失败(*>﹏<*)【{ex}】")
            return 0
    
    # def format_csv(self, path: str = "", title_list: list = None):
    #     cont_list = [{"name": 1, "age": 14},{"name": 2, "age": 14},]
    #     df = pd.DataFrame(cont_list, columns=['name', "age"])
    #     df.to_csv("aa.csv", index=False)