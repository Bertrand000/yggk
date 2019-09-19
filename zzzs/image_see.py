#!/usr/bin/env python
# encoding: utf-8
import requests
import base64
import json
'''

@author: Mr.Chen
@file: image_see.py
@time: 2019/9/3 11:37

'''
table_ocr = "https://aip.baidubce.com/rest/2.0/solution/v1/form_ocr/request"
tongyong_ocr = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
'''高精度含位置'''
ces_ocr = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate"
'''百度基础图像识别'''
base_ocr = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
'''自定义模板识别'''
MODEL_OCR = "https://aip.baidubce.com/rest/2.0/solution/v1/iocr/recognise"
app_key = "STTHk6B5AQFNZ0Td0EZ9SG3o"
secret_key = "USHUyIt0wkMGIcjmVv2lv72akjC4HGYK"
'''小魏'''
# app_key = "vDRbUXbnDMncYOl7R6vPvcPi"
# secret_key = "mhV39dDoTd1M2WEaozkfVo0R0SQ0FvRk"
'''波娃'''
# app_key = "1bYlRSkiV4dFhSn7zGOLfWhE"
# secret_key = "mtHL0Gi5Sl8cMzbiloIQQ9iaf61xH18i"

token = "24.3e71cee5cbd1b1c966cb30fcfca456e4.2592000.1570178560.282335-17108856"
'''波娃账号token'''
token_b = "24.4be9b3c18eab0fb1783677fbb371432f.2592000.1571381154.282335-17272107"
'''小魏账号token'''
token_w = "24.fce7eab3a602d4813edb9b3c041fa7c6.2592000.1571386011.282335-17273240"


def __get_token(api_key,secret_key):
    '''
    获取token
    :return:
    '''
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    '''
    例：https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=Va5yQRHlA4Fq5eR3LT0vuXV4&client_secret=0rDSjzQ20XUj5itV6WRtznPQSzr5pVw2&
    grant_type： 必须参数，固定为client_credentials；
    client_id： 必须参数，应用的API Key； 4WIIzGSB8IHTsSR9lfw9fXGD
    client_secret： 必须参数，应用的Secret Key；QrfaMi1jEC010yDxKavo2m33OCKNq0Qn
    '''
    host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s'%(api_key,secret_key)
    resp = requests.session().get(host,headers={'Content-Type':'application/json; charset=UTF-8'})

    if (resp.text):
        print(json.loads(resp.text)['access_token'])

def post_image():
    '''
    提交图片给百度处理
    :return:
    '''
    ''' or json / excel'''
    type_status = "json"

    post_image_url = table_ocr + "?access_token=" + token
    '''图片编码'''
    with open("a.jpg", 'rb') as f:
        base64_data = base64.b64encode(f.read())
        code = base64_data.decode()
    if type_status=="json":
        resp = requests.session().post(post_image_url,data={"image":code,"is_sync":"true","request_type":"json"},headers={"Content-Type":"application/x-www-form-urlencoded"})
        resptext = json.loads(resp.text)
        test = json.loads(resptext['result']['result_data'])
        print(resptext)
    else:
        resp = requests.session().post(post_image_url,data={"image":code,"is_sync":"true","request_type":"excel"},headers={"Content-Type":"application/x-www-form-urlencoded"})
        print(resp.text)
def post_image_tongyong(image,url):
    '''
    百度通用性文字识别
    :return:
    '''
    post_image_url = url + "?access_token=" + token_b
    '''图片编码'''
    base64_data = base64.b64encode(image)
    code = base64_data.decode()
    # resp = requests.session().post(post_image_url,data={"image":code},headers={"Content-Type":"application/x-www-form-urlencoded"})
    resp = requests.session().post(post_image_url,data={"image":code},headers={"Content-Type":"application/x-www-form-urlencoded"},timeout=30)
    resptext = json.loads(resp.text)
    try:
        one_word = resptext['words_result'][0]['words']
    except Exception as e:
        return False
    # print(resptext)
    return one_word

def image_url_model(url):
    '''
    图片url模板识别
    :param url:
    :return:
    '''
    '''图片编码'''
    model_u = url + "?access_token=" + token
    with open("a.jpg", 'rb') as f:
        base64_data = base64.b64encode(f.read())
        code = base64_data.decode()
    resp = requests.session().post(model_u,data={"image":code,"templateSign":"8338501f42ce8de607507a9cd0b1ca94"},headers={"Content-Type":"application/x-www-form-urlencoded"})
    resptext = json.loads(resp.text)
    print(resptext)
# __get_token("vDRbUXbnDMncYOl7R6vPvcPi","mhV39dDoTd1M2WEaozkfVo0R0SQ0FvRk")