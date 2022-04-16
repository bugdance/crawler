### 数据库字段说明

> 1.数据性质:快运企业  
> 表名:data_1688_companies  索引:corp_code
 
| 中文名称 | 字段名       | 数据类型     | 主键  | 非空  | 外健  |
| -------- | ------------ | ------------ | ----- | ----- | ----- |
| ID       | ID           | int(11)      | TRUE  | TRUE  | FALSE |
| 公司ID   | corp_code    | varchar(50)  | FALSE | FALSE | FALSE |
| 公司名称 | corp_name    | varchar(250) | FALSE | FALSE | FALSE |
| 线路条数 | route_num    | int(11)      | FALSE | FALSE | FALSE |
| 网点数目 | node_num     | int(11)      | FALSE | FALSE | FALSE |
| 公司电话 | corp_tel     | varchar(100) | FALSE | FALSE | FALSE |
| 公司传真 | corp_fax     | varchar(100) | FALSE | FALSE | FALSE |
| 公司模式 | corp_model   | varchar(100) | FALSE | FALSE | FALSE |
| 公司信息 | corp_info    | longtext     | FALSE | FALSE | FALSE |
| 公司地址 | corp_address | varchar(250) | FALSE | FALSE | FALSE |
| 公司网站 | corp_url     | varchar(250) | FALSE | FALSE | FALSE |
| 页面地址 | url          | varchar(250) | FALSE | FALSE | FALSE |

> 2.数据性质:快运网点
> 表名:data_1688_nodes   索引:corp_code,node_name,node_address

| 中文名称 | 字段名       | 数据类型     | 主键  | 非空  | 外健  |
| -------- | ------------ | ------------ | ----- | ----- | ----- |
| ID       | ID           | int(11)      | TRUE  | TRUE  | FALSE |
| 公司ID   | corp_code    | varchar(50)  | FALSE | FALSE | FALSE |
| 网点名称 | node_name    | varchar(50)  | FALSE | FALSE | FALSE |
| 网点地址 | node_address | varchar(200) | FALSE | FALSE | FALSE |
| 网点电话 | phone        | varchar(250) | FALSE | FALSE | FALSE |
| 业务范围 | business     | varchar(250) | FALSE | FALSE | FALSE |
| 页面地址 | url          | varchar(250) | FALSE | FALSE | FALSE |

> 3.数据性质:快运线路
> 表名:data_1688_routes  索引:corp_code,departure,arrive,type,route_time

| 中文名称 | 字段名         | 数据类型     | 主键  | 非空  | 外健  |
| -------- | -------------- | ------------ | ----- | ----- | ----- |
| ID       | ID             | int(11)      | TRUE  | TRUE  | FALSE |
| 公司ID   | corp_code      | varchar(50)  | FALSE | FALSE | FALSE |
| 出发地   | departure      | varchar(100) | FALSE | FALSE | FALSE |
| 到达地   | arrive         | varchar(100) | FALSE | FALSE | FALSE |
| 运输类型 | type           | varchar(20)  | FALSE | FALSE | FALSE |
| 有效时间 | route_time     | varchar(20)  | FALSE | FALSE | FALSE |
| 重货普通 | heavy_normal   | double(11,2) | FALSE | FALSE | FALSE |
| 重货打折 | heavy_discount | double(11,2) | FALSE | FALSE | FALSE |
| 重货单位 | heavy_unit     | varchar(20)  | FALSE | FALSE | FALSE |
| 轻货普通 | low_normal     | double(11,2) | FALSE | FALSE | FALSE |
| 轻货打折 | low_discount   | double(11,2) | FALSE | FALSE | FALSE |
| 轻货单位 | low_unit       | varchar(20)  | FALSE | FALSE | FALSE |
| 最低一票 | lowest         | varchar(50)  | FALSE | FALSE | FALSE |
| 页面地址 | url            | varchar(250) | FALSE | FALSE | FALSE |

> 4.数据性质:物流人才，大数据人才，电商人才
> 表名:data_logistics_jobs   索引:url,release_time
> 同表:data_bigdata_jobs, data_ecommerce_jobs

