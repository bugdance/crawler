#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from scrapy import log
from scrapy.utils.url import canonicalize_url
from scrapy.utils.markup import remove_tags
from scrapy.contrib.loader.processor import Compose, Join, TakeFirst
from scrapy.exceptions import CloseSpider
from chardet import detect
from urllib.parse import urlencode
from urllib.request import urlopen
from datetime import datetime, timedelta
from html.parser import HTMLParser
from lxml import etree, html
from lxml.html.clean import Cleaner
import os.path, codecs, re, json, jsonpath_rw, string, base64, time, hashlib, imp, tempfile, zlib

try:
    from pickle import pickle
except ImportError:
    import pickle

try:
    from termcolor import colored
except ImportError:
    def colored(text, color=None, on_color=None, attrs=None): return text

def R(x): return colored(x, 'red',    attrs=['bold'])
def G(x): return colored(x, 'green',  attrs=['dark', 'bold'])
def B(x): return colored(x, 'blue',   attrs=['bold'])
def Y(x): return colored(x, 'yellow', attrs=['dark', 'bold'])

def RR(x): return colored(x, 'white', 'on_red',    attrs=['bold'])
def GG(x): return colored(x, 'white', 'on_green',  attrs=['dark', 'bold'])
def BB(x): return colored(x, 'white', 'on_blue',   attrs=['bold'])
def YY(x): return colored(x, 'white', 'on_yellow', attrs=['dark', 'bold'])

def help():
    msg = 'If you want a thing done well, do it yourself!'
    msg = 'Simplicity is the ultimate sophistication!'
    log.msg(R(''.join([chr(0xfee0+ord(i)) if i.isalnum() else i for i in msg])))

def connect_uri(uri):

    if uri.startswith('mongodb://'):
        import pymongo
        parsed = pymongo.uri_parser.parse_uri(uri)
        database = parsed['database']
        collection = parsed['collection']
        host, port = parsed['nodelist'][0]

        cnn = pymongo.MongoClient(host=host, port=port)
        db = cnn[database]
        tbl = db[collection]

    elif uri.startswith('mysql://'):
        try:
            import mysql.connector as pymysql
        except ImportError:
            import pymysql
        parsed = urlparse.urlparse(uri)
        host = parsed.hostname
        port = parsed.port
        user = parsed.username
        passwd = parsed.password

        db, tbl = parsed.path.strip('/').split('.')
        cnn = pymysql.connect(
                                host=host,
                                port=port,
                                user=user,
                                passwd=passwd,
                                db=db,
                                charset='utf8'
                             )



    else:
        raise Exception('unknow uri <{}>'.format(uri))

    return (cnn, db, tbl)

def hash_url(url):
    url = canonicalize_url(url)
    sha1 = hashlib.sha1()
    sha1.update(url)
    return sha1.hexdigest()

def to_unicode(txt):
    if type(txt)==str:
        return txt
    elif type(txt)==str:
        enc = 'gbk' if detect(txt[:2048])['encoding'].lower()=='gb2312' else 'utf-8'
        return txt.decode(enc)
    else:
        return ''

def load_file(path):
    if os.path.exists(path):
        path = os.path.abspath(path)
        path = 'file://'+path
    try:
        txt = urlopen(path, timeout=10).read()
        txt = to_unicode(txt)
    except Exception as ex:
        log.msg('cannot load file <{}>'.format(path.decode('utf-8')), level=log.ERROR)
        txt = ''
    return txt

def load_cfg(path):
    cfg = json.loads(load_file(path))
    if 'base' in cfg:
        cfg = dict(list(load_cfg(cfg['base']).items())+list(cfg.items()))
        del cfg['base']
    return cfg


