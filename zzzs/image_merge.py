#!/usr/bin/env python
# encoding: utf-8
from PIL import Image,ImageFile
import os
'''
图片合并
@author: Mr.Chen
@file: image_merge.py
@time: 2019/8/30 9:27

'''
IMAGES_PATH = 'E:\\新建文件夹\\'  # 图片集地址
IMAGES_FORMAT = ['.jpg', '.JPG']  # 图片格式
IMAGE_SIZE = 1000  # 宽
IMAGE_ROW = 411 # 高
IMAGE_SAVE_PATH = 'E:\\新建文件夹\\test.jpg'  # 图片转换后的地址

# 获取图片集地址下的所有图片名称
image_names = [name for name in os.listdir(IMAGES_PATH) for item in IMAGES_FORMAT if
               os.path.splitext(name)[1] == item]

# 定义图像拼接函数
def image_compose():
    to_image = Image.new('RGB', (IMAGE_SIZE, IMAGE_ROW*len(image_names)))  # 创建一个新图
    # 循环遍历，把每张图片按顺序粘贴到对应位置上
    for y in range(1, len(image_names) + 1):
            from_image = Image.open(IMAGES_PATH + image_names[y - 1]).resize(
                (IMAGE_SIZE, IMAGE_ROW), Image.ANTIALIAS)
            to_image.paste(from_image, (0, (y - 1) * IMAGE_ROW))

    to_image.save(IMAGE_SAVE_PATH, quality=80, optimize=True, progressive=True)  # 保存新图


image_compose()  # 调用函数
