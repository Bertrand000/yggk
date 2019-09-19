#!/usr/bin/env python
# encoding: utf-8

import pymysql
import configparser
import re
'''

@author: Mr.Chen
@file: db_driver.py
@time: 2019/4/23 14:50

'''


class db_driver():
    cfg = configparser.ConfigParser()
    cfg.read("D:\python_project\yggk\zzzs\config.ini")
    # mysql关键字 过滤关键字
    MYSQL_KEY = ["order"]
    db = None
    def __init__(self):
        # 初始化数据库连接
        print(self.cfg.sections())
        try:
            db_host = self.cfg.get("db", "host")
            db_port = int(self.cfg.get("db", "port"))
            db_user = self.cfg.get("db", "user")
            db_pass = self.cfg.get("db", "password")
            db_db = self.cfg.get("db", "db")
            db_charset = self.cfg.get("db", "charset")
        except Exception as err:
            print("配置文件读取异常")
            print(err)
            return
        try:
            self.db = pymysql.connect(host=db_host, port=db_port, user=db_user, passwd=db_pass, db=db_db,
                                      charset=db_charset)
            self.db_cursor = self.db.cursor()
        except Exception as err:
            print("请检查数据库配置")

    # 创建表
    def create_table(self, sql):
        try:
            self.db_cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            print("------------------------------------------------------------------------------------------------------------------------------------")
            print("                                                             创建表失败")
            print("------------------------------------------------------------------------------------------------------------------------------------")
            print(e)
    # 查询（sql）
    def query(self,sql):
        try:
            self.db_cursor.execute(sql)
            self.db.commit()
            return self.db_cursor.fetchall()
        except Exception as e:
            print("------------------------------------------------------------------------------------------------------------------------------------")
            print("                                                             查询失败")
            print("------------------------------------------------------------------------------------------------------------------------------------")
            print(e)

    # 单条数据保存（sql，data）
    def save(self,sql,data):
        try:
            self.db_cursor.execute(sql, data)
            self.db.commit()
            print("------------------------------------------------------------------------------------------------------------------------------------")
            print("                                                             保存成功:")
            print(data)
            print("------------------------------------------------------------------------------------------------------------------------------------")
            return True
        except Exception as e:
            self.db.rollback()
            print(e)
            return False
    # 更新（sql，data）
    def updata(self,sql):
        try:
            self.db_cursor.execute(sql)
            self.db.commit()
            return True
        except Exception as e:
            return False
            print(e)

    def table_exists(self,table_name):
        '''
        判断表是否存在
        :param table_name:
        :return:
        '''
        sql = "show tables;"
        try:
            self.db_cursor.execute(sql)
            tables = [self.db_cursor.fetchall()]
            table_list = re.findall('(\'.*?\')', str(tables))
            table_list = [re.sub("'", '', each) for each in table_list]
            if table_name in table_list:
                return True
            return False
        except Exception as e:
            print("------------------------------------------------------------------------------------------------------------------------------------")
            print("                                                             表验证失败")
            print("------------------------------------------------------------------------------------------------------------------------------------")
            print(e)
            return True

    def count(self,table_name):
        '''
        查询表数据总数
        :param table_name:
        :return:
        '''
        sql = "select count(*) from "+table_name
        try:
            self.db_cursor.execute(sql)
            return self.db_cursor.fetchone()
        except Exception as e:
            print("------------------------------------------------------------------------------------------------------------------------------------")
            print("                                                             总数查询错误")
            print("------------------------------------------------------------------------------------------------------------------------------------")
            print(e)
            return False

    def save_dict_list(self,datas,sql):
        '''
        批量保存
        :param datas: dict数据集
        :param sql: 保存sql
        :return:
        '''
        try:
            for data in datas:
                self.db_cursor.execute(sql,tuple(data.values()))
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(e)
            return False

    def save_list(self,datas,sql):
        '''
        批量保存
        :param datas: list 数据集
        :param sql:
        :return:
        '''
        try:
            for data in datas:
                self.db_cursor.execute(sql,tuple(data))
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(e)
            return False