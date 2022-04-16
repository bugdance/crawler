import requests

def ticket():
    data = {
        'username': '13084233827',
        'password': '22In06jA8',
        'ticket_code': 'E615503560',
        'pay_code': '00011000',
        'cookie': 'JSESSIONID%3D153AF3DA300D4506A062759FE66D1A47%3B+BIGipServerotn%3D972030474.64545.0000%3B+route%3D6f50b51faa11b987e576cdb301e545c4%3B+current_captcha_type%3DZ'
    }
    a = requests.post('http://headless.hangtian123.com/payments/', data=data)
    # a = requests.post(url="http://127.0.0.1/payments/", data=data)
    print(a.text)


# while True:
ticket()