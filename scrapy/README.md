用户手册
==============

## 爬虫列表

- example(通用型)



## scrapy入门

- test:

        $ scrapy crawl <spider>
        
- deploy:

        $ scrapy deploy <project>
        
- schedule:

        $ curl http://yourdomain:6800/schedule.json -d project=<project> -d spider=<spider> -d config=</path/to/spider.conf> -d setting=DOWNLOAD_DELAY=1
        
- cancel:

        $ curl http://yourdomain:6800/cancel.json   -d project=<project> -d job=xxxxxxxxxxx
        
- listjobs:

        $ curl http://yourdomain:6800/listjobs.json -d project=<project>




配置文件语法
============



## site

**站点名称**, 值类型为`string`, 默认值为`"未知站点"`. 例如:

    "天涯论坛"

站点名称, 需要简明扼要, 并且能够精确描述本配置文件的用途.

## domains

**站点域名**, 值类型为`list`, 默认值为`[]`(即, 空数组). 例如:

    ["bj.news.site.com", "sh.news.site.com"]

爬虫在提取页面中链接时, 会自动忽略除此之外的域名. 例如, 上述配置会忽略下述链接:

    "http://tj.news.site.com"
    "http://www.ads.com"

## urls

**入口链接**, 值类型为`list`或`dict`, 默认值为`[]`(即, 空数组). 例如:

    [
        "http://www.site.com/?rn=10&cate=%B5%D8%C7%F8&city=北京",
        "http://www.site.com/?rn=10&cate=%B5%D8%C7%F8&city=上海",
        "http://www.site.com/?rn=10&cate=%B5%D8%C7%F8&city=广州",
        "http://www.site.com/?rn=10&cate=%B5%D8%C7%F8&city=重庆",
        "http://www.site.com/?rn=10&cate=%B5%D8%C7%F8&city=天津"
    ]

当这些链接具有共同特征时, 可以使用规则自动生成. 例如:

    {
        "base": "http://www.site.com/?rn=10",
        "qstr": {
            "type": 1,
            "cate": {"val":"地区", "enc":"gbk"}
        },
        "keywords": {
            "name": "city",
            "file": "http://www.mysite.com/cities.txt",
            "list": ["北京", "上海"],
            "enc" : "utf-8"
        },
        "method": "GET"
    }

- `base`: 基础链接(可以含有查询字段), 值类型为`string`.
- `qstr`: 链接的查询部分, 值类型为`dict`. 用来描述固定查询字段.
- `keywords`: 关键词, 值类型为`dict`. 用来描述动态查询字段.

    * `name`: 关键词名称, 值类型为`string`, 不能为空.
    * `file`: 文件名称, 值类型为`string`. 可以使用本地或网络路径, 编码方式必须是`UTF-8`.

            # http://www.mysite.com/cities.txt
            广州
            重庆
            天津

    * `list`: 关键词列表, 值类型为`list`, 默认值为`[]`.
    * `enc`: 编码方式, 值类型为`string`, 默认值为`utf-8`. 可以对关键词进行编码.
    * `query`: 是否属于查询字段, 默认值为`true`. 当其值为`false`时, 会对基础链接进行替换.

            {
                "base": "http://www.site.com/FORUM/index.html",
                "keywords": {
                    "name" : "FORUM",
                    "list" : ["news", "blog", "about"],
                    "query": false
                }
            }
            
            上述配置可以生成下述链接
            
            http://www.site.com/news/index.html
            http://www.site.com/blog/index.html
            http://www.site.com/about/index.html

- `pages`: 自动翻页(当且仅当`rules`为空时, 该配置才有效). 例如:

        {
            "xpath" : "//div[@id='page']",
            "regex" : "&(pn)=([0-9]+)",
            "start" : 1,
            "stop"  : 5,
            "group" : 2
        }

- `method`: HTTP请求方法, 值类型为`string`, 默认值为`GET`. 当其值为`POST`时, 可以模拟表单提交.
- `headers`: HTTP请求头, 值类型为`dict`, 默认值为`{}`. 不区分键的大小写. 例如:

        {
            "User-Agent": "webbot++(by kev++)",
            "Cookie": "hello=world; foo=bar"
        }

## rules

**链接规则集**, 值类型为`dict`, 默认值为`{}`(即, 空字典). 用来提取页面中满足条件的链接. 例如:

    {
        "#1": {
            "follow": true,
            "regex" : "/f\\?kw=",
            "xpath" : "//div[@class='sub_dir_box']"
        },
        "#2": {
            "follow": true,
            "regex" : "/f/fdir.*&pn=([0-9]+)",
            "xpath" : "//div[@class='pagination']/a[last()-1]",
            "pages" : {"start":1, "stop":5}
        },
        "#3": {
            "follow": true,
            "regex" : "&pn=([0-9]+)",
            "xpath" : "//div[@id='frs_list_pager']/a[@class='next']",
            "pages" : {"start":0, "stop":250}
        },
        "#4": {
            "follow": false,
            "regex" : "/p/[0-9]+",
            "xpath" : "//ul[@id='thread_list']//a[@class='j_th_tit']"
        }
    }