| 中文名称 | 字段名           | 数据类型     | 主键  | 非空  | 外健  |
| -------- | ---------------- | ------------ | ----- | ----- | ----- |
| ID       | ID               | int(11)      | TRUE  | TRUE  | FALSE |
| 职位名称 | job_title        | varchar(100) | FALSE | FALSE | FALSE |
| 公司名称 | company_name     | varchar(100) | FALSE | FALSE | FALSE |
| 公司性质 | company_nature   | varchar(50)  | FALSE | FALSE | FALSE |
| 公司行业 | company_industry | varchar(50)  | FALSE | FALSE | FALSE |
| 搜索词   | search_word      | varchar(50)  | FALSE | FALSE | FALSE |
| 搜索职位 | search_category  | varchar(50)  | FALSE | FALSE | FALSE |
| 工作职位 | job_category     | varchar(50)  | FALSE | FALSE | FALSE |
| 薪资     | salary           | varchar(50)  | FALSE | FALSE | FALSE |
| 公司规模 | company_scale    | varchar(50)  | FALSE | FALSE | FALSE |
| 公司地址 | company_address  | varchar(100) | FALSE | FALSE | FALSE |
| 学历     | education        | varchar(50)  | FALSE | FALSE | FALSE |
| 经验     | experience       | varchar(50)  | FALSE | FALSE | FALSE |
| 工作性质 | work_nature      | varchar(50)  | FALSE | FALSE | FALSE |
| 招聘人数 | recruiting       | varchar(50)  | FALSE | FALSE | FALSE |
| 工作地址 | address          | varchar(100) | FALSE | FALSE | FALSE |
| 职位信息 | ability          | longtext     | FALSE | FALSE | FALSE |
| 发布时间 | release_time     | date         | FALSE | FALSE | FALSE |
| 采集网站 | website          | varchar(50)  | FALSE | FALSE | FALSE |
| 页面地址 | url              | varchar(250) | FALSE | FALSE | FALSE |

> 5.数据性质:港口设施
> 表名:data_chinaports_facilities  索引: port_id, company_name, equip_name, equip_type

| 中文名称 | 字段名       | 数据类型     | 主键  | 非空  | 外健  |
| -------- | ------------ | ------------ | ----- | ----- | ----- |
| ID       | ID           | int(11)      | TRUE  | TRUE  | FALSE |
| 港口ID   | port_id      | int(11)      | FALSE | FALSE | FALSE |
| 公司名称 | company_name | varchar(100) | FALSE | FALSE | FALSE |
| 设施名称 | equip_name   | varchar(100) | FALSE | FALSE | FALSE |
| 设施型号 | equip_type   | varchar(100) | FALSE | FALSE | FALSE |
| 设施数量 | equip_num    | int(11)      | FALSE | FALSE | FALSE |
| 设施单位 | equip_unit   | varchar(50)  | FALSE | FALSE | FALSE |
| 备注说明 | remark       | text         | FALSE | FALSE | FALSE |
| 页面地址 | url          | varchar(250) | FALSE | FALSE | FALSE |

> 6.数据性质:港口企业
> 表名:data_chinaports_portcorps  索引: port_id, company_name

| 中文名称 | 字段名          | 数据类型     | 主键  | 非空  | 外健  |
| -------- | --------------- | ------------ | ----- | ----- | ----- |
| ID       | ID              | int(11)      | TRUE  | TRUE  | FALSE |
| 公司ID   | port_id         | int(11)      | FALSE | FALSE | FALSE |
| 公司名称 | company_name    | varchar(100) | FALSE | FALSE | FALSE |
| 公司地址 | company_address | varchar(250) | FALSE | FALSE | FALSE |
| 公司电话 | company_tel     | varchar(100) | FALSE | FALSE | FALSE |
| 公司网站 | company_url     | varchar(250) | FALSE | FALSE | FALSE |
| 页面地址 | url             | varchar(250) | FALSE | FALSE | FALSE |

> 7.数据性质:港口
> 表名:data_chinaports_ports  索引: port_id

| 中文名称 | 字段名    | 数据类型     | 主键  | 非空  | 外健  |
| -------- | --------- | ------------ | ----- | ----- | ----- |
| ID       | ID        | int(11)      | TRUE  | TRUE  | FALSE |
| 港口ID   | port_id   | int(11)      | FALSE | FALSE | FALSE |
| 港口名称 | port_name | varchar(50)  | FALSE | FALSE | FALSE |
| 港口区域 | port_area | varchar(50)  | FALSE | FALSE | FALSE |
| 港口信息 | port_info | text         | FALSE | FALSE | FALSE |
| 页面地址 | url       | varchar(250) | FALSE | FALSE | FALSE |

> 8.数据性质:港口船舶企业
> 表名:data_chinaports_shipcorps  索引: corp_id

