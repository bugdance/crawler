import time
import requests


def ticket():
    data ={
        'username': '13084233827',
        'password': '22In06jA8',
        'ticket_date': '2019-03-01',
        'ticket_code': 'E610853136',
        'cookie': 'JSESSIONID%3D153AF3DA300D4506A062759FE66D1A47%3B+BIGipServerotn%3D972030474.64545.0000%3B+route%3D6f'
                  '50b51faa11b987e576cdb301e545c4%3B+current_captcha_type%3DZ'
    }

    # a = requests.post('http://127.0.0.1/audits/', data=data)
    a = requests.post('http://headless.hangtian123.com/audits/', data=data, timeout=120)
    print(a.text)


# while True:
ticket()