> 注意: 当`rules`为空时, 会直接下载`urls`中的所有链接, 也会按`keywords.pages`中的规则进行翻页, 并且按`fields`中的规则对页面进行解析.

**链接规则集** 是由**链接规则项**构成的. 其中， `#1`, `#2` ... `#4`为**规则项**序号(名称), 需要注意的是:

- 规则名称可以是任何不重复的字符串
- 这些规则不存在先后次序
- 它们会在每个页面中起作用
- 一个页面可能会同时匹配多条规则

**规则项**的值类型为`dict`, 由下列元素组成:

- `follow`, 是否跟踪链接, 值类型为`bool`或`null`, 默认值为`true`.
    * 当其值为`true`时, 表示: 仅follow, 不parse
    * 当其值为`false`时, 表示: 不follow, 仅parse
    * 当其值为`null`时, 表示: 既follow, 又parse
    * 若**规则集**不为空时, 至少要有一条**规则项**的`follow`设为`false`或`null`
- `regex`, 链接需要匹配的regex, 值类型为`string`, 默认值为`null`.
- `xpath`, 链接需要匹配的xpath, 值类型为`string`, 默认值为`null`. 在xpath中可以使用下列扩展函数:
    * datetime-delta(dt, tz, delta)
    * unixtime-delta(dt, delta)
- `sub`, 链接转换, 值类型为`dict`, 默认值为`null`. (先于`pages`执行)
    * `from`, 原始地址(转换前), 值类型为`string`, 不能为空.
    * `to`, 目标地址(转换后), 值类型为`string`, 不能为空.
- `pages`, 提取链接中的页码(数字), 判断是否在范围之内, 值类型为`dict`, 默认值为`null`. (需要同时设置上述的`regex`)
    * `start`, 起始页码(包含), 值类型为`int`, 默认值为`1`.
    * `stop`, 终止页面(不包含), 值类型为`int`, 默认值为`5`.
    * `group`, 需要提取的`regex`分组编号, 值类型为`int`, 默认值为`1`.

> 注意: `regex`, `xpath`, `pages`都是用来对链接进行过滤的, 需要同时满足.

## loop

**循环表达式**, 值类型为`string`, 默认值为`(//*)[1]`(即, root元素). 用该XPATH表达式来循环提取页面中多条信息. 例如:

    "loop": "//table/tr"

若`loop`值以`css:`为前缀, 则使用`css`选择器. 例如:

    "loop": "css:table tr"

## fields

**字段定义**, 值类型为`dict`, 默认值为`{}`. 例如:

    {                                                                                     
        "url"     : {"name": "url",         "value": "${URL}"},
        "title"   : {"name": "title",       "xpath": "//h1[@id='title']/text()", "default": "未知标题"},
        "date"    : {"name": "ctime",       "xpath": "//div[contains(@class, 'l_post')][1]/@data-field", "parse": [{"type":"jpath", "query":"$.content.date"}, {"type":"cst"}]},
        "updated" : {"name": "gtime",       "value": "${NOW}", "parse": {"type": "date", "tz": "+08:00"}},
        "content" : {"name": "content",     "xpath": "//div[@class='d_post_content']", "parse": {"type":"text"}},
        "clicks"  : {"name": "visitCount",  "value": 0},
        "category": {"name": "info_flag",   "value": "02"}
    }

上述对字段的定义, 可以提取网页中的下述信息:

     category : 02
      updated : 2013-04-23 15:15:09
          url : http://news.qq.com/a/20130423/000484.htm
        title : 俄海军重型巡洋舰“瓦良格”号将远航访问亚太
      content : 中新社莫斯科4月22日电 (记者 贾靖峰)俄罗斯海军太平洋舰...
         date : 2013-04-23 01:06:00
       clicks : 0

**字段定义集**, 是由多个 **字段定义项**组成. 每个**字段定义项**由`字段名称`(值类型为`string`)和`字段定义`(值类型为`dict`)组成.
其中, `字段定义`由下列元素组成:

- `name`, 数据库字段名称
    * 若无该字段, 则不会写入数据库, 并在**debug**模式下, 会在名称后打印`*`标识.
- `value`, 固定值, 取值范围为:
    * 整数
    * 浮点数
    * 字符串