def generate_urls(obj, macro):
    try:
        if type(obj)==list:
            for url in obj:
                yield macro.expand(url)

        elif type(obj)==dict:
            base = macro.expand(obj['base'].encode('utf-8'))
            us = urlparse.urlsplit(base)
            qstr = dict(urlparse.parse_qsl(us.query))
            qstr.update(obj.get('qstr', {}))
            base = urlparse.urlunsplit(us._replace(query=''))

            for k,v in qstr.items():
                if type(v)==dict and type(v['val'])==str:
                    v = v['val'].encode(v.get('enc', 'utf-8'), errors='ignore')
                qstr[k] = macro.expand(v)

            if 'keywords' in obj:
                kw_obj = obj['keywords']
                for kw in load_keywords(kw_obj):
                    key = kw_obj['name'].encode('utf-8')
                    val = kw.encode(kw_obj.get('enc', 'utf-8'), errors='ignore') if type(kw)==str else str(kw)
                    if kw_obj.get('query', True):
                        qstr.update({key:val})
                        url = base+'?'+urlencode(qstr)
                    else:
                        url = base.replace(key, val)+'?'+urlencode(qstr)
                    yield url
            else:
                url = base+'?'+urlencode(qstr)
                yield url

    except Exception as ex:
        log.msg('cannot generate urls: {}'.format(ex), level=log.ERROR)
        raise CloseSpider()

def load_keywords(kw_obj, msg='keywords'):
    keywords = set()

    if type(kw_obj)==dict:
        path = kw_obj.get('file')

        if path:
            for line in load_file(kw_obj['file']).splitlines():
                kw = line.strip()
                if kw and not kw.startswith('#'):
                    keywords.add(kw)

        for kw in kw_obj.get('list', []):
            keywords.add(kw)

        sub = kw_obj.get('sub')

        if sub:
            frm = sub.get('from')
            to = sub.get('to')
            keywords = {re.sub(frm, to, kw) for kw in keywords}

        log.msg('load {} from <{}>({})'.format(msg, path, len(keywords)))

    return keywords

def convert_type(infs):
    def _wrapper(inf, t):
        def _convert(data):
            if t not in ['join', 'list'] and isinstance(data, list):
                data = TakeFirst()(data)
                if type(data) in [str, str]:
                    data = data.strip()
                elif type(data) in [int, float, datetime]:
                    data = str(data)
                else:
                    return data

            if t=='join':
                sep = inf.get('sep', ' ')
                return Join(sep)(data)
            elif t=='list':
                sep = inf.get('sep', ' ')
                return remove_tags(Join(sep)(data)).strip()
            elif t=='text':
                return remove_tags(data).strip()
            elif t=='clean':
                cleaner = Cleaner(style=True, scripts=True, javascript=True, links=True, meta=True)
                return cleaner.clean_html(data)
            elif t=='unesc':
                return HTMLParser().unescape(data)
            elif t=='base64':
                return base64.decodestring(data)
            elif t=='sub':
                frm = inf.get('from')
                to = inf.get('to')
                return re.sub(frm, to, data)
            elif t=='xpath':
                qs = inf.get('query')
                dom = html.fromstring(data)
                return dom.xpath(qs)
            elif t=='map':
                m = inf.get('map')
                d = inf.get('default')
                return m.get(data, d)
            elif t=='int':
                data = data.replace(',', '')
                data = re.search(r'[0-9]+', data).group(0)
                return int(data)
            elif t=='float':
                data = data.replace(',', '')
                data = re.search(r'[.0-9]+', data).group(0)
                return float(data)
            elif t=='date':
                fmt = inf.get('fmt', 'auto')
                tz = inf.get('tz', '+00:00')
                return parse_date(data, fmt, tz)
            elif t=='cst':
                fmt = inf.get('fmt', 'auto')
                return parse_date(data, fmt, '+08:00')
            elif t=='http':
                import requests
                url = data
                m = inf.get('method', 'get').upper()
                d = inf.get('data', {})
                e = inf.get('enc', 'utf-8')
                if m=='GET':
                    return requests.get(url).content.decode(e)
                elif m=='POST':
                    return requests.get(url, data=d).content.decode(e)
                else:
                    return data
            else:
                return data
        return _convert

    infs = infs if type(infs)==list else [infs]
    return Compose(*[_wrapper(inf, inf.get('type', 'str')) for inf in infs])