| 中文名称 | 字段名           | 数据类型     | 主键  | 非空  | 外健  |
| -------- | ---------------- | ------------ | ----- | ----- | ----- |
| ID       | ID               | int(11)      | TRUE  | TRUE  | FALSE |
| 公司ID   | corp_id          | varchar(50)  | FALSE | FALSE | FALSE |
| 公司名称 | company_name     | varchar(100) | FALSE | FALSE | FALSE |
| 公司地址 | company_address  | varchar(250) | FALSE | FALSE | FALSE |
| 公司电话 | company_tel      | varchar(100) | FALSE | FALSE | FALSE |
| 联系人   | linkman          | varchar(100) | FALSE | FALSE | FALSE |
| 电话     | mobile           | varchar(100) | FALSE | FALSE | FALSE |
| 邮箱     | email            | varchar(100) | FALSE | FALSE | FALSE |
| 传真     | fax              | varchar(100) | FALSE | FALSE | FALSE |
| 公司信息 | company_info     | text         | FALSE | FALSE | FALSE |
| 公司业务 | company_business | text         | FALSE | FALSE | FALSE |
| 页面地址 | url              | varchar(250) | FALSE | FALSE | FALSE |

> 9.数据性质:港口船舶动态
> 表名:data_chinaports_ships  索引: port_id, ship_name, status, port_name, real_time

| 中文名称 | 字段名    | 数据类型     | 主键  | 非空  | 外健  |
| -------- | --------- | ------------ | ----- | ----- | ----- |
| ID       | ID        | int(11)      | TRUE  | TRUE  | FALSE |
| 港口ID   | port_id   | int(11)      | FALSE | FALSE | FALSE |
| 船舶名字 | ship_name | varchar(100) | FALSE | FALSE | FALSE |
| 船舶状态 | status    | varchar(100) | FALSE | FALSE | FALSE |
| 口岸名字 | port_name | varchar(100) | FALSE | FALSE | FALSE |
| 船舶类型 | ship_type | varchar(100) | FALSE | FALSE | FALSE |
| 船舶载重 | ship_load | double(11,2) | FALSE | FALSE | FALSE |
| 实时时间 | real_time | datetime     | FALSE | FALSE | FALSE |
| 页面地址 | url       | varchar(250) | FALSE | FALSE | FALSE |

> 10.数据性质:省市代码
> 表名:data_city_codes  索引: sid

| 中文名称 | 字段名    | 数据类型     | 主键  | 非空  | 外健  |
| -------- | --------- | ------------ | ----- | ----- | ----- |
| ID       | ID        | int(11)      | TRUE  | TRUE  | FALSE |
| 省市ID   | sid       | int(11)      | FALSE | FALSE | FALSE |
| 省市全称 | full_name | varchar(100) | FALSE | FALSE | FALSE |
| 省市级别 | level     | varchar(100) | FALSE | FALSE | FALSE |
| 父级ID   | pid       | varchar(100) | FALSE | FALSE | FALSE |

> 11.数据性质:数据资讯
> 表名:data_data_news  索引: article_url

| 中文名称 | 字段名          | 数据类型     | 主键  | 非空  | 外健  |
| -------- | --------------- | ------------ | ----- | ----- | ----- |
| ID       | ID              | int(11)      | TRUE  | TRUE  | FALSE |
| 页面地址 | article_url     | varchar(250) | FALSE | FALSE | FALSE |
| 文章题目 | article_title   | varchar(100) | FALSE | FALSE | FALSE |
| 发表时间 | article_time    | date         | FALSE | FALSE | FALSE |
| 文章来源 | article_src     | varchar(100) | FALSE | FALSE | FALSE |
| 文章内容 | article_content | longtext     | FALSE | FALSE | FALSE |
| 网站     | website         | varchar(100) | FALSE | FALSE | FALSE |
| 搜索词   | search_word     | varchar(100) | FALSE | FALSE | FALSE |

> 12.数据性质:车源信息
> 表名:data_freight_cars   索引:url

