import requests
import demjson
import random
import time
from PIL import Image
import os


def run():
    s = requests.session()
    n = 550
    while 1:
        h = {
                        "Accept": "*/*",
                      "Accept-Encoding": "gzip, deflate",
                      "Accept-Language": "zh-CN,zh;q=0.9",
                      "Connection": "keep-alive",
                      "Host": "chuanbo.weiboyi.com",
                      "Referer": "http://www.weiboyi.com/",
                      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"

        }
        r = s.get("http://chuanbo.weiboyi.com/hwauth/index/captchaajax", headers=h)
        t = r.text
        t = t.replace("(", "")
        t = t.replace(")", "")
        a = demjson.decode(t)
        url = a['url']

        time.sleep(2)

        h = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Host": "img.weiboyi.com",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"

        }
        img = s.get(url, headers=h)

        with open(f"../images/h{n}.jpg", "wb") as f:
            f.write(img.content)
        # with open(f"test.jpg", "wb") as f:
        #     f.write(img.content)
        # print("OK")
        n += 1
        time.sleep(3)




# 二值化处理
def two_value():
    names = []
    dirs = os.listdir("../test")
    for dir in dirs:
        names.append(dir)
    for i in names:

        # 打开文件夹中的图片
        image = Image.open(f'../test/{i}')
        # 灰度图
        lim = image.convert('L')
        # 灰度阈值设为165，低于这个值的点全部填白色
        threshold = 140
        table = []

        for j in range(256):
            if j < threshold:
                table.append(1)
            else:
                table.append(0)

        bim = lim.point(table, '1')
        bim.save(f'../test2/{i}')


if __name__ == "__main__":

    # run()




    two_value()