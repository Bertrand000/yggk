# -*- coding: utf-8 -*-
"""
Created on Tue May 28 19:23:19 2019
将图片按照表格框线交叉点分割成子图片（传入图片路径）
@author: hx
"""
import math
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

jindu_flag = 1
def split_image_by_sentence(image,y1,y2,x1,x2,var):
    '''
    切割图片根据每句话
    :param cv2:图片容器
    :param y1:最大坐标
    :param y2:最小坐标
    :return:
    '''
    # var 30 或 40
    hight = y2 - y1
    one_with = x2 - x1
    cv2.imshow("测试", image)
    cv2.waitKey(0)
    # 根据传入参数拆分向上取整
    x = math.ceil((y2-y1)/var)
    # 画布X轴大小等于拆分数量*X轴大小
    toImage = Image.new('RGBA', (y2-y1,(x2-x1)*x))

    for i in range(1,x+1):
        ROI = image[y1+var*(i-1):y1+var*i, x1:x2]
        # cv2.imshow("测试", ROI)
        # cv2.waitKey(0)
        # test = Image.fromarray(cv2.cvtColor(ROI,cv2.COLOR_BGR2RGB))
        # test.show()
        toImage.paste(Image.fromarray(cv2.cvtColor(ROI,cv2.COLOR_BGR2RGB)), (one_with * (i - 1),hight))
    toImage.save("a.png")
    print()