| 中文名称   | 字段名            | 数据类型     | 主键  | 非空  | 外健  |
| ---------- | ----------------- | ------------ | ----- | ----- | ----- |
| ID         | ID                | int(11)      | TRUE  | TRUE  | FALSE |
| 出发地     | delivery_address  | varchar(50)  | FALSE | FALSE | FALSE |
| 出发省     | delivery_province | varchar(50)  | FALSE | FALSE | FALSE |
| 出发市     | delivery_city     | varchar(50)  | FALSE | FALSE | FALSE |
| 出发县     | delivery_county   | varchar(50)  | FALSE | FALSE | FALSE |
| 目的地     | receiver_address  | varchar(50)  | FALSE | FALSE | FALSE |
| 目的省     | receiver_province | varchar(50)  | FALSE | FALSE | FALSE |
| 目的市     | receiver_city     | varchar(50)  | FALSE | FALSE | FALSE |
| 目的县     | receiver_county   | varchar(50)  | FALSE | FALSE | FALSE |
| 车牌号     | car_num           | varchar(50)  | FALSE | FALSE | FALSE |
| 车辆类型   | car_type          | varchar(50)  | FALSE | FALSE | FALSE |
| 车长       | car_length        | varchar(50)  | FALSE | FALSE | FALSE |
| 车长单位   | unit_length       | varchar(50)  | FALSE | FALSE | FALSE |
| 车重       | car_weight        | varchar(50)  | FALSE | FALSE | FALSE |
| 车重单位   | unit_weight       | varchar(50)  | FALSE | FALSE | FALSE |
| 体积       | car_volume        | varchar(50)  | FALSE | FALSE | FALSE |
| 体积单位   | unit_volume       | varchar(50)  | FALSE | FALSE | FALSE |
| 价格       | car_price         | varchar(50)  | FALSE | FALSE | FALSE |
| 价格单位   | unit_price        | varchar(50)  | FALSE | FALSE | FALSE |
| 时效       | time              | varchar(50)  | FALSE | FALSE | FALSE |
| 时效单位   | unit_time         | varchar(50)  | FALSE | FALSE | FALSE |
| 公司       | company           | varchar(50)  | FALSE | FALSE | FALSE |
| 联系人     | linkman           | varchar(50)  | FALSE | FALSE | FALSE |
| 电话       | phone             | varchar(50)  | FALSE | FALSE | FALSE |
| 手机       | mobile            | varchar(50)  | FALSE | FALSE | FALSE |
| 车辆所在地 | car_address       | varchar(50)  | FALSE | FALSE | FALSE |
| 出发时间   | departure         | varchar(50)  | FALSE | FALSE | FALSE |
| 发布时间   | publish_date      | varchar(50)  | FALSE | FALSE | FALSE |
| 网站       | website           | varchar(50)  | FALSE | FALSE | FALSE |
| 页面地址   | url               | varchar(250) | FALSE | FALSE | FALSE |

> 13.数据性质:货源信息
> 表名:data_freight_goods   索引: url, release_time

| 中文名称 | 字段名            | 数据类型     | 主键  | 非空  | 外健  |
| -------- | ----------------- | ------------ | ----- | ----- | ----- |
| ID       | ID                | int(11)      | TRUE  | TRUE  | FALSE |
| 出发地   | send_address      | varchar(100) | FALSE | FALSE | FALSE |
| 出发省   | send_province     | varchar(50)  | FALSE | FALSE | FALSE |
| 出发市   | send_city         | varchar(50)  | FALSE | FALSE | FALSE |
| 出发县   | send_county       | varchar(50)  | FALSE | FALSE | FALSE |
| 目的地   | receiver_address  | varchar(100) | FALSE | FALSE | FALSE |
| 目的省   | receiver_province | varchar(50)  | FALSE | FALSE | FALSE |
| 目的市   | receiver_city     | varchar(50)  | FALSE | FALSE | FALSE |
| 目的县   | receiver_county   | varchar(50)  | FALSE | FALSE | FALSE |
| 货品名   | goods_name        | varchar(50)  | FALSE | FALSE | FALSE |
| 货品类型 | goods_type        | varchar(50)  | FALSE | FALSE | FALSE |
| 货品重量 | goods_weight      | varchar(50)  | FALSE | FALSE | FALSE |
| 货品体积 | goods_volume      | varchar(50)  | FALSE | FALSE | FALSE |
| 运输方式 | transport_type    | varchar(50)  | FALSE | FALSE | FALSE |
| 价格     | price             | varchar(50)  | FALSE | FALSE | FALSE |
| 公司     | company_name      | varchar(100) | FALSE | FALSE | FALSE |
| 联系人   | linkman           | varchar(50)  | FALSE | FALSE | FALSE |
| 有效期   | indate            | varchar(50)  | FALSE | FALSE | FALSE |
| 发布时间 | release_time      | varchar(50)  | FALSE | FALSE | FALSE |
| 网站     | website           | varchar(50)  | FALSE | FALSE | FALSE |
| 页面地址 | url               | varchar(250) | FALSE | FALSE | FALSE |

> 14.数据性质:零担信息
> 表名:data_freight_zeroload   索引: url

