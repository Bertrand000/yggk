# -*- coding: utf-8 -*-
"""
Created on Tue May 28 19:23:19 2019
将图片按照表格框线交叉点分割成子图片（传入图片路径）
@author: hx
"""

import cv2
import numpy as np
import pytesseract
import os
import matplotlib.pyplot as plt
import redis
from zzzs import my_util
from PIL import Image
from zzzs import image_see as bd_ocr

my_util = my_util.my_util()
r = redis.Redis(host='localhost', port='6379', db=0)
dict_all = my_util.db.query("select h_school from 1_2")

def image_see(image_path,path_name):
    '''opencv中opencv不接受non-ascii的路径,即接收中文，解决方法就是先用先用np.fromfile()读取为np.uint8格式，再使用cv2.imdecode()解码，如下：'''
    image = cv2.imdecode(np.fromfile(image_path,dtype=np.uint8), -1)
    # 灰度图片
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # cv2.imshow('result.jpg',image)
    # 二值化
    binary = cv2.adaptiveThreshold(~gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, -5)
    # ret,binary = cv2.threshold(~gray, 127, 255, cv2.THRESH_BINARY)
    # cv2.imshow("二值化图片：", binary)  # 展示图片
    # cv2.waitKey(0)

    rows, cols = binary.shape
    scale = 40
    # 识别横线
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (cols // scale, 1))
    eroded = cv2.erode(binary, kernel, iterations=1)
    # cv2.imshow("Eroded Image",eroded)
    dilatedcol = cv2.dilate(eroded, kernel, iterations=1)
    # cv2.imshow("表格横线展示：", dilatedcol)
    # cv2.waitKey(0)

    # 识别竖线
    scale = 3
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, rows // scale))
    eroded = cv2.erode(binary, kernel, iterations=1)
    dilatedrow = cv2.dilate(eroded, kernel, iterations=1)
    # cv2.imshow("表格竖线展示：", dilatedrow)
    # cv2.waitKey(0)

    # 标识交点
    bitwiseAnd = cv2.bitwise_and(dilatedcol, dilatedrow)
    # cv2.imshow("表格交点展示：", bitwiseAnd)
    # cv2.waitKey(0)
    # cv2.imwrite("my.png",bitwiseAnd) #将二值像素点生成图片保存

    # 标识表格
    merge = cv2.add(dilatedcol, dilatedrow)
    # cv2.imshow("表格整体展示：", merge)
    # cv2.waitKey(0)

    # 两张图片进行减法运算，去掉表格框线
    merge2 = cv2.subtract(binary, merge)
    # cv2.imshow("图片去掉表格框线展示：", merge2)
    # cv2.waitKey(0)

    # 识别黑白图中的白色交叉点，将横纵坐标取出
    ys, xs = np.where(bitwiseAnd > 0)

    mylisty = []  # 纵坐标
    mylistx = []  # 横坐标

    # 通过排序，获取跳变的x和y的值，说明是交点，否则交点会有好多像素值值相近，我只取相近值的最后一点
    # 这个10的跳变不是固定的，根据不同的图片会有微调，基本上为单元格表格的高度（y坐标跳变）和长度（x坐标跳变）
    i = 0
    myxs = np.sort(xs)
    for i in range(len(myxs) - 1):
        if (myxs[i + 1] - myxs[i] > 10):
            mylistx.append(myxs[i])
        i = i + 1
    mylistx.append(myxs[i])  # 要将最后一个点加入

    i = 0
    myys = np.sort(ys)
    # print(np.sort(ys))
    for i in range(len(myys) - 1):
        if (myys[i + 1] - myys[i] > 10):
            mylisty.append(myys[i])
        i = i + 1
    mylisty.append(myys[i])  # 要将最后一个点加入

    print('mylisty', mylisty)
    print('mylistx', mylistx)


    dict = {"name":"","sex":"","school":"","prov":""}
    # my_util.table_create("1_1",dict)
    # print(my_util.sql_create("1_1",dict))
    sql = '''
            REPLACE INTO
                                                                                      1_2(name,sex,school,prov,h_school)
                                                                                      VALUES(%s,%s,%s,%s,%s)
    '''
    # 循环y坐标，x坐标分割表格
    for i in range(len(mylisty) - 1)[1:]:
        data_list = []
        for j in range(len(mylistx) - 1):
            # 在分割时，第一个参数为y坐标，第二个参数为x坐标
            ROI = image[mylisty[i] + 3:mylisty[i + 1] - 3, mylistx[j]:mylistx[j + 1] - 3]  # 减去3的原因是由于我缩小ROI范围
            # cv2.imshow("分割后子图片展示：", ROI)
            # cv2.waitKey(0)
            image_base64 = cv2.imencode('.jpg', ROI)[1]
            text1 = bd_ocr.post_image_tongyong(image_base64,bd_ocr.base_ocr)

            '''识别异常'''
            if not text1:
                text1 = "image discriminate false"
                # raise Exception("识别异常")
            if text1=='å¥³':
                text1 = '女'
            elif text1 == "ç”·":
                text1 = '男'
            '''非中文标志识别错误'''
            if '\u4e00' > text1 > '\u9fff':
                text1 = "image discriminate false"

            data_list.append(text1)
            # special_char_list = '`~!@#$%^&*()-_=+[]{}|\\;:‘’，。《》/？ˇ'
            # pytesseract.pytesseract.tesseract_cmd = 'E:/Tesseract-OCR/tesseract.exe'
            # text1 = pytesseract.image_to_string(ROI,lang='fontyp')  # 读取文字，此为默认英文
            # text2 = ''.join([char for char in text2 if char not in special_char_list])
            print('识别分割子图片信息为：' + str(text1))
        data_list.append(str(path_name).split(".")[0])
        my_util.save_data(sql,data_list)

delete_sql = 'delete from 1_2 where h_school="%s"'
# s = delete_sql%"111"
# a = my_util.db.query(s)
base_path = "E:\\yggk_image\\2019年高校自主招生录取考生名单\\自主招生名单公示"
'''中断添加学校'''
# r.sadd("zzmd","西南大学350.jpg")
i = 0
while r.scard("zzmd")!=0 and i < 47000:
    i += 40
    path = str(r.spop("zzmd").decode('utf-8'))
    '''
    遍历所有文件夹
    '''
    if (str(path).split('.')[0],) in dict_all:
        print(path + "已存数据，跳过...")
        continue
    try:
        image_see(base_path + '\\' +path,path)
    except Exception as e:
        my_util.db.query(delete_sql%str(path).split('.')[0])
        print(path + "图片读取异常")
        '''添加异常图片到redis队列'''
        r.sadd("error_zzmd",path)
    print("******************************************************************************************************************")
    print("                                         " + path+"  识别完毕")
    print("******************************************************************************************************************")

# while r.scard("error_set_beifen")>=1:
#     error_p = r.spop("error_set_beifen")
#     test = str(error_p.decode('utf-8'))
#     db_sum = my_util.db.query("select count(h_school) from 1_1")[0][0]
#     # if int(db_sum) - old_sum >= 9000:
#     #     os.exit(1)
#     if (str(test).split('.')[0],) in dict_all:
#         print(test + "已存数据，跳过...")
#         os._exit(1)
#         # continue
#     try:
#         image_see(base_path + '\\' +test,test)
#         print("******************************************************************************************************************")
#         print("                                         " + test + "  识别完毕")
#         print("******************************************************************************************************************")
#     except Exception as e:
#         print(test + "图片读取异常")
#         '''添加异常图片到redis队列'''
#         r.sadd("error_set_beifen",test)







