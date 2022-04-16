#!/usr/bin/env python
# -*- encoding: utf-8 -*-

BOT_NAME = 'example'
LOG_LEVEL = 'INFO'

SPIDER_MODULES = ['example.spiders']
NEWSPIDER_MODULE = 'example.spiders'

USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'

DEFAULT_REQUEST_HEADERS = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh,en;q=0.5',
        }

ITEM_PIPELINES = [
            'example.pipelines.BasicPipeline',
            'example.pipelines.DebugPipeline',
            'example.pipelines.MongoPipeline',
            'example.pipelines.MysqlPipeline',
        ]

EXTENSIONS = {
            'scrapy.webservice.WebService': None,
            'example.extensions.StatsPoster': 999
        }

DOWNLOADER_MIDDLEWARES = {
            'example.middlewares.DedupMiddleware': 999,
            'example.middlewares.ProxyMiddleware': 999,
            'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': None,
            'example.middlewares.RetryMiddleware': 500,
        }

SPIDER_MIDDLEWARES = {
        }

COOKIES_ENABLED = False
TELNETCONSOLE_ENABLED = False
#DOWNLOAD_DELAY = 60
#DOWNLOAD_TIMEOUT = 60
RETRY_TIMES = 3

#DEFAULT_LOGGER = 'mongodb://localhost:27017/result.data'
DEFAULT_LOGGER = 'mysql://root:logis2017@localhost:33306/website.spider_monitors'
DEFAULT_DEDUP = None