| 中文名称 | 字段名            | 数据类型     | 主键  | 非空  | 外健  |
| -------- | ----------------- | ------------ | ----- | ----- | ----- |
| ID       | ID                | int(11)      | TRUE  | TRUE  | FALSE |
| 出发地   | delivery_address  | varchar(50)  | FALSE | FALSE | FALSE |
| 出发省   | delivery_province | varchar(50)  | FALSE | FALSE | FALSE |
| 出发市   | delivery_city     | varchar(50)  | FALSE | FALSE | FALSE |
| 出发县   | delivery_county   | varchar(50)  | FALSE | FALSE | FALSE |
| 目的地   | receiver_address  | varchar(50)  | FALSE | FALSE | FALSE |
| 目的省   | receiver_province | varchar(50)  | FALSE | FALSE | FALSE |
| 目的市   | receiver_city     | varchar(50)  | FALSE | FALSE | FALSE |
| 目的县   | receiver_county   | varchar(50)  | FALSE | FALSE | FALSE |
| 重货     | heavy             | varchar(50)  | FALSE | FALSE | FALSE |
| 轻货     | low               | varchar(50)  | FALSE | FALSE | FALSE |
| 时效     | time              | varchar(50)  | FALSE | FALSE | FALSE |
| 价格     | price             | varchar(50)  | FALSE | FALSE | FALSE |
| 公司     | corp_name         | varchar(50)  | FALSE | FALSE | FALSE |
| 联系人   | linkman           | varchar(50)  | FALSE | FALSE | FALSE |
| 电话     | phone             | varchar(50)  | FALSE | FALSE | FALSE |
| 手机     | mobile            | varchar(50)  | FALSE | FALSE | FALSE |
| 公司地址 | corp_address      | varchar(50)  | FALSE | FALSE | FALSE |
| 发布时间 | publish_date      | date         | FALSE | FALSE | FALSE |
| 网站     | website           | varchar(50)  | FALSE | FALSE | FALSE |
| 页面地址 | url               | varchar(250) | FALSE | FALSE | FALSE |

> 15.数据性质:快递企业
> 表名:data_kd100_companies  索引: url

| 中文名称 | 字段名    | 数据类型     | 主键  | 非空  | 外健  |
| -------- | --------- | ------------ | ----- | ----- | ----- |
| ID       | ID        | int(11)      | TRUE  | TRUE  | FALSE |
| 公司代码 | corp_code | varchar(50)  | FALSE | FALSE | FALSE |
| 公司名称 | corp_name | varchar(50)  | FALSE | FALSE | FALSE |
| 公司电话 | corp_tel  | varchar(50)  | FALSE | FALSE | FALSE |
| 公司网站 | corp_url  | varchar(250) | FALSE | FALSE | FALSE |
| 公司logo | corp_img  | varchar(250) | FALSE | FALSE | FALSE |
| 公司信息 | corp_info | text         | FALSE | FALSE | FALSE |
| 页面地址 | url       | varchar(250) | FALSE | FALSE | FALSE |

> 16.数据性质:快递线路
> 表名:data_kd100_express   
> 索引: company_code, product_type, send_code, receive_code, pick_time, 
>       freight_time, total_price, min_price, first_price, follow_price

| 中文名称 | 字段名       | 数据类型     | 主键  | 非空  | 外健  |
| -------- | ------------ | ------------ | ----- | ----- | ----- |
| ID       | ID           | int(11)      | TRUE  | TRUE  | FALSE |
| 公司代码 | company_code | varchar(20)  | FALSE | FALSE | FALSE |
| 产品类型 | product_type | varchar(20)  | FALSE | FALSE | FALSE |
| 出发代码 | send_code    | int(11)      | FALSE | FALSE | FALSE |
| 目的代码 | receive_code | int(11)      | FALSE | FALSE | FALSE |
| 取货时间 | pick_time    | varchar(20)  | FALSE | FALSE | FALSE |
| 运输时效 | freight_time | varchar(20)  | FALSE | FALSE | FALSE |
| 总价     | total_price  | double(11,2) | FALSE | FALSE | FALSE |
| 最低一票 | min_price    | double(11,2) | FALSE | FALSE | FALSE |
| 首重价格 | first_price  | double(11,2) | FALSE | FALSE | FALSE |
| 续重价格 | follow_price | double(11,2) | FALSE | FALSE | FALSE |
| 电话     | phone        | varchar(100) | FALSE | FALSE | FALSE |
| Qq       | qq           | varchar(50)  | FALSE | FALSE | FALSE |

> 17.数据性质:快递网点
> 表名:data_kd100_nodes   索引: url, city_code