def image_see(image_path,path_name,prov="",shcool=""):
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
                                                                                      `2`(h_school,prov,files,`name`,sex,of_prov,of_shcool,type,project,sum,standard,major,pref_score,remake)
                                                                                      VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    '''
    # 循环y坐标，x坐标分割表格
    for i in range(len(mylisty) - 1)[1:]:
        data_list = []
        data_list = [var for var in path_name]
        for j in range(len(mylistx) - 1):
            # 在分割时，第一个参数为y坐标，第二个参数为x坐标
            ROI = image[mylisty[i] + 2:mylisty[i + 1] - 2, mylistx[j]:mylistx[j + 1] - 2]  # 减去3的原因是由于我缩小ROI范围
            # cv2.imshow("分割后子图片展示：", ROI)
            # cv2.waitKey(0)
            image_base64 = cv2.imencode('.jpg', ROI)[1]
            new_ROI = split_image_by_sentence(image,mylisty[i],mylisty[i+1],mylistx[j],mylistx[j+1],30)
            text1 = bd_ocr.post_image_tongyong(image_base64,bd_ocr.base_ocr)

            '''识别异常'''
            if not text1:
                text1 = "image discriminate false"
                # raise Exception("识别异常")
            if text1=='å¥³':
                text1 = '女'
            elif text1 == "ç”·" or text1 == "é‡Œ":
                text1 = '男'
            # '''非中文标志识别错误'''
            # if '\u4e00' > text1 > '\u9fff':
            #     text1 = "image discriminate false"

            data_list.append(text1)
            # special_char_list = '`~!@#$%^&*()-_=+[]{}|\\;:‘’，。《》/？ˇ'
            # pytesseract.pytesseract.tesseract_cmd = 'E:/Tesseract-OCR/tesseract.exe'
            # text1 = pytesseract.image_to_string(ROI,lang='fontyp')  # 读取文字，此为默认英文
            # text2 = ''.join([char for char in text2 if char not in special_char_list])
            print('识别分割子图片信息为：' + str(text1))
        my_util.save_data(sql,data_list)

delete_sql = 'delete from %s where files="%s"'
# s = delete_sql%"111"
# a = my_util.db.query(s)
base_path = "E:\\yggk_image\\2019年具有高校自主招生入选资格的考生名单"
'''中断添加学校'''
# r.sadd("zzmd_1","西南财经大学108.jpg")
'''百度云每天5W条免费'''
i = 0
dict_all = None
def mysql_re(path,table_name):
    '''
    判断该数据是否在mysql 中重复
    :return:
    '''
    global dict_all
    if not dict_all:
        dict_all = my_util.db.query("select h_school from `%s`"%table_name)

    if path in dict_all:
        print(path + "已存数据，跳过...")
        return True
# r.sadd("rxzg",["南京大学","四川","南京大学1.jpg"])
def handle_image_by_path(redis_name,table_name):
    '''
    处理图片为数据
    :param redis_name redis库名
    '''
    # 指定操作全局变量
    flag = True
    i = 0
    while r.scard(redis_name) != 0 and i < 47000:
        i += 100
        # path = str(r.srandmember(redis_name,1)[0].decode('utf-8')).replace("'","").replace(" ","")[1:-1]
        path = str(r.spop(redis_name).decode('utf-8')).replace("'","").replace(" ","")[1:-1]
        path = path.split(",")
        if mysql_re(path[0],2):
            continue
        try:
            image_see(base_path + '\\' + path[0] + "\\" + path[1] + "\\" + path[2],path,path[1],path[0])
        except Exception as e:
            print(e)
            my_util.db.query(delete_sql%(table_name,str(path[0])))
            print(path + "图片读取异常")
            '''添加异常图片到redis队列'''
            r.sadd(redis_name+"_error_1",path)

def read_jpg_redis(base_path,redis_name):
    '''
    读取文件夹下的所有jpg图片名并记录路径信息并保存redis
    '''
    dir_all = os.listdir(base_path)
    # 是否没有二级学院 例如上海交大
    for dir in dir_all:
        dir_two = os.listdir(base_path+"\\"+dir)
        for d in dir_two:
            # 是否有二级学院 例如上海交大 上海交大医学部
            test = os.path.exists(base_path + "\\" + dir + "\\" + dir)
            if test:
                for dir_three in os.listdir(base_path + "\\" + dir + "\\" + d):
                    files = os.listdir(base_path + "\\" + dir + "\\" + d + "\\" + dir_three)
                    for file in files:
                        r.sadd(redis_name,[d,dir_three,file])
            else:
                for file in os.listdir(base_path + "\\" + dir + "\\" + d):
                    r.sadd(redis_name,[dir,d,file])
            # filts = os.listdir(base_path + "\\" + dir + "\\" + d)
            # if filts:
            #     flag = False



# while r.scard("zzmd")!=0 and i < 47000:
#     i += 40
#     path = str(r.spop("zzmd").decode('utf-8'))
#     '''
#     遍历所有文件夹
#     '''
#     if (str(path).split('.')[0],) in dict_all:
#         print(path + "已存数据，跳过...")
#         continue
#     try:
#         image_see(base_path + '\\' +path,path)
#     except Exception as e:
#         my_util.db.query(delete_sql%str(path).split('.')[0])
#         print(path + "图片读取异常")
#         '''添加异常图片到redis队列'''
#         r.sadd("error_zzmd",path)
#     print("******************************************************************************************************************")
#     print("                                         " + path+"  识别完毕")
#     print("******************************************************************************************************************")
# def read_error(redis_name,beifen):
#     # 指定操作全局变量
#     global i
#     while r.scard(redis_name)>=1 and i < 47000 :
#         i += 40
#         error_p = r.spop(redis_name)
#         test = str(error_p.decode('utf-8'))
#         if (str(test).split('.')[0],) in dict_all:
#             print(test + "已存数据，跳过...")
#             continue
#         try:
#             image_see(base_path + '\\' +test,test)
#             print("******************************************************************************************************************")
#             print("                                         " + test + "  识别完毕")
#             print("******************************************************************************************************************")
#         except Exception as e:
#             my_util.db.query(delete_sql % str(test).split('.')[0])
#             print(test + "图片读取异常")
#             '''添加异常图片到redis队列'''
#             r.sadd(beifen,test)
# read_error("zzmd_1","error_zzmd_2")

# read_jpg_redis(base_path,"rxzg")
handle_image_by_path("rxzg","2")