- `xpath`, xpath表达式
- `default`, 默认值, 取值范围于`value`相同. 若`value`及`xpath`提取数据为空, 则使用该默认值.
- `regex`, regex表达式(先于`parse`执行)
- `parse`, 数据解析, 值类型为`dict`或`list`(由`dict`组成), 默认值为`{}`.
    * 当值类型为`dict`时:
        - `type`, 解析类型, 值类型为`string`, 默认值为`str`. (取值范围为下述10+种之一):
            * `str`, 文本
            * `text`, 文本(自动去除tag)
            * `unesc`, HTML实体转义

                    # "hello&amp;world" => "hello&world"
                    {"type":"unesc"}

            * `clean`, 清理HTML(自动去除style/script/meta/links等)
            * `sub`, 字符替换
                - `from`, 替换前
                - `to`, 替换后

                        # "hello - world"  => "world - hello"
                        {"type":"sub", "from":"(.*) - (.*)", "to":"\\g<2> - \\g<1>"}

            * `int`, 整数, 提取字符串中出现的数字, 并且转化成整数
            * `float`, 浮点数, 提取字符串中出现的数字及小数点, 并且转化成浮点数
            * `join`, 拼接
                - `sep`, 分隔符, 值类型为`string`, 默认值为`" "`(即, 空格).
            * `list`, 拼接(自动去除tag)
                - `sep`, 分隔符, 值类型为`string`, 默认值为`" "`(即, 空格).
            * `date`, 日期
                - `fmt`, 日期格式, 值类型为`string`, 默认值为`auto`. 可自动识别下列日期格式:
                    * 刚刚
                    * 几秒前
                    * 半分钟前
                    * 半小时前
                    * 半天前
                    * 8秒前
                    * 8 分钟前
                    * 8小时前
                    * 8 天前
                    * 今天 12:12
                    * 昨日 12:12
                    * 前天 12:12
                    * 2013年3月5日 18:30
                    * 2013年03月05日 18:30
                    * 2013-03-05 18:30
                    * 2013-3-5 18:30:00
                    * ...
                - `tz`, 时区, 值类型为`string`, 默认值为`+00:00`(即, UTC时间). 注意: 当涉及到相对时间计算时, 需要指定`tz`.
            * `cst`, CST(China Standard Time)日期 (`{"type":"cst"}`等价于`{"type:"date", "tz":"+08:00"}`), 为中国大陆用户量身定做
                - `fmt`, 日期格式, 值类型为`string`, 默认值为`auto`.
            * `continue`, 继续解析. 解析结果必须是个url, 自动下载该url, 并继续解析:

                    {
                        "fields": {
                            "url": {"name":"url",       "value":"${URL}"},
                            "txt": {"name":"content",   "xpath":"//iframe[@id='content']/@src", "parse":{"type":"continue"}}
                        },

                        "continue": {
                            "fields": {
                                "txt": {"name":"content",   "xpath":"//div[@class='content']", "parse":{"type":"text"}}
                            }
                        }
                    }

    * 当值类型为`list`时, 会按先后顺序, 依次进行数据变换. 



另外, **rules** 以及 **fields** 中的`value`及`xpath`中可以嵌入变量(形如, `${VARNAME}`), 目前支持下列变量:

    'UTCNOW':   utcnow.strftime('%Y-%m-%d %H:%M:%S'),
    'NOW':      now.strftime('%Y-%m-%d %H:%M:%S'),
    'TODAY':    now.strftime('%Y-%m-%d'),
    'ITODAY':   '%d-%d-%d'.format(now.year, now.month, now.day)

    'YEAR':     now.strftime('%Y'),
    'MONTH':    now.strftime('%m'),
    'DAY':      now.strftime('%d'),
    'HOUR':     now.strftime('%H'),
    'MINUTE':   now.strftime('%M'),
    'SECOND':   now.strftime('%S'),

    'IMONTH':   str(now.month),
    'IDAY':     str(now.day),
    'IHOUR':    str(now.hour),
    'IMINUTE':  str(now.minute),
    'ISECOND':  str(now.second),

    'UNOW':     str(int(time.time())),
    'UTODAY':   str(int(time.mktime(time.strptime(now.strftime('%Y-%m-%d'), '%Y-%m-%d')))),
    'UENDDAY':  str(int(time.mktime(time.strptime(now.strftime('%Y-%m-%d 23:59:59'), '%Y-%m-%d %H:%M:%S'))))
    
    'SITE':     站点名称, 于`site`值一致
    'CONF':     配置文件内容
    'URL':      本页面链接(仅用于**fields** 字段定义, 不可在**rules**中使用)

## proxy

**代理设置**, 值类型为`dict`. 例如:

    {
        "enabled" : true,
        "rate"    : 5,
        "file"    : "http://192.168.3.155/proxy.txt",
        "list"    : [
                      "http://1.2.3.4:5678",
                      "http://8.7.6.5:4321"
                    ]
    }

