#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@@..> pool tools
@@..> package utils
@@..> author pyleo <lihao@372163.com>
"""
#######################################################################################
# @@..> base import
from dataclasses import dataclass, field
from typing import Iterable
# @@..> PoolAct
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_pymongo import PyMongo
from flask_redis import FlaskRedis


#######################################################################################
# @@... to be continue
@dataclass
class PoolAct:
    """
    [mysql/mongo/redis client]
    """
    __logger: any = field(default_factory=bool)
    __app: Flask = field(default_factory=bool)
    __mysql: SQLAlchemy = field(default_factory=bool)
    __redis: FlaskRedis = field(default_factory=bool)

    @property
    def logger(self):
        return self.__logger

    @logger.setter
    def logger(self, value):
        self.__logger = value

    @property
    def app(self):
        return self.__app

    @property
    def mysql(self):
        return self.__mysql

    @property
    def redis(self):
        return self.__redis

    def init_app(self) -> None:
        """
        [create app]

        Returns:
            None: [nothing.]
        """
        self.__app = Flask(__name__)
        self.__app.config['JSON_AS_ASCII'] = False

    def init_mysql(self, mysql_uri: str = "") -> any:
        """
        [mysql client]

        Args:
            mysql_uri (str, optional):
                [mysql://user:pass@127.0.0.1:3306/test?charset=utf8mb4].
                Defaults to nothing.

        Returns:
            scoped_session: [sqlalchemy.orm.scoping.scoped_session]
        """
        try:
            self.__app.config['SQLALCHEMY_DATABASE_URI'] = mysql_uri
            self.__app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            self.__app.config['SQLALCHEMY_ECHO'] = False
            self.__app.config['SQLALCHEMY_POOL_SIZE'] = 100
            self.__app.config['SQLALCHEMY_MAX_OVERFLOW'] = 100
            self.__app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
            self.__mysql = SQLAlchemy(self.__app).session
            return True
        except Exception as ex:
            self.__logger.info(f"初始Mysql连接失败(*>﹏<*)【{ex}】")
            return False

    def execute_mysql(self, sql: str = "", is_commit: bool = False) -> bool:
        """
        [execute sql]

        Args:
            sql (str, optional): [nothing.]. Defaults to nothing.
            is_commit (bool, optional): [if commit or not]. Defaults to False.

        Returns:
            bool: [nothing.]
        """
        try:
            if is_commit:
                self.__mysql.commit()
            else:
                self.__mysql.execute(sql)
            return True
        except Exception as ex:
            self.__logger.info(f"执行Mysql语句失败(*>﹏<*)【{ex}】")
            return False

    def query_mysql(self, sql: str = "") -> Iterable:
        """
        [execute sql]

        Args:
            sql (str, optional): [nothing.]. Defaults to nothing.

        Returns:
            Iterable: [sqlalchemy.engine.cursor.CursorResult]
        """
        try:
            result = self.__mysql.execute(sql)
            return result
        except Exception as ex:
            self.__logger.info(f"查询Mysql语句失败(*>﹏<*)【{ex}】")
            return (x for x in range(0))

    def close_mysql(self) -> bool:
        """
        [close mysql session]

        Returns:
            bool: [nothing.]
        """
        try:
            self.__mysql.close()
            return True
        except Exception as ex:
            self.__logger.info(f"关闭Mysql连接失败(*>﹏<*)【{ex}】")
            return False

    def init_mongo(self, mongo_uri: str = "") -> any:
        """
        [mongo client]

        Args:
            mongo_uri (str, optional):
                [mongodb://user:pass@127.0.0.1:27017/test]. Defaults to nothing.

        Returns:
            Database: [flask_pymongo.wrappers.Database]
        """
        try:
            self.__app.config['MONGO_MAX_POOL_SIZE'] = 100
            mongo = PyMongo(self.__app, uri=mongo_uri,
                            connect=False, serverSelectionTimeoutMS=10)
            return mongo.db
        except Exception as ex:
            self.__logger.info(f"初始Mongo连接失败(*>﹏<*)【{ex}】")
            return False

    def query_mongo(self, mongo_db: any = None, col_name: str = "",
                    filters: dict = None, projects: dict = None,
                    sorts: list = None, skips: int = 0,
                    limits: int = 0) -> Iterable:
        """
        [mongo find]

        Args:
            mongo_db (Database, optional): [database]. Defaults to None.
            col_name (str, optional): [collection]. Defaults to nothing.
            filters (dict, optional): [filter]. Defaults to None.
            projects (dict, optional): [project]. Defaults to None.
            sorts (list, optional): [sort]. Defaults to None.
            skips (int, optional): [skip]. Defaults to 0.
            limits (int, optional): [limit]. Defaults to 0.

        Returns:
            Iterable: [pymongo.cursor.Cursor]
        """
        try:
            result = (x for x in range(0))
            if projects:
                if sorts:
                    result = mongo_db[col_name].find(
                        filters, projects).sort(sorts).skip(skips).limit(limits)
                else:
                    result = mongo_db[col_name].find(
                        filters, projects).skip(skips).limit(limits)
            else:
                if sorts:
                    result = mongo_db[col_name].find(
                        filters).sort(sorts).skip(skips).limit(limits)
                else:
                    result = mongo_db[col_name].find(
                        filters).skip(skips).limit(limits)

            return result
        except Exception as ex:
            self.__logger.info(f"查询Mongo数据失败(*>﹏<*)【{ex}】")
            return (x for x in range(0))

    def aggregate_mongo(self, mongo_db: any = None, col_name: str = "",
                        aggregate_list: list = None) -> Iterable:
        """
        [mongo aggregate]

        Args:
            mongo_db (Database, optional): [database]. Defaults to None.
            col_name (str, optional): [collection]. Defaults to nothing.
            aggregate_list (dict, optional): [filter]. Defaults to None.

        Returns:
            Iterable: [pymongo.command_cursor.CommandCursor]
        """
        try:
            result = mongo_db[col_name].aggregate(
                aggregate_list, allowDiskUse=True)
            return result
        except Exception as ex:
            self.__logger.info(f"合计Mongo数据失败(*>﹏<*)【{ex}】")
            return (x for x in range(0))

    def update_mongo(self, mongo_db: any = None, col_name: str = "",
                     filters: dict = None, updates: dict = None,
                     upserts: bool = False, multis: bool = False) -> bool:
        """
        [mongo update]

        Args:
            mongo_db (Database, optional): [database]. Defaults to None.
            col_name (str, optional): [collection]. Defaults to nothing.
            filters (dict, optional): [filters]. Defaults to None.
            updates (dict, optional): [updates]. Defaults to None.
            upserts (bool, optional): [upsert]. Defaults to False.
            multis (bool, optional): [multi]. Defaults to False.

        Returns:
            bool: [nothing.]
        """
        try:
            mongo_db[col_name].update(
                filters, updates, upsert=upserts, multi=multis)
            return True
        except Exception as ex:
            self.__logger.info(f"更新Mongo数据失败(*>﹏<*)【{ex}】")
            return False

    def close_mongo(self, mongo_db: any = None) -> bool:
        """
        [close mysql session]

        Args:
            mongo_db (Database, optional): [database]. Defaults to None.

        Returns:
            bool: [nothing.]
        """
        try:
            del mongo_db
            return True
        except Exception as ex:
            self.__logger.info(f"关闭Mongo连接失败(*>﹏<*)【{ex}】")
            return False

    def init_redis(self, redis_uri: str = "") -> FlaskRedis:
        """
        [redis client]

        Args:
            redis_uri (str, optional): [redis://user:pass@127.0.0.1:6379/0].
                Defaults to nothing.

        Returns:
            FlaskRedis: [nothing.]
        """
        try:
            self.__app.config['REDIS_URL'] = redis_uri
            self.__redis = FlaskRedis(self.__app, decode_responses=True)
            return True
        except Exception as ex:
            self.__logger.info(f"初始Redis连接失败(*>﹏<*)【{ex}】")
            return False

    def query_redis(self, key_name: str = "") -> bool:
        """
        [redis find key]

        Args:
            key_name (str, optional): [key]. Defaults to nothing.

        Returns:
            bool: [nothing.]
        """
        try:
            result = self.__redis.exists(key_name)
            if result:
                return True
            else:
                return False
        except Exception as ex:
            self.__logger.info(f"查询Redis数据失败(*>﹏<*)【{ex}】")
            return False

    def push_redis(self, key_name: str = "", insert_data: str = "") -> bool:
        """
        [redis push data]

        Args:
            key_name (str, optional): [key]. Defaults to nothing.
            insert_data (str, optional): [push data]. Defaults to nothing.

        Returns:
            bool: [nothing.]
        """
        try:
            self.__redis.lpush(key_name, insert_data)
            return True
        except Exception as ex:
            self.__logger.info(f"推送Redis数据失败(*>﹏<*)【{ex}】")
            return False

    def pop_redis(self, key_name: str = "", time_out: int = 5) -> bool:
        """
        [redis pop data]

        Args:
            key_name (str, optional): [key]. Defaults to nothing.
            time_out (int, optional): [nothing.]. Defaults to 5.

        Returns:
            bool: [nothing.]
        """
        try:
            result_data = self.__redis.brpop(key_name, time_out)
            if result_data is None:
                return ""
            else:
                return result_data[1]
        except Exception as ex:
            self.__logger.info(f"获取Redis数据失败(*>﹏<*)【{ex}】")
            return ""

    def close_redis(self) -> bool:
        """
        [close redis client]

        Returns:
            bool: [nothing.]
        """
        try:
            self.__redis.close()
            return True
        except Exception as ex:
            self.__logger.info(f"关闭Redis连接失败(*>﹏<*)【{ex}】")
            return False