| 中文名称 | 字段名         | 数据类型     | 主键  | 非空  | 外健  |
| -------- | -------------- | ------------ | ----- | ----- | ----- |
| ID       | ID             | int(11)      | TRUE  | TRUE  | FALSE |
| 网点名称 | node_name      | varchar(100) | FALSE | FALSE | FALSE |
| 公司名称 | company_name   | varchar(100) | FALSE | FALSE | FALSE |
| 城市代码 | city_code      | int(11)      | FALSE | FALSE | FALSE |
| 网点地址 | node_address   | varchar(250) | FALSE | FALSE | FALSE |
| 取件电话 | check_phone    | varchar(250) | FALSE | FALSE | FALSE |
| 查件电话 | take_phone     | varchar(250) | FALSE | FALSE | FALSE |
| 投诉电话 | complain_phone | varchar(250) | FALSE | FALSE | FALSE |
| 联系人   | linkman        | varchar(250) | FALSE | FALSE | FALSE |
| 收派范围 | work_area      | longtext     | FALSE | FALSE | FALSE |
| 超区范围 | refuse_area    | longtext     | FALSE | FALSE | FALSE |
| 备注     | remark         | longtext     | FALSE | FALSE | FALSE |
| 网页地址 | url            | varchar(250) | FALSE | FALSE | FALSE |

> 18.数据性质:领导人信息
> 表名:data_leaders   索引: name, department, province, city, level

| 中文名称 | 字段名     | 数据类型     | 主键  | 非空  | 外健  |
| -------- | ---------- | ------------ | ----- | ----- | ----- |
| ID       | ID         | int(11)      | TRUE  | TRUE  | FALSE |
| 姓名     | name       | varchar(50)  | FALSE | FALSE | FALSE |
| 部门     | department | varchar(50)  | FALSE | FALSE | FALSE |
| 职位     | position   | varchar(250) | FALSE | FALSE | FALSE |
| 省       | province   | varchar(50)  | FALSE | FALSE | FALSE |
| 市       | city       | varchar(50)  | FALSE | FALSE | FALSE |
| 县       | county     | varchar(50)  | FALSE | FALSE | FALSE |
| 层级     | level      | int(2)       | FALSE | FALSE | FALSE |
| 信息     | info       | text         | FALSE | FALSE | FALSE |
| 图片     | photo      | varchar(250) | FALSE | FALSE | FALSE |
| 网站     | website    | varchar(50)  | FALSE | FALSE | FALSE |
| 网页地址 | url        | varchar(250) | FALSE | FALSE | FALSE |

> 19.数据性质:资讯，评价
> 表名:data_logistics_news  索引: article_title, article_src, article_time, website
> 同表:data_logistics_comments

| 中文名称   | 字段名          | 数据类型     | 主键  | 非空  | 外健  |
| ---------- | --------------- | ------------ | ----- | ----- | ----- |
| ID         | ID              | int(11)      | TRUE  | TRUE  | FALSE |
| 页面地址   | article_url     | varchar(250) | FALSE | FALSE | FALSE |
| 文章题目   | article_title   | varchar(100) | FALSE | FALSE | FALSE |
| 发表时间   | article_time    | date         | FALSE | FALSE | FALSE |
| 文章来源   | article_src     | varchar(100) | FALSE | FALSE | FALSE |
| 文章内容   | article_content | longtext     | FALSE | FALSE | FALSE |
| 网站       | website         | varchar(100) | FALSE | FALSE | FALSE |
| 搜索词     | search_word     | varchar(100) | FALSE | FALSE | FALSE |
| 访问量     | visit_count     | int(11)      | FALSE | FALSE | FALSE |
| 分享量     | share_count     | int(11)      | FALSE | FALSE | FALSE |
| 回复量     | reply_count     | int(11)      | FALSE | FALSE | FALSE |
| 点赞量     | favorite_count  | int(11)      | FALSE | FALSE | FALSE |
| 是否主题贴 | isreply         | int(11)      | FALSE | FALSE | FALSE |

> 20.数据性质:上市企业
> 表名:data_sina_corps  索引: stock_id

| 中文名称 | 字段名          | 数据类型     | 主键  | 非空  | 外健  |
| -------- | --------------- | ------------ | ----- | ----- | ----- |
| ID       | ID              | int(11)      | TRUE  | TRUE  | FALSE |
| 股票代码 | stock_id        | varchar(20)  | FALSE | FALSE | FALSE |
| 股票名称 | stock_name      | varchar(100) | FALSE | FALSE | FALSE |
| 上市类型 | stock_type      | varchar(20)  | FALSE | FALSE | FALSE |
| 公司名称 | corp_name       | varchar(100) | FALSE | FALSE | FALSE |
| 公司简介 | corp_intro      | longtext     | FALSE | FALSE | FALSE |
| 公司信息 | corp_info       | longtext     | FALSE | FALSE | FALSE |
| 公司高管 | corp_manager    | longtext     | FALSE | FALSE | FALSE |
| 公司董事 | corp_director   | longtext     | FALSE | FALSE | FALSE |
| 公司监事 | corp_supervisor | longtext     | FALSE | FALSE | FALSE |
| 分线     | min_gif         | varchar(250) | FALSE | FALSE | FALSE |
| 日线     | daily_gif       | varchar(250) | FALSE | FALSE | FALSE |
| 周线     | weekly_gif      | varchar(250) | FALSE | FALSE | FALSE |
| 月线     | monthly_gif     | varchar(250) | FALSE | FALSE | FALSE |
| 网页地址 | url             | varchar(250) | FALSE | FALSE | FALSE |

