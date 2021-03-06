#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from scrapy import log
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.exceptions import CloseSpider
from scrapy.http import Request, FormRequest
from scrapy.item import Item, Field
from scrapy.selector import HtmlXPathSelector
from scrapy.utils.misc import arg_to_iter
from scrapy.utils.datatypes import CaselessDict
from cssselect.xpath import HTMLTranslator
from example.uitls import utils
from example import settings
from urllib2 import urlparse
from pprint import pprint
import re, json, jsonpath_rw, http.cookies, traceback


class ExampleSpider(CrawlSpider):

    name = 'example'

    def __init__(self, config=None, debug=None, verbose=0, **kwargs):
        super(ExampleSpider, self).__init__()
        self.config = config
        self.debug = debug
        self.verbose = int(verbose)
        self.tz = kwargs.get('tz', '+00:00')
        self.conf = self.load_config()

    def start_requests(self):
        self.log('loading config from <{}>:\n{}'.format(str(self.config, encoding='utf-8'),
            json.dumps(self.conf, indent=4, ensure_ascii=False, sort_keys=True)), level=log.INFO)
        self.debug_mode()
        for i in CrawlSpider.start_requests(self):
            yield i

    def debug_mode(self):
        if self.debug==None:
            return
        self.debug = str(self.debug).upper()=='TRUE'
        if self.debug:
            log.msg(utils.G('{:=^20}'.format(' DEBUG MODE ')))
            if hasattr(self, 'mongo'):
                self.log(utils.Y('disable mongo'), level=log.WARNING)
                del self.mongo
            if hasattr(self, 'mysql'):
                self.log(utils.Y('disable mysql'), level=log.WARNING)
                del self.mysql

    def load_config(self):
        conf = utils.load_cfg(self.config)

        #### debug
        if self.debug==None:
            self.debug = conf.get('debug', False)

        #### site
        self.site = conf.get('site', '????????????')
        self.macro = utils.MacroExpander({
            'SITE': self.site,
            'CONF': json.dumps(conf)
        })

        #### allowed_domains
        self.allowed_domains = conf.get('domains', [])

        #### start_urls
        urls = conf.get('urls', [])
        self.start_urls = utils.generate_urls(urls, self.macro)
        self.start_method = urls.get('method', 'GET') if type(urls)==dict else 'GET'
        self.make_headers(urls.get('headers', {}) if type(urls)==dict else {})

        #### rules
        self.tr = HTMLTranslator()
        self.rules = []
        self.page_extractor = None
        for k,v in conf.get('rules', {}).items():

            follow = v.get('follow', True)
            callback = None if follow else 'parse_page'
            follow = True if follow is None else follow
            regex = self.macro.expand(v.get('regex'))
            css = self.macro.expand(v.get('css'))
            if css:
                xpath = self.tr.css_to_xpath(css)
            else:
                xpath = self.macro.expand(v.get('xpath'))
            pages = v.get('pages')
            sub = v.get('sub')

            rule = Rule(
                SgmlLinkExtractor(
                    allow=regex,
                    restrict_xpaths=xpath,
                    process_value=utils.first_n_pages(regex, pages)),
                process_links=self.sub_links(sub),
                callback=callback,
                follow=follow
            )

            self.rules.append(rule)
        self._compile_rules()

        if not self.rules:
            self.parse = self.parse_page
            self.make_page_extractor(conf.get('urls', []))

        ### mappings(loop/fields)
        self.build_mappings(conf)

        ### proxy
        self.proxy = conf.get('proxy', {})

        ### database
        for db in ['mongo', 'mysql']:
            if db in conf:
                setattr(self, db, conf[db])

        ### settings
        self.logger = settings.DEFAULT_LOGGER
        self.dedup = settings.DEFAULT_DEDUP
        for k,v in conf.get('settings', {}).items():
            log.msg(utils.G('+SET {} = {}'.format(k, v)))
            setattr(self, k, v)

        ### parser(html)
        if hasattr(self, 'spider') and 'json' in self.spider:
            pass
        else:
            self.parse_item = self.parse_html_item


        return conf

    def build_mappings(self, conf, lvl=0):
        if lvl==0:
            self.mappings = dict()
            for k,v in conf['fields'].items():
                Item.fields[k] = Field()
                if 'name' in v:
                    Item.fields[k]['name'] = v['name']

        loop = self.macro.expand(conf.get('loop', ''))
        if loop.startswith('css:'):
            loop = self.tr.css_to_xpath(loop[len('css:'):])

        self.mappings[lvl] = {
            'loop': loop,
            'fields': conf.get('fields')
        }

        if 'continue' in conf:
            self.build_mappings(conf.get('continue'), lvl+1)

    def make_requests_from_url(self, url):
        us = urlparse.urlsplit(url)
        qstr = dict(urlparse.parse_qsl(us.query))
        base = urlparse.urlunsplit(us._replace(query=''))
        return FormRequest(base, formdata=qstr, method=self.start_method, headers=self.headers, cookies=self.cookies, dont_filter=True)


    def parse_page(self, response):
        try:
            if isinstance(response, Request):
                yield response
                return

            lvl = response.meta.get('level', 0)
            mapping = self.mappings[lvl]
            loop, fields = mapping['loop'], mapping['fields']

            for item in self.parse_item(response, loop, fields):
                yield self.maybe_continue(item, response)

            if self.page_extractor:
                for link in self.page_extractor.extract_links(response):
                    yield Request(link.url, meta=response.meta)

        except Exception as ex:
            log.msg('{}\n{}'.format(response.url, traceback.format_exc()))


    def parse_html_item(self, response, loop, fields):
        hxs = HtmlXPathSelector(response)
        self.macro.update({'URL':response.url})

        for e in hxs.select(loop or '(//*)[1]'):
            loader = XPathItemLoader(item=Item(), selector=e)

            for k,v in fields.items():
                if 'value' in v:
                    get_v_x = loader.get_value
                    v_x = v.get('value')
                elif 'css' in v:
                    get_v_x = loader.get_xpath
                    v_x = self.tr.css_to_xpath(v.get('css'))
                elif 'xpath' in v:
                    get_v_x = loader.get_xpath
                    v_x = v.get('xpath')
                else:
                    log.msg('field [{}] should contains "value", "xpath" or "css"'.format(k), level=log.WARNING)
                    continue

                val = get_v_x(
                    self.macro.expand(v_x),
                    utils.convert_type(v.get('parse', {})),
                    re=v.get('regex')
                )

                if not val and 'default' in v:
                    val = self.macro.expand(v.get('default'))

                qry = v.get('filter', {})
                if utils.filter_data(qry, val):
                    loader.add_value(k, val)
                else:
                    break
            else:
                yield loader.load_item()

    def maybe_continue(self, item, response):
        meta = response.meta
        item = self.update_item(meta.get('item', Item()), item)
        lvl = meta.get('level', 0)
        mapping = self.mappings[lvl]
        fields = mapping['fields']
        for k,v in fields.items():
            ps = v.get('parse', [{}])
            if not isinstance(ps, list):
                ps = [ps]
            if ps[-1].get('type')=='continue':
                url = item[k][0]
                meta = {
                    'level':lvl+1,
                    'item':item
                }
                return Request(url, meta=meta, callback=self.parse_page, dont_filter=True)
        return item

    def update_item(self, origin, patch):
        for k,v in patch.fields.items():
            if k in patch:
                origin[k] = patch[k]
        return origin

    def sub_links(self, sub):
        if not sub:
            return None

        frm = sub.get('from')
        to = sub.get('to')

        def _sub(links):
            new_links = []
            for i in links:
                i.url = re.sub(frm, to, i.url)
                new_links.append(i)
            return new_links

        return _sub

    def make_headers(self, headers):
        headers = CaselessDict(headers)
        if 'user-agent' in headers:
            self.user_agent = headers.pop('user-agent')
        self.cookies = self.make_cookies(headers.pop('cookies', {}))
        self.headers = headers

    def make_cookies(self, cookies):
        if type(cookies) == str:
            cookies = cookies.encode('utf-8')
        if type(cookies)==str:
            cookies = {i.key:i.value for i in list(http.cookies.SimpleCookie(cookies).values())}
        elif type(cookies)==dict:
            cookies = cookies
        else:
            cookies = {}
        return cookies

    def make_page_extractor(self, obj):
        if type(obj)!=dict:
            return
        pages = obj.get('pages')
        if pages:
            regex = self.macro.expand(pages.get('regex'))
            css = self.macro.expand(pages.get('css'))
            if css:
                xpath = self.tr.css_to_xpath(css)
            else:
                xpath = self.macro.expand(pages.get('xpath'))
            self.page_extractor = SgmlLinkExtractor(
                                        allow=regex,
                                        restrict_xpaths=xpath,
                                        process_value=utils.first_n_pages(regex, pages))