由下列元素组成:

- `enabled`, 是否生效, 值类型为`bool`, 默认值为`true`.
- `rate`, 代理变化频率, 值类型为`int`, 默认值为`10`(表示: 每10次HTTP请求, 就随机切换代理).
- `file`, 代理列表文件, 值类型为`string`, 可以使用本地或网络路径, 编码方式必须是`UTF-8`.

        # 由3个字段组成(prot/host/port), 它们之间用空白符(如, `tab`)分隔
        http    218.29.218.10   6666
        http    122.96.59.103   80
        http    61.136.93.38    8080

- `list`, 固定代理列表, 值类型为`list`, 默认值为`[]`, 由形如`prot://host:port`的代理地址组成:
    * `prot`, 协议类型, 如`http`, `https`, `socks5`, `socks4`等(只支持`http`)
    * `host`, 主机名(或IP地址)
    * `port`, 端口号

## debug

**调试模式**, 值类型为`bool`, 默认值为`false`. 当值为`true`时, 程序运行过程中, 会把采集到的item详情输出到屏幕.

## settings

**全局设置**, 值类型为`dict`, 默认值为`{}`. 控制爬虫特定行为. 例如:

    {
        "user_agent": "Mozilla 5.0 (webbot by Kev++)",
        "download_timeout": 30,
        "download_delay": 5,
        "mysql": "mysql://user:passwd@hostname/db_name.table_name"
    }
    
    - `user_agent`, 浏览器型号
    - `download_timeout`, 下载超时, 默认值为`30`(单位:秒)
    - `download_delay`, 两次下载之间的延时, 默认值为`0`(单位:秒)
    - `mysql`, MySQL入库设置, 例如: `mysql://user:passwd@hostname:3306/db_name.table_name`
    - `mongo`, MongoDB入库设置, 例如: `mongodb://hostname:27017/db_name.collection_name`






## 配置软件

    # 配置scrapyd
    $ sudo vi /etc/scrapyd/conf.d/000-default

        [scrapyd]
        http_port  = 6800
        debug      = off
        eggs_dir   = /var/lib/scrapyd/eggs
        dbs_dir    = /var/lib/scrapyd/dbs
        items_dir  =
        logs_dir   = /var/log/scrapyd
        jobs_to_keep = 20000
        poll_interval = 5
        max_proc_per_cpu = 5

    $ sudo service scrapyd restart

    # 配置mongodb
    $ sudo vi /etc/mongodb.conf

        bind_ip = 0.0.0.0

    $ sudo service mongodb restart

## 目录结构

  
    
    configs/
    ├── README.md
    ├── log
    │   ├── example
    │   │   ├── index.html
    │   │   ├── config.html
    │   │   └── task.html
    │   └── twistd
    │       ├── twistd.log
    │       ├── twistd.log.1
    │       └── twistd.log.2
    ├── keywords
    │   ├── b1.dic
    │   ├── b2.dic
    │   └── b3.dic
    ├── bbs
    │   ├── abc_bbs.conf
    │   ├── def_bbs.conf
    │   └── ghi_bbs.conf
    ├── blog
    │   ├── abc_blog.conf
    │   ├── def_blog.conf
    │   └── ghi_blog.conf
    ├── mblog
    │   ├── abc_mblog.conf
    │   ├── def_mblog.conf
    │   └── ghi_mblog.conf
    └── news
        ├── abc_news.conf
        ├── def_news.conf
        └── ghi_news.conf

## 命名规则

        域名            配置名
    ------------    ------------
    bbs.abc.com     abc_bbc.conf
    blog.def.org    def_blog.conf
    news.ghi.net    ghi_news.conf



## 计划任务

    $ crontab -e

    # m h  dom mon dow   command
    ################################## NEWS ########################################
    15 */1 * * * curl http://192.168.3.154:6800/schedule.json -d project=example -d spider=example -d setting=CLOSESPIDER_TIMEOUT=3600 -d config=http://192.168.3.155/news/abc_news.conf
    ################################## BLOG ########################################
    15 */7 * * * curl http://192.168.3.154:6800/schedule.json -d project=example -d spider=example -d setting=CLOSESPIDER_TIMEOUT=3600 -d config=http://192.168.3.155/news/abc_blog.conf
    ################################## BBS ########################################
    15 */3 * * * curl http://192.168.3.154:6800/schedule.json -d project=example -d spider=example -d setting=CLOSESPIDER_TIMEOUT=3600 -d config=http://192.168.3.155/news/abc_bbs.conf
    ################################## MBLOG ########################################
    15 */2 * * * curl http://192.168.3.154:6800/schedule.json -d project=example -d spider=example -d setting=CLOSESPIDER_TIMEOUT=3600 -d config=http://192.168.3.155/news/abc_mblog.conf

