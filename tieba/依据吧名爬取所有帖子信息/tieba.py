# -*- coding: utf-8 -*-
#author_=su
#time=2018.11.21

import requests
from random import randint
import time
from bs4 import BeautifulSoup
import json
import threading
from openpyxl import Workbook
from datetime import datetime


def get_tie_list(key):
    url='https://tieba.baidu.com/f?kw='+key+'&ie=utf-8&pn={0}'
    tie_id_list=[]
    tie_id_temporarylist=[]
    for p in range(0,24850,50):  #吧内所有帖子最后一页
        print('爬取id列表',p)
        tieurl = url.format(p)
        try:
            html=requests.get(tieurl).text
            time.sleep(randint(1,2))
            soup=BeautifulSoup(html,'lxml')
        except:
            print('获取'+key+'贴吧第'+str(p)+'错误')
            continue
        try:
            tie_list=soup.find_all(class_='j_thread_list')
        except:
            continue
        for i in tie_list:
            try:
                tie_attr=json.loads(i.attrs['data-field'])
                id=tie_attr['id']
                if id not in tie_id_list:
                    tie_id_list.append(id)
                    tie_id_temporarylist.append(id)
            except:
                break
        with open('帖子id.txt','a+',encoding='utf-8') as f:
            f.write(str(tie_id_temporarylist)+','+'\n')
        tie_id_temporarylist=[]
    return tie_id_list

def get_tie(list,key):
    datalist=[]
    tiedatalist=[]
    len_list=len(list)
    for index,m in enumerate(list):
        option={}
        dict={}
        tie_list=[]
        i=1
        for page in range(0,50):
            print('爬取第'+str(index)+'个帖子，共'+str(len_list))
            url='https://tieba.baidu.com/p/'+str(m)+'?pn='+str(page)
            try:
                html=requests.get(url).text
                time.sleep(randint(1,2))
                soup=BeautifulSoup(html,'lxml')
            except:
                print('获取帖子第'+str(page)+'页错误'+url)
                break
            try:
                amount=soup.find(class_='l_reply_num').find_all(class_='red')[-1].text
            except:
                amount=10
            try:
                dict['reply_number']=soup.find(class_='l_reply_num').find_all(class_='red')[-2].text  #帖子总回复数
            except:
                dict['reply_number']=''
            try:
                content_list=soup.find_all(class_='l_post')
                if i==1: #检测一次
                    try:
                        try:
                            dict['ba_name']=soup.find(class_='card_title_fname').text  #吧名
                        except:
                            dict['ba_name']=''
                        try:
                            option['title']=soup.find(class_='core_title_txt').attrs['title']  #发帖主题
                        except:
                            option['title']=''
                        tietime=content_list[0].find_all(class_='tail-info')[-1].text  #发帖时间
                        dict['tie_creattime']=tietime
                        date=tietime.split(' ')[0]
                        tie_time=datetime.strptime(date, "%Y-%m-%d")
                        begin_date='2018-1-1'
                        begin_date = datetime.strptime(begin_date, "%Y-%m-%d")
                        end_date='2018-10-30'
                        end_date = datetime.strptime(end_date, "%Y-%m-%d")
                        if begin_date<=tie_time<=end_date:
                            pass
                        else:
                            break

                    except:
                        dict['tie_creattime']=''
                i+=1

                for i in content_list:
                    tiedata={}
                    try:
                        tiedata['author_name']=i.find(class_='d_name').text  #用户名
                    except:
                        tiedata['author_name']=''
                    try:
                        tiedata['creat_time']=i.find_all(class_='tail-info')[-1].text  #回复时间
                    except:
                        tiedata['creat_time']=''
                    try:
                        tiedata['tie_content']=i.find(class_='d_post_content').text  #回复内容
                    except:
                        tiedata['tie_content']=''
                    tie_list.append(tiedata)
            except:
                break
            try:
                if page==int(amount)-1:
                    break
            except:
                pass
        if tie_list:
            option['content']=tie_list  #帖子内容
            option['id']=m #帖子id
            with open('帖子回复.txt','a+',encoding='utf-8') as f:
                f.write(str(option)+'\n')  #记录临时每个帖子的信息
            datalist.append(option)
        else:
            continue
        dict['title']=option['title']  #帖子主题
        dict['id']=m  #帖子id
        dict['url']='https://tieba.baidu.com/p/'+str(m) #帖子url
        with open('帖子信息.txt','a+',encoding='utf-8') as f:
            f.write(str(dict)+'\n')
        tiedatalist.append(dict)

    write_tie_excel(tiedatalist,key)
    write_information_excel(datalist,key)

def write_information_excel(list,key):
    wb = Workbook()
    ws=wb.active
    ws['A1'] = '帖子ID'
    ws['B1'] = '帖子标题'
    ws['C1'] = '用户名称'
    ws['D1'] = '回复内容'
    ws['E1'] = '回复时间'
    row=2
    col=1
    for m in list:
        content=m['content']
        for n in content:
            values=[m['id'],m['title'],n['author_name'],n['tie_content'],n['creat_time']]
            for i in values:
                ws.cell(row=row,column=col,value=i)
                col=col+1
            row=row+1
            col=1
    filename=key+'-'+"huifu.xlsx"
    wb.save(filename)


def write_tie_excel(list,key):
    wb = Workbook()
    ws=wb.active
    ws['A1'] = '标题'
    ws['B1'] = '帖子ID'
    ws['C1'] = 'url地址'
    ws['D1'] = '吧名'
    ws['E1'] = '帖子创建时间'
    ws['F1']='帖子评论数'
    row=2
    col=1
    for m in list:
        values=[m['title'],m['id'],m['url'],m['ba_name'],m['tie_creattime'],m['reply_number']]
        for i in values:
            ws.cell(row=row,column=col,value=i)
            col=col+1
        row=row+1
        col=1
    filename=key+'-'+"tie.xlsx"
    wb.save(filename)



if __name__ == '__main__':
    key='中国惊奇先生'   #吧名
    tie_id_list=get_tie_list(key)
    get_tie(tie_id_list,key)
