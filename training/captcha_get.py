import requests
import time


def aa():
	s = requests.session()
	t = time.time()

	header = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
					  "Chrome/86.0.4240.75 Safari/537.36",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
				  "image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
		"Accept-Language": "en-US,en;q=0.9,zh;q=0.8,zh-TW;q=0.7",
		"Host": "weixin.sogou.com",
		"Sec-Fetch-Site": "same-origin",
		"Sec-Fetch-Mode": "no-cors",
		"Sec-Fetch-Dest": "image",
		"Referer": "https://weixin.sogou.com/antispider/?from=%2Fweixin%3Ftype%3D1%26query%3DLife-BOOKs%26ie%3Dutf8%26s_from%3Dinput%26_sug_%3Dy%26_sug_type_%3D",

	}
	r = s.get(url="https://weixin.sogou.com/antispider/util/seccode.php", headers=header)
	print(r.content)
	
	with open(f"captcha.jpg", "wb") as f:
		f.write(r.content)


aa()


def asd():
    print()

