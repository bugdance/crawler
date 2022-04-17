#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@@..> json tools
@@..> package utils
@@..> author pyleo <lihao@372163.com>
"""
#######################################################################################
# @@..> base import
from typing import Generator
# @@..> JsonAct
from jsonpath import jsonpath
import demjson
import yaml


#######################################################################################
class JsonAct:
    """
    [about json object]
    """
    logger: any = False

    @classmethod
    def format_string(cls, source_data: any = None, encoding: str = "utf-8") -> str:
        """
        [format json to string]

        Args:
            source_data (any, optional): [list/dict]. Defaults to None.
            encoding (str, optional): [utf8/gbk]. Defaults to utf-8.

        Returns:
            str: [nothing.]
        """
        if isinstance(source_data, (list, dict)) and isinstance(encoding, str):
            try:
                # @@..! must strict mode
                source_data = demjson.encode(
                    source_data, encoding=encoding, strict=False)
            except demjson.JSONEncodeError:
                cls.logger.info("格式Json字符失败(*>﹏<*)【string】")
                return ""
            else:
                return source_data.decode(encoding)
        else:
            cls.logger.info("格式Json字符失败(*>﹏<*)【type】")
            return ""

    @classmethod
    def format_json(cls, source_data: any = None, encoding: str = "utf-8") -> any:
        """
        [format string to json]

        Args:
            source_data (any, optional): [str/bytes]. Defaults to None.
            encoding (str, optional): [utf-8/gbk]. Defaults to utf-8.

        Returns:
            any: [list/dict. Defaults to list]
        """
        if isinstance(source_data, (str, bytes)) and isinstance(encoding, str):
            try:
                # @@..! must strict mode
                source_data = demjson.decode(
                    source_data, encoding=encoding, strict=False)
            except demjson.JSONDecodeError:
                cls.logger.info("格式Json对象失败(*>﹏<*)【list】")
                return []
            else:
                return source_data
        else:
            cls.logger.info("格式Json对象失败(*>﹏<*)【type】")
            return []

    @classmethod
    def parse_json(cls, source_data: any = None, path_syntax: str = "$.") -> Generator:
        """
        [parse json value]

        Args:
            source_data (any, optional): [list/dict]. Defaults to None.
            path_syntax (str, optional): [path syntax]. Defaults to $..

        Returns:
            Generator: [nothing.]
        """
        if isinstance(source_data, (list, dict)) and isinstance(path_syntax, str):
            source_data = jsonpath(source_data, path_syntax)
            if source_data is False:
                return (x for x in range(0))
            else:
                for i in source_data:
                    yield i
        else:
            cls.logger.info("解析Json对象失败(*>﹏<*)【type】")
            return (x for x in range(0))

    @classmethod
    def format_yaml(cls, source_data: any = None, file_path: str = "") -> bool:
        """
        [format json to yaml]

        Args:
            source_data (any, optional): [list/dict]. Defaults to None.
            file_path (str, optional): [nothing.]. Defaults to nothing.

        Returns:
            bool: [nothing.]
        """
        if isinstance(source_data, (list, dict)) and isinstance(file_path, str):
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    yaml.dump(source_data, f)
                return True
            except FileNotFoundError:
                cls.logger.info("格式Yaml对象失败(*>﹏<*)【yaml】")
                return False
        else:
            cls.logger.info("格式Yaml对象失败(*>﹏<*)【type】")
            return False

    @classmethod
    def parse_yaml(cls, file_path: str = "", ) -> any:
        """
        [parse yaml to json]

        Args:
            file_path (str, optional): [nothing.]. Defaults to nothing.

        Returns:
            any: [list/dict. Defaults to list]
        """
        if isinstance(file_path, str):
            try:
                with open(file_path, encoding="utf-8") as f:
                    return_data = yaml.safe_load(f.read())

                if isinstance(return_data, (list, dict)):
                    return return_data
                else:
                    return []
            except FileNotFoundError:
                cls.logger.info("解析Yaml对象失败(*>﹏<*)【json】")
                return []
        else:
            cls.logger.info("解析Yaml对象失败(*>﹏<*)【type】")
            return []
