# # # @@ Import current path
import sys
sys.path.append('..')

from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.http import Http404


# @@..? 需要重新做
def sync_charts(request):
    pass
    # mongo = MongoAct(logger)
    # mongo.start_client("mongodb")
    # db = mongo.create_database("source")
    # source_col = mongo.create_collection(db, 'mcn_source')
    # scrape_col = mongo.create_collection(db, 'mcn_scrape')
    # context = {}
    # try:
    #     # source 同步，抓取，丢失
    #     lost_count = 0
    #     scrape_count = 0
    #     sync_count = mongo.parse_aggregate(
    #         source_col,
    #         [
    #             {"$match": {"syncName": "api"}},
    #             {"$group": {"_id": "$isScrape", "count": {"$sum": 1}}},
    #         ])
    #     if sync_count:
    #         for i in sync_count:
    #             if i['_id']:
    #                 scrape_count = i['count']
    #             else:
    #                 lost_count = i['count']
    #     sync_count = lost_count + scrape_count
    #     context['sync_count'] = sync_count
    #     context['scrape_count'] = scrape_count
    #     context['lost_count'] = lost_count
    #     # scrape 真实，有效，无效
    #     valid_count = 0
    #     invalid_count = 0
    #     real_count = mongo.parse_aggregate(
    #         scrape_col,
    #         [
    #             {"$group": {"_id": "$isAvailable", "count": {"$sum": 1}}},
    #         ])
    #     if real_count:
    #         for i in real_count:
    #             if i['_id']:
    #                 valid_count = i['count']
    #             else:
    #                 invalid_count = i['count']
    #     real_count = valid_count + invalid_count
    #     context['real_count'] = real_count
    #     context['valid_count'] = valid_count
    #     context['invalid_count'] = invalid_count

    #     # 分平台同步
    #     sync_data = mongo.parse_aggregate(
    #         source_col,
    #         [
    #             {"$match": {"syncName": "api"}},
    #             {"$group": {"_id": "$platId", "count": {"$sum": 1}}},
    #         ])
    #     context['sync_data'] = []
    #     if sync_data:
    #         for i in sync_data:
    #             if i['_id'] == 1:
    #                 context["sync_data"].append({"name": '抖音', "value": i['count']})
    #             elif i['_id'] == 2:
    #                 context["sync_data"].append({"name": '快手', "value": i['count']})
    #             elif i['_id'] == 3:
    #                 context["sync_data"].append({"name": '哔哩', "value": i['count']})
    #             elif i['_id'] == 4:
    #                 context["sync_data"].append({"name": '红书', "value": i['count']})
    #             elif i['_id'] == 5:
    #                 context["sync_data"].append({"name": '微博', "value": i['count']})
    #             elif i['_id'] == 6:
    #                 context["sync_data"].append({"name": '微信', "value": i['count']})
    #             elif i['_id'] == 7:
    #                 context["sync_data"].append({"name": '知乎', "value": i['count']})
    #             elif i['_id'] == 8:
    #                 context["sync_data"].append({"name": '头条', "value": i['count']})

    #     # 分平台采集
    #     scrape_data = mongo.parse_aggregate(
    #         source_col,
    #         [
    #             {"$match": {"syncName": "api", "isScrape": 1}},
    #             {"$group": {"_id": "$platId", "count": {"$sum": 1}}},
    #         ])
    #     context['scrape_data'] = []
    #     if scrape_data:
    #         for i in scrape_data:
    #             if i['_id'] == 1:
    #                 context["scrape_data"].append({"name": '抖音', "value": i['count']})
    #             elif i['_id'] == 2:
    #                 context["scrape_data"].append({"name": '快手', "value": i['count']})
    #             elif i['_id'] == 3:
    #                 context["scrape_data"].append({"name": '哔哩', "value": i['count']})
    #             elif i['_id'] == 4:
    #                 context["scrape_data"].append({"name": '红书', "value": i['count']})
    #             elif i['_id'] == 5:
    #                 context["scrape_data"].append({"name": '微博', "value": i['count']})
    #             elif i['_id'] == 6:
    #                 context["scrape_data"].append({"name": '微信', "value": i['count']})
    #             elif i['_id'] == 7:
    #                 context["scrape_data"].append({"name": '知乎', "value": i['count']})
    #             elif i['_id'] == 8:
    #                 context["scrape_data"].append({"name": '头条', "value": i['count']})

    #     # 分平台有效
    #     valid_data = mongo.parse_aggregate(
    #         scrape_col,
    #         [
    #             {"$match": {"isAvailable": 1}},
    #             {"$group": {"_id": "$platId", "count": {"$sum": 1}}},
    #         ])
    #     context['valid_data'] = []
    #     if valid_data:
    #         for i in valid_data:
    #             if i['_id'] == 1:
    #                 context["valid_data"].append({"name": '抖音', "value": i['count']})
    #             elif i['_id'] == 2:
    #                 context["valid_data"].append({"name": '快手', "value": i['count']})
    #             elif i['_id'] == 3:
    #                 context["valid_data"].append({"name": '哔哩', "value": i['count']})
    #             elif i['_id'] == 4:
    #                 context["valid_data"].append({"name": '红书', "value": i['count']})
    #             elif i['_id'] == 5:
    #                 context["valid_data"].append({"name": '微博', "value": i['count']})
    #             elif i['_id'] == 6:
    #                 context["valid_data"].append({"name": '微信', "value": i['count']})
    #             elif i['_id'] == 7:
    #                 context["valid_data"].append({"name": '知乎', "value": i['count']})
    #             elif i['_id'] == 8:
    #                 context["valid_data"].append({"name": '头条', "value": i['count']})

    #     # 分平台无效
    #     invalid_data = mongo.parse_aggregate(
    #         scrape_col,
    #         [
    #             {"$match": {"isAvailable": 0}},
    #             {"$group": {"_id": "$platId", "count": {"$sum": 1}}},
    #         ])
    #     context['invalid_data'] = []
    #     if invalid_data:
    #         for i in invalid_data:
    #             if i['_id'] == 1:
    #                 context["invalid_data"].append({"name": '抖音', "value": i['count']})
    #             elif i['_id'] == 2:
    #                 context["invalid_data"].append({"name": '快手', "value": i['count']})
    #             elif i['_id'] == 3:
    #                 context["invalid_data"].append({"name": '哔哩', "value": i['count']})
    #             elif i['_id'] == 4:
    #                 context["invalid_data"].append({"name": '红书', "value": i['count']})
    #             elif i['_id'] == 5:
    #                 context["invalid_data"].append({"name": '微博', "value": i['count']})
    #             elif i['_id'] == 6:
    #                 context["invalid_data"].append({"name": '微信', "value": i['count']})
    #             elif i['_id'] == 7:
    #                 context["invalid_data"].append({"name": '知乎', "value": i['count']})
    #             elif i['_id'] == 8:
    #                 context["invalid_data"].append({"name": '头条', "value": i['count']})

    # except Exception as ex:
    #     logger.info(ex)
    # finally:
    #     mongo.close_client()
    #     return render(request, 'sync_charts.html', context)