class MacroExpander(object):

    def __init__(self, env):
        self.macros = dict()
        self.macros.update(env)

    def update(self, env={}):
        now = datetime.now().replace(microsecond=0)
        utcnow = datetime.utcnow().replace(microsecond=0)
        self.macros.update({
                'UTCNOW':   utcnow.strftime('%Y-%m-%d %H:%M:%S'),
                'NOW':      now.strftime('%Y-%m-%d %H:%M:%S'),
                'TODAY':    now.strftime('%Y-%m-%d'),
                'ITODAY':   '{}-{}-{}'.format(now.year, now.month, now.day),

                'YEAR':     now.strftime('%Y'),
                'MONTH':    now.strftime('%m'),
                'DAY':      now.strftime('%d'),
                'HOUR':     now.strftime('%H'),
                'MINUTE':   now.strftime('%M'),
                'SECOND':   now.strftime('%S'),

                'IYEAR':    str(now.year),
                'IMONTH':   str(now.month),
                'IDAY':     str(now.day),
                'IHOUR':    str(now.hour),
                'IMINUTE':  str(now.minute),
                'ISECOND':  str(now.second),

                'UNOW':     str(int(time.time())),
                'UTODAY':   str(int(time.mktime(time.strptime(now.strftime('%Y-%m-%d'), '%Y-%m-%d')))),
                'UENDDAY':  str(int(time.mktime(time.strptime(now.strftime('%Y-%m-%d 23:59:59'), '%Y-%m-%d %H:%M:%S'))))
        })
        self.macros.update(env)

    def expand(self, value):
        if type(value)!=str and type(value)!=str:
            return value
        template = string.Template(value)
        self.update()
        return template.safe_substitute(self.macros)


def tz_offset(tz):
    res = (re.search(r'(?P<F>[-+])(?P<H>\d{2}):?(?P<M>\d{2})', tz) or re.search('', '')).groupdict()
    offset = (1 if res.get('F', '+')=='+' else -1) * timedelta(
                        hours   = int(res.get('H', 0)),
                        minutes = int(res.get('M', 0)))
    return offset

def parse_date(data, fmt, tz):
    offset = tz_offset(tz)

    if fmt=='auto':
        now = datetime.utcnow().replace(microsecond=0)+offset
        now_1 = now-timedelta(days=1)
        now_2 = now-timedelta(days=2)

        # ???/???/??????/??????/??????
        x = data.strip()
        x = x.replace('\xa0', ' ')
        x = x.replace('???', ' 0 ')
        x = re.sub(r'???[??????]', now.strftime(' %Y-%m-%d %H:%M:%S '), x)
        x = re.sub(r'???[??????]', now.strftime(' %Y-%m-%d '), x)
        x = re.sub(r'???[??????]', now_1.strftime(' %Y-%m-%d '), x)
        x = re.sub(r'???[??????]', now_2.strftime(' %Y-%m-%d '), x)
        x = re.sub(r'[??????]',  '/', x)
        x = re.sub(r'[???]',    ' ', x)
        x = re.sub(r'???\s*[??????]???',  '12?????????', x)
        x = re.sub(r'???\s*??????????','30?????????', x)
        x = re.sub(r'???\s*?????????','30?????????', x)
        x = re.sub(r'\s{2,}', r' ', x)

        # XX???
        res = ( re.search(r'(?P<S>\d+)\s*??????????', x) \
             or re.search(r'(?P<M>\d+)\s*?????????', x) \
             or re.search(r'(?P<H>\d+)\s*??????????', x) \
             or re.search(r'(?P<d>\d+)\s*[??????]???', x) \
             or re.search('', '')).groupdict()

        if res:
            dt = now - timedelta(
                                days    = int(res.get('d', 0)),
                                hours   = int(res.get('H', 0)),
                                minutes = int(res.get('M', 0)),
                                seconds = int(res.get('S', 0))
                              )
        else:
            # XX-XX-XX XX:XX:XX
            res = ( re.search(r'(?P<Y>\d+)[/-](?P<m>\d+)[/-](?P<d>\d+)(\s+(?P<H>\d{2}):(?P<M>\d{2})(:(?P<S>\d{2}))?)?', x) \
                 or re.search('', '')).groupdict()

            if res:
                Y = res.get('Y', now.year)
                m = res.get('m', now.month)
                d = res.get('d', now.day)
                H = res.get('H', now.hour)
                M = res.get('M', now.minute)
                S = res.get('S', 0)

                dt = datetime(
                            year   = int(Y) if Y!=None else now.year,
                            month  = int(m) if m!=None else now.month,
                            day    = int(d) if d!=None else now.day,
                            hour   = int(H) if H!=None else now.hour,
                            minute = int(M) if M!=None else now.minute,
                            second = int(S) if S!=None else 0
                        )
            else:
                # 1970-01-01 00:00:00
                dt = datetime.utcfromtimestamp(0)+offset

    # UNIX TIMESTAMP
    elif fmt=='unix':
        dt = datetime.utcfromtimestamp(int(data))
        offset = timedelta(0)
    else:
        dt = datetime.strptime(str(data).encode('utf-8'), str(fmt).encode('utf-8'))

    return dt-offset

