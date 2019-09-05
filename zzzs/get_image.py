#!/usr/bin/env python
# encoding: utf-8
import requests
import re
import os
import redis
import random
import pymysql
import json
import time
from zzzs import image_see
from bs4 import BeautifulSoup as bs
'''
阳光高考自主招生获取图片
@author: Mr.Chen
@file: get_image.py
@time: 2019/8/28 10:13

'''
'''2019年高校自主招生录取考生名单(高校专项计划名单公示,自主招生名单公示),2019年具有高校自主招生入选资格的考生名单,2019年自主招生报名审核通过的考生名单'''
base_path = "E:\yggk_image"

base_url = "https://gaokao.chsi.com.cn"
url_one = "https://gaokao.chsi.com.cn/zzbm/mdgs/orgs.action?lx=1&a=a"
url_one_2 = "https://gaokao.chsi.com.cn/zzbm/mdgs/orgs.action?lx=2"
url_two = "https://gaokao.chsi.com.cn/zsgs/zzxblqzgmd--method-groupByYx,zslx-1.dhtml"
url_three = "https://gaokao.chsi.com.cn/zsgs/zzlqmd--method-groupByYx,zslx-1.dhtml"
path = "E:\\yggk_image\\2019年具有高校自主招生入选资格的考生名单\\"
headers = {
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
    "Accept-Encoding":"gzip, deflate, br",
    "Accept-Language":"zh-CN,zh;q=0.9",
    "Cache-Control":"max-age=0",
    "Connection":"close",
    "Cookie":"JSESSIONID=59311B019D956FF27DB61E139ADD22C2; TS01c0c047=01886fbf6ecb219d62baf5f2192de0f12e87f36c1119e250a21450ca9eb414bdfff8cde45da7650b2e43ee713ef644f2349db457cff13227e8ae41fd9335dfbf9a71224e4e49870e7582b5d4784405c09a5f037ceb8664c69b993c509d5f263d74fa135574; _ga=GA1.3.1851263967.1546391745; __utmz=142379556.1546495556.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); XSRF-CCKTOKEN=c1adf8c42a5c70847ab3b4cbc4eeee55; CHSICC02=!tKITP0eLQDv5miMGGYWrKFjgWJfD/xTaJISfaVYvQ2F1C9ePoo75Y6HZjzOEqO4X58Q3xKruoUu8IQ==; CHSICC01=!E27vFj+qRZf4au4GGYWrKFjgWJfD/2swOjUDxgZLUq2N9yoipWSkEHUqKN3gjOPjq1yOto/l6V1E7Q==; _gid=GA1.3.206988835.1567470889; __utmc=142379556; TS01e31144=01886fbf6ea72567d8a044dd2125975017c31b0b4b4857145ab2ef5b82eb8299a3b2cf7d923d717ac076cfcf87015ad2ce79a21267f67f6334f0d5a2ae7a7b0f3602d9c83f7f937e0c04e9ccbbbc31f14f00d65696; __utma=142379556.1851263967.1546391745.1567493264.1567499167.27; __utmt=1; __utmb=142379556.7.10.1567499167",
    "Host":"gaokao.chsi.com.cn",
    "Upgrade-Insecure-Requests":"1"
}
user_agents = [
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60',
		'Opera/8.0 (Windows NT 5.1; U; en)',
		'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
		'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
		'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
		'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2 ',
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
		'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
		'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16',
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
		'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11',
		'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER',
		'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
		'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
		'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0) ',
	]
'''redis初始化'''
r = redis.Redis(host='localhost', port='6379', db=0)
def cre_makdir(path_name):
    '''
    创建文件夹
    :return:
    '''
    isExists = os.path.exists(path_name)
    if not isExists:
        os.makedirs(path_name)
        print(path_name + ' 创建成功')
    else:
        print("目录已存在")