> 21.数据性质:上市企业数据报表
> 表名:data_sina_tables  索引: stock_id, table_id, year

| 中文名称 | 字段名     | 数据类型     | 主键  | 非空  | 外健  |
| -------- | ---------- | ------------ | ----- | ----- | ----- |
| ID       | ID         | int(11)      | TRUE  | TRUE  | FALSE |
| 股票代码 | stock_id   | varchar(20)  | FALSE | FALSE | FALSE |
| 表格代码 | table_id   | varchar(100) | FALSE | FALSE | FALSE |
| 年份     | year       | int(11)      | FALSE | FALSE | FALSE |
| 计量单位 | unit       | varchar(100) | FALSE | FALSE | FALSE |
| 值域名称 | value_name | varchar(250) | FALSE | FALSE | FALSE |
| 时间1    | date1      | date         | FALSE | FALSE | FALSE |
| 值1      | value1     | varchar(250) | FALSE | FALSE | FALSE |
| 时间2    | date2      | date         | FALSE | FALSE | FALSE |
| 值2      | value2     | varchar(250) | FALSE | FALSE | FALSE |
| 时间3    | date3      | date         | FALSE | FALSE | FALSE |
| 值3      | value3     | varchar(250) | FALSE | FALSE | FALSE |
| 时间4    | date4      | date         | FALSE | FALSE | FALSE |
| 值4      | value4     | varchar(250) | FALSE | FALSE | FALSE |
| 网页地址 | url        | varchar(250) | FALSE | FALSE | FALSE |

> 22.数据性质:国家统计局数据
> 表名:data_stats_data  索引: dbcode, pid, sid, valuecode, regcode

| 中文名称 | 字段名    | 数据类型    | 主键  | 非空  | 外健  |
| -------- | --------- | ----------- | ----- | ----- | ----- |
| ID       | ID        | int(11)     | TRUE  | TRUE  | FALSE |
| db代码   | dbcode    | varchar(50) | FALSE | FALSE | FALSE |
| 父级代码 | pid       | varchar(50) | FALSE | FALSE | FALSE |
| 本级代码 | sid       | varchar(50) | FALSE | FALSE | FALSE |
| 时间代码 | valuecode | varchar(50) | FALSE | FALSE | FALSE |
| 值       | strdata   | varchar(50) | FALSE | FALSE | FALSE |
| 城市代码 | regcode   | varchar(50) | FALSE | FALSE | FALSE |

> 23.数据性质:国家统计局分类
> 表名:data_stats_types 索引: dbcode, wdcode, pid, sid

| 中文名称 | 字段名   | 数据类型     | 主键  | 非空  | 外健  |
| -------- | -------- | ------------ | ----- | ----- | ----- |
| ID       | ID       | int(11)      | TRUE  | TRUE  | FALSE |
| db代码   | dbcode   | varchar(20)  | FALSE | FALSE | FALSE |
| wd代码   | wdcode   | varchar(20)  | FALSE | FALSE | FALSE |
| 父级代码 | pid      | varchar(50)  | FALSE | FALSE | FALSE |
| 是否父级 | isparent | int(11)      | FALSE | FALSE | FALSE |
| 等级     | level    | int(11)      | FALSE | FALSE | FALSE |
| 本级代码 | sid      | varchar(50)  | FALSE | FALSE | FALSE |
| 名称     | name     | varchar(200) | FALSE | FALSE | FALSE |
| 单位     | unit     | varchar(20)  | FALSE | FALSE | FALSE |
| exp      | exp      | longtext     | FALSE | FALSE | FALSE |
| memo     | memo     | longtext     | FALSE | FALSE | FALSE |

> 24.数据性质:世界银行国家
> 表名:data_wb_countries  索引: iso2code

