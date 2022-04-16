#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Define your item pipelines here

from scrapy import log
from scrapy.exceptions import DropItem
from datetime import datetime
from example.utils import utils
import re, traceback


def item2post(item):
    post = {}
    for k,v in item.fields.items():
        if 'name' in v:
            post[v['name']] = item[k]
    return post


class BasicPipeline(object):
    def process_item(self, item, spider):
        try:
            for k,v in item.fields.items():
                if type(item[k])==list:
                    item[k] = item[k][0]
            return item
        except Exception as ex:
            raise DropItem('item error: {}'.format(ex))


class DebugPipeline(object):
    def open_spider(self, spider):
        self.idx = 0

    def process_item(self, item, spider):
        if not (hasattr(spider, 'debug') and spider.debug):
            return item

        self.idx += 1
        print(utils.B('{:=^30}'.format(self.idx)))
        for k,v in item.items():
            if type(v) in [str, str]:
                v = re.sub(r'\s{2,}', ' ', v.replace('\n', ' ').replace('\r', ''))
                if spider.verbose<3 and len(v)>74:
                    v = '{} {} {}'.format(v[:60].strip(), utils.B('……'), v[-14:].strip())
            elif type(v)==datetime:
                now = datetime.utcnow()
                if v>now:
                    colored = utils.RR
                elif (now-v).total_seconds()>24*3600:
                    colored = utils.R
                else:
                    colored = lambda x:x
                offset = utils.tz_offset(spider.tz)
                v = colored(v + offset)
            f = ' ' if 'name' in item.fields[k] else '*'
            print('{:>10.10}{}: {}'.format(k, f, v).encode('utf-8'))

        return item


# 数据存储(mongo)
class MongoPipeline(object):
    def open_spider(self, spider):
        if hasattr(spider, 'mongo'):
            try:
                uri = spider.mongo
                log.msg('connect <{}>'.format(uri))
                self.cnn, self.db, self.tbl = utils.connect_uri(uri)
                return
            except Exception as ex:
                log.err('cannot connect to mongodb: {}'.format(ex))

        self.cnn = self.db = None

    def process_item(self, item, spider):
        if self.cnn:
            try:
                post = item2post(item)
                self.tbl.insert(post)
            except Exception as ex:
                traceback.print_exc()
        return item

    def close_spider(self, spider):
        if self.cnn:
            log.msg('disconnect mongodb')
            self.cnn.close()
            self.cnn = None


# 数据存储(mysql)
class MysqlPipeline(object):
    def open_spider(self, spider):
        if hasattr(spider, 'mysql'):
            try:
                uri = spider.mysql
                log.msg('connect <{}>'.format(uri))
                self.cnn, _, self.tbl = utils.connect_uri(uri)
                self.cur = self.cnn.cursor()
                return
            except Exception as ex:
                traceback.print_exc()
                log.err('cannot connect to mysql: {}'.format(ex))

        self.cnn = self.cur = None

    def process_item(self, item, spider):
        if self.cnn:
            try:
                post = item2post(item)
                fields = []
                values = []
                for k,v in post.items():
                    fields.append(k)
                    values.append(v)
                self.cur.execute("""INSERT INTO {}({}) VALUES({});""".format(
                                                                                self.tbl,
                                                                                ','.join(fields),
                                                                                ','.join(['%s']*len(fields))
                                                                            ), values)
                self.cnn.commit()
            except Exception as ex:
                traceback.print_exc()
        return item

    def close_spider(self, spider):
        if self.cnn:
            log.msg('disconnect mysql')
            self.cur.close()
            self.cnn.close()
            self.cnn = self.cur = None


