# -*- coding: utf-8 -*-
# =============================================================================
# Copyright (c) 2018-, pyLeo Developer. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================


from train.captcha_run import CaptchaRun
from concurrent.futures import ThreadPoolExecutor
import requests
import time
from PIL import Image
from io import BytesIO
import demjson



def test2(n):
	s = requests.session()
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

	with open(f"test.jpg", "wb") as f:
		f.write(img.content)


	# 打开文件夹中的图片
	image = Image.open(BytesIO(img.content))
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

	bytesIO = BytesIO()
	bim.save(bytesIO, format='jpeg')
	image_data = bytesIO.getvalue()

	# bim.save('test2.jpg')
	# with open("test2.jpg", "rb") as f:
	# 	image_data = f.read()

	s = time.time()
	
	CR = CaptchaRun()
	
	pre_text = CR.captcha2text(image_data, 'model/')
	
	CR.tf.compat.v1.reset_default_graph()
	
	e = time.time()
	print(' 模型预测值:', pre_text, "时间：", e - s)


	# with open(f"img/{response.text}-{int(time.time())}.png", "wb") as f:
	# 	f.write(image_data)

	# with open(f"test.jpg", "wb") as f:
	# 	f.write(image_data)
	






if __name__ == '__main__':

	test2(1)

	# for i in range(100):
	# 	test2(i)

	# executor = ThreadPoolExecutor(max_workers=1)
	# urls = [3 for x in range(5000)]  # 并不是真的url
	# for data in executor.map(test, urls):
	# 	pass
	#