| 中文名称     | 字段名            | 数据类型    | 主键  | 非空  | 外健  |
| ------------ | ----------------- | ----------- | ----- | ----- | ----- |
| ID           | ID                | int(11)     | TRUE  | TRUE  | FALSE |
| Iso3代码     | iso3code          | varchar(20) | FALSE | FALSE | FALSE |
| Iso2代码     | iso2code          | varchar(20) | FALSE | FALSE | FALSE |
| 国家名称     | country_name      | varchar(50) | FALSE | FALSE | FALSE |
| 国家中文名称 | cn_zh             | varchar(50) | FALSE | FALSE | FALSE |
| 首都         | capital_city      | varchar(50) | FALSE | FALSE | FALSE |
| 首都中文     | cc_zh             | varchar(50) | FALSE | FALSE | FALSE |
| 区域代码     | region_id         | varchar(50) | FALSE | FALSE | FALSE |
| 区域         | region_value      | varchar(50) | FALSE | FALSE | FALSE |
| 区域中文     | rv_zh             | varchar(50) | FALSE | FALSE | FALSE |
| 管理区域代码 | adminregion_id    | varchar(50) | FALSE | FALSE | FALSE |
| 管理区域     | adminregion_value | varchar(50) | FALSE | FALSE | FALSE |
| 管理区域中文 | av_zh             | varchar(50) | FALSE | FALSE | FALSE |
| 收入代码     | incomelevel_id    | varchar(50) | FALSE | FALSE | FALSE |
| 收入         | incomelevel_value | varchar(50) | FALSE | FALSE | FALSE |
| 收入中文     | iv_zh             | varchar(50) | FALSE | FALSE | FALSE |
| 借贷类型代码 | lendingtype_id    | varchar(50) | FALSE | FALSE | FALSE |
| 借贷类型     | lendingtype_value | varchar(50) | FALSE | FALSE | FALSE |
| 借贷类型中文 | lv_zh             | varchar(50) | FALSE | FALSE | FALSE |
| 经度         | longitude         | varchar(50) | FALSE | FALSE | FALSE |
| 纬度         | latitude          | varchar(50) | FALSE | FALSE | FALSE |

> 25.数据性质:世界银行数据
> 表名:data_wb_data 索引: indicator_id, iso2code, valuecode

| 中文名称 | 字段名       | 数据类型    | 主键  | 非空  | 外健  |
| -------- | ------------ | ----------- | ----- | ----- | ----- |
| ID       | ID           | int(11)     | TRUE  | TRUE  | FALSE |
| 指标代码 | indicator_id | varchar(50) | FALSE | FALSE | FALSE |
| Iso2代码 | iso2code     | varchar(50) | FALSE | FALSE | FALSE |
| 年份     | valuecode    | varchar(50) | FALSE | FALSE | FALSE |
| 值       | strdata      | varchar(50) | FALSE | FALSE | FALSE |

> 26.数据性质:世界银行指标
> 表名:data_wb_topics 索引: indicator_id, topic_id

| 中文名称     | 字段名              | 数据类型    | 主键  | 非空  | 外健  |
| ------------ | ------------------- | ----------- | ----- | ----- | ----- |
| ID           | ID                  | int(11)     | TRUE  | TRUE  | FALSE |
| 指标代码     | indicator_id        | varchar(50) | FALSE | FALSE | FALSE |
| 指标名称     | indicator_name      | varchar(20) | FALSE | FALSE | FALSE |
| 指标中文     | in_zh               | varchar(50) | FALSE | FALSE | FALSE |
| 主题代码     | topic_id            | int(11)     | FALSE | FALSE | FALSE |
| 主题名称     | topic_value         | varchar(50) | FALSE | FALSE | FALSE |
| 主题中文     | tv_zh               | varchar(50) | FALSE | FALSE | FALSE |
| 来源注释     | source_note         | varchar(50) | FALSE | FALSE | FALSE |
| 来源注释中文 | sn_zh               | varchar(50) | FALSE | FALSE | FALSE |
| 来源组织     | source_organization | varchar(50) | FALSE | FALSE | FALSE |
| 来源组织中文 | so_zh               | varchar(50) | FALSE | FALSE | FALSE |

> 27.数据性质:天气
> 表名:data_weather  索引: province, city, zone, riqi

| 中文名称 | 字段名         | 数据类型    | 主键  | 非空  | 外健  |
| -------- | -------------- | ----------- | ----- | ----- | ----- |
| ID       | ID             | int(11)     | TRUE  | TRUE  | FALSE |
| 省       | province       | varchar(50) | FALSE | FALSE | FALSE |
| 市       | city           | varchar(20) | FALSE | FALSE | FALSE |
| 县       | zone           | varchar(50) | FALSE | FALSE | FALSE |
| 时间     | riqi           | date        | FALSE | FALSE | FALSE |
| 最高气温 | temperature_h  | varchar(50) | FALSE | FALSE | FALSE |
| 最低气温 | temperature_l  | varchar(50) | FALSE | FALSE | FALSE |
| 天气     | weather        | varchar(50) | FALSE | FALSE | FALSE |
| 风向     | wind_direction | varchar(50) | FALSE | FALSE | FALSE |
| 风力     | wind_power     | varchar(50) | FALSE | FALSE | FALSE |

 