def first_n_pages(pattern, pages):
    if not pages:
        return None

    start = pages.get('start', 1)
    stop = pages.get('stop', 5)
    group = pages.get('group', 1)
    enc = pages.get('enc')

    def _filter(url):
        m = re.search(pattern, url)
        if m and start<=int(m.group(group))<stop:
            if enc:
                return urlparse.unquote(url).decode('utf-8').encode(enc)
            else:
                return url
        return None

    return _filter

def filter_data(query, data):
    for k,v in query.items():
        if k=='delta':
            now = datetime.utcnow()
            if not (type(data)==datetime and (now-data).total_seconds()<v):
                return False
        elif k=='match':
            if not (type(data) in [str, str] and re.match(v, data)):
                return False
        elif k=='min':
            if data<v:
                return False
        elif k=='max':
            if data>v:
                return False
        else:
            log.msg('invalid query <{}>'.format(query), level=log.WARNING)
            return False
    return True

def get_ipaddr(ifname):
    try:
        import socket, fcntl, struct
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
    except Exception as ex:
        return '0.0.0.0'

def register_xpath_functions():

    def get_text(es):
        if type(es)==list:
            if len(es)>0:
                e = es[0]
            else:
                return False, None
        else:
            e = es

        if type(e)==etree._Element:
            txt = etree.tostring(e, method='text', encoding=str)
        elif type(e) in [str, str, etree._ElementStringResult, etree._ElementUnicodeResult]:
            txt = e
        else:
            return False, None

        return True, txt

    def datetime_delta(ctx, es, tz, delta):
        ok, txt = get_text(es)
        if ok:
            now = datetime.utcnow()
            dt = parse_date(txt, 'auto', tz)
            return (now-dt).total_seconds() < delta
        else:
            return False

    def unixtime_delta(ctx, es, delta):
        ok, txt = get_text(es)
        if ok:
            now = time.time()
            dt = float(txt)
            return now-dt < delta
        else:
            return False

    ns = etree.FunctionNamespace(None)
    ns['datetime-delta'] = datetime_delta
    ns['unixtime-delta'] = unixtime_delta

def register_xpath_namespaces():
    fns = {
            'date':'http://exslt.org/dates-and-times',
            'dyn':'http://exslt.org/dynamic',
            'exsl':'http://exslt.org/common',
            'func':'http://exslt.org/functions',
            'math':'http://exslt.org/math',
            'random':'http://exslt.org/random',
            're':'http://exslt.org/regular-expressions',
            'set':'http://exslt.org/sets',
            'str':'http://exslt.org/strings'
    }
    for k,v in fns.items():
        etree.FunctionNamespace(v).prefix = k

register_xpath_functions()
register_xpath_namespaces()