def save_image(url,name):
    '''
    保存文件
    :param url: 图片地址
    :return:
    '''
    path_name = name + ".jpg"
    headers['User-Agent'] = random.choice(user_agents)
    resp = requests.session().get(url,headers={"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8","User-Agent":random.choice(user_agents)})
    # 阳光高考监测下行流量
    while(not resp.content):
        i = 0.7
        print("下载限流量，等待"+str(i)+"秒，进入wait时间:")
        # for j in range(1,i+1):
        #     time.sleep(1)
        #     print(i-j+1)

        resp = requests.session().get(url,headers=headers)

    with open(path_name,"wb") as f:
        f.write(resp.content)
    print(name + " 资料保存成功 url：" + url)
def save_job(url,school,hrefs=[],stats=1):
    '''
    获取图片url
    :param dict:图片信息{url:xxx,shcool:xxx}
    :return:
    '''
    headers['User-Agent'] = random.choice(user_agents)
    resp = requests.session().get(url, headers=headers,timeout=30).text
    soup = bs(resp)
    a = soup.find("a", text=re.compile(r"下一页"))
    hrefs.append(url)
    if not a:
        print(school + " 完成图片路径采集!")
        return hrefs
    else:
        next_url = base_url + a['href']
        print(school + ",第" + str(stats) + "页图片,获取成功")
        stats += 1
        save_job(next_url,school,hrefs,stats)
        return hrefs
def image_handle(url):
    '''
    识别图片处理
    :param url:
    :return:
    '''
def get_all_image_url(url):
    '''
    获取全部学校url
    :param url: 初始url
    :return: 返回学校下级url
    '''
    headers['User-Agent'] = random.choice(user_agents)
    resp = requests.session().get(url,headers=headers).text
    soup = bs(resp)
    tags = soup.find(id="YKTabCon2_10").find_all("li")
    prov_list = []
    for tag in tags:
        try:
            href_url = base_url + str(tag.a['href']).replace("amp;", "")

        except Exception as e:
            print(str(tag.text) + "没有数据")
            continue
        school = tag.text.replace("\n", "").replace("\r", "")
        prov_list.append({"url": href_url, "school": school})
    return prov_list

def get_imageurl(pro_url,prov,name,stat=0):
    '''
    递归获取所有图片
    :return:
    '''
    stat += 1
    resp = requests.session().get(pro_url,headers=headers).text

    soup = bs(resp)
    a = soup.find("a",text=re.compile(r"下一页"))
    href = re.findall("var src = '(.+?)';", resp)
    try:
        save_image(href[0], path + name + "\\" + prov + "\\" + name + str(stat))
    except Exception as e:
        print("检查数据")
    if not a:
        return
    else:
        next_url = a['href']
        get_imageurl(next_url,prov,name,stat)

def get_prov(urls,path_school):
    '''
    根据省份
    :param urls:
    :return:
    '''
    prov_list = []
    '''YKTabCon2_10'''
    resp = requests.session().get(urls)
    soup = bs(resp.text)
    tags = soup.find(id = "YKTabCon2_10").find_all("li")
    for tag in tags:
        prov_list.append([tag.text,base_url+str(tag.a['href'])])
        cre_makdir(path_school+ "\\" +tag.text)
    return prov_list
def get_url(resp):
    '''
    获取学校数据
    :param resp:
    :return:
    '''
    soup = bs(resp)
    tags = soup.find(id="YKTabCon2_10").find_all("li")
    for tag in tags:
        try:
            href_url = base_url+str(tag.a['href']).replace("amp;","")
        except Exception as e:
            print(str(tag.text) + "没有数据")
            continue

        school = tag.text.replace("\n","").replace("\r","")
        cre_makdir(path +school)
        prov_list = get_prov(href_url,path +school)
        for prov in prov_list:
            get_imageurl(prov[1],prov[0],school)
get_url(requests.session().get("https://gaokao.chsi.com.cn/zsgs/zzxblqzgmd--method-groupByYx,zslx-1.dhtml",headers=headers).text)


# dict_datas = get_all_image_url(url_one)
#
# for dict_data in dict_datas:
#     u = ""
#     school = ""
#     hh = []
#     u = dict_data['url']
#     school = dict_data['school']
#     hh = save_job(u,school,[])
#     for url_image in list(hh):
#         r.lpush("image_url",{"school":school,"url":url_image})
#         print(school+" 信息图片:" + url_image + "获取成功")
# def image_to_json():
#     '''
#     图片转json
#     :return:
#     '''
#     image_see
