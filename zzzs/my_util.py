#!/usr/bin/env python
# encoding: utf-8
from zzzs import db_driver
import configparser

'''

@author: Mr.Chen
@file: my_util.py
@time: 2019/4/19 14:47

'''

class my_util():
    config = configparser.ConfigParser()
    config.read("D:\python_project\yggk\zzzs\config.ini")
    db = None
    headers_like = None
    headers_wenke = None
    # 金榜路与志愿通数据库对应关系
    jbl_zyt_colname = {
        "collegeHistoryID":"yx_id"
        ,"matricDiffYear":"nianfen"
        ,"moveDocGrade":"diaodangfen"
        ,"averageGrade":"pingjunfen"
        ,"moveDocLocation":"diaodangfenweici"
        ,"averageLocation":"pingjunfenweici"
        ,"moveDocGradeDiff":"diaodangxiancha"
        ,"averageGradeDiff":"pingjunxiancha"
        ,"hasPower":"youxiaoli"
        ,"collegeCode":"yuanxiaodaima"
        ,"publisher":"shangchuanren"
        ,"publishDate":"shangchuanshijian"
        ,"collegeHistoryBaseId":"ID"
        ,"gradeDiffLevel":"luqucengci"
        ,"order_1":"pici"
        ,"subject_1":"kelei"
        ,"collegeName":"gaoxiaomingcheng"
        ,"province":"shengfen"
        ,"collegeCount":"kaisheyuanxiaoshu"
        ,"specialtyCode":"zhuanyeid"
        ,"specialtyComment":"zhuanyejibie"
        ,"specialtyPlace":"zhuanyemingci"
        # 专业计划代码
        ,"speicaltyName":"zhuanyemingcheng"
        ,"planCollegeId":"jh_ID"
        ,"collegeCode":"yuanxiaodaima"
        ,"speicaltyName":"zhuanyemingcheng"
        ,"specialtyCategoryName":"zhuanyemenleimingcheng"
        ,"specialtyPlanTotal":"jihuashu"
        ,"studyLength":"xuezhi"
        ,"studyLanguage":"yuzhongxianzhi"
        ,"sexy":"xingbiexianzhi"
        ,"otherRequire":"qita"
        ,"specialtyPlanCode":"zhuanyedaima"
        ,"specialtyComment":"zhuanyeshuoming"
        ,"year":"nianfen"
        ,"studyMoney":"xuefei"
        ,"specialtyCategoryID":"zhuanyemenleidaima"
        ,"planComment":"jihuashuoming"
        # end
    }
    def __init__(self):
        # 创建数据驱动对象
        self.db = db_driver.db_driver()
        # 读取 headers

    def job_table_create(self,table_name):
        '''
        创建工作表 生成字段全为varchar(255)
        :param table_name:表名
        :param data:样本数据
        :return:
        '''
        if self.db.table_exists(table_name):
            print("创建工作表失败:表'" + table_name + "'已存在")
            return
        sql = "CREATE TABLE " + table_name + "(url varchar(255),status varchar(255),keypoint varchar(255))"
        try:
            self.db.create_table(sql)
        except Exception as e:
            print(e)

    def table_read(self,table_name,coulmns,keywhere = None):
        '''
        读取指定表指定字段
        :param table_name:  表名
        :param coulmn:[]   字段名,可为*
        :param keywhere 筛选条件
        :return:[]
        '''
        insert_coulmn = ""
        if coulmns=="*":
            insert_coulmn = "*"
        else:
            for coulmn in coulmns:
                insert_coulmn = insert_coulmn + coulmn  + ","
            insert_coulmn = insert_coulmn.rstrip(",")
        query_sql = "SELECT " + insert_coulmn + " FROM "+ table_name
        if keywhere:
            query_sql = query_sql + " where " + keywhere
        return self.db.query(query_sql)

    def loading_job_table(self,table_name):
        sql = "SELECT url,keypoint FROM %s where status='0' ORDER BY keypoint"%table_name
        return self.db.query(sql)

    def job_table_init(self,job_table_name,keypoints,url_temple):
        '''
        初始化工作表
        :param job_table_name:
        :param keypoints:
        :param url_temple:
        :return:
        '''
        if self.db.count(job_table_name)[0]:
            print("工作表已完成初始化")
            return
        init_url_sql = "INSERT INTO " + job_table_name + "(url,status,keypoint)VALUES"
        for keypoint in keypoints:
            url = url_temple % keypoint[0]
            sql_data = "('%s','0','%s')," % (url, keypoint[0])
            init_url_sql += sql_data
        # 去除末尾逗号
        init_url_sql = init_url_sql.rstrip(",")
        self.db.updata(init_url_sql)

    def table_create(self,table_name,json_data):
        '''
        创建数据表
        :param sql:
        :param json_data:
        :return:
        '''
        if self.db.table_exists(table_name):
            print("表'" + table_name + "'已存在")
            return
        create_table_sql = "CREATE TABLE "+table_name+"(%s)"
        column_list = dict(json_data).keys()

        # 根据对应关系将金榜路字段转换为志愿通字段
        column_list = [self.jbl_zyt_colname[i] if i in self.jbl_zyt_colname else i for i in column_list]

        column_str = ''
        for column in column_list:
            if column in self.db.MYSQL_KEY:
                column = column + "_1"
            column_str += column + " varchar(255),"
        try:
            self.db.create_table(create_table_sql % (column_str.rstrip(",")))
            print("自动创建表成功")
        except Exception as e:
            print("自动创建表失败，请检查生成的sql")
            print(e)

    def sql_create(self,table_name,json_data):
        '''
        生成sql
        :param table_name:
        :param json_data:
        :return:
        '''
        sql = '''REPLACE INTO
                                                                                  '''+table_name+'''(%s)
                                                                                  VALUES(%s)
                                                                                  '''
        column_list = dict(json_data).keys()

        # 根据对应关系将金榜路字段转换为志愿通字段
        column_list = [self.jbl_zyt_colname[i] if i in self.jbl_zyt_colname else i for i in column_list]

        column_str = ''
        values_str = ''
        for column in column_list:
            if column in self.db.MYSQL_KEY:
                column = column + "_1"
            column_str += (column + ',')
            values_str += '%s,'

        return sql % (column_str.rstrip(','), values_str.rstrip(','))

    def save_data(self,sql,data):
        '''
        保存数据
        :param sql:
        :param data:
        :return: 返回保存是否成功
        '''
        return self.db.save(sql, tuple(data))

    def updata_job_table(self,job_table_name,code):
        '''
        更新工作表记录
        :param table_name: 工作表名
        :param code: 信息
        :return:
        '''
        log_sql = '''UPDATE 
                                    %s SET status=1 
                                    where keypoint=%s''' % (job_table_name,code)
        return self.db.updata(log_sql)


    def save_dict_list(self,sql,datas):
        '''
        批量保存
        :param sql:
        :param datas:
        :return:
        '''
        return self.db.save_dict_list(datas,sql)

