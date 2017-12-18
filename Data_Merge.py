#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 19:41:54 2017

@author: Tian
"""

import pandas as pd
import numpy as np


def load_transaction():
    
    sales_data0300=pd.read_csv('/Users/apple/Desktop/Data/sales_data_store0300.csv')
    
    return sales_data0300

def load_data(day):
    
    mac_data0300=pd.read_csv('/Users/apple/Desktop/Data/store0300/macs.details.东城涡岭美宜佳.%s.csv'%day)

    return mac_data0300

def data_filter(data):
    
    group=data.groupby(['MAC地址'])
    
    mac=[]
    traj=[]
    for i,j in group:     #按照阈值-56筛选是否进店
        thre=np.array([-56 for i in range(len(j['信号强度'].values))])
        if (j['信号强度'].values>thre).any():        #只要有一个小于-56就对应进店
            mac.append(i)
            traj.append(j)  
            
    passby=pd.datetime(2015,1,1,12,00,10)-pd.datetime(2015,1,1,8,00,10) 
    #定义大于一小时的人是多次路过或者是店员
    enter=pd.datetime(2015,1,1,10,10,10)-pd.datetime(2015,1,1,10,5,10)  
    #有些data虽然信号强度小于-56，但是其时间过短，定义为路人
    
    
    for i in range(len(mac)-1,-1,-1):
        
        val=traj[i].sort_values(by='出现时间')
        
        last=len(traj[i]['出现时间'])-1    
        time1=pd.to_datetime(val['出现时间'].values[0])
        time2=pd.to_datetime(val['出现时间'].values[last])
        interval=time2-time1
        
        if interval>passby:   #出现时间长于两小时的去除,无法排除一天之内多次进店的人

            mac.pop(i)
            traj.pop(i)
            
        elif interval<enter:  #出现时间小于5分钟的去除
            mac.pop(i)
            traj.pop(i)
    
    return (mac,traj)

def merge(traj,trans):
    
    trade=trans['交易时间'].values
    trade=list(set(trade))
    trade.sort()
    
    zero=pd.datetime(2015,1,1,10,10,0)-pd.datetime(2015,1,1,10,10,0)
    sixty_seconds=pd.datetime(2015,1,1,10,11,0)-pd.datetime(2015,1,1,10,10,0)
    
    sort_traj=traj.sort_values(by='出现时间')   #排序索引会跟着改变
    
    merge=[]
    count=0
    for j in range(len(trade)):
        time0=pd.to_datetime(trade[j])
        people=str()
        true_people=str()
        minitime=pd.datetime(2015,1,1,10,12,0)-pd.datetime(2015,1,1,10,10,0)
        for i in range(count,len(sort_traj)):
            time1=pd.to_datetime(sort_traj['出现时间'].values[i])
            if sixty_seconds>time0-time1>zero and time0-time1<minitime:             #在交易时间前后60s内的人与此次交易对应
                people=sort_traj['MAC地址'].values[i]                  
                minitime=time0-time1
            elif sixty_seconds>time1-time0>zero and sort_traj['MAC地址'].values[i]==people:
                true_people=sort_traj['MAC地址'].values[i]
                break
            elif time1-time0>sixty_seconds:
                break
        if i>100:          #从此次交易之前再次进行检索
            count=i-100
        if true_people==str():    
            merge.append([str(time0),np.nan])
        else:
            people1=[true_people]
            merge.append([str(time0),people1])
            
    result=pd.DataFrame(merge,columns=['transaction','people'])
    result.to_csv('/Users/apple/Desktop/Data/Merge_data.csv')
    
def main():
    
    macdata=[]
    Fdata=[]
    Fdata_name=[]

    
    date=pd.date_range('20150716','20150905')
    for day in date:
        day=str(day)
        macdata.append(load_data(day[:10])) 
    people=pd.concat(macdata)
    
    for i in macdata:     #按天筛选数据
        per_day=data_filter(i)
        Fdata_name.append(per_day[0])
        Fdata.extend(per_day[1])
    
    Mac_data=pd.concat(Fdata)        
    trans_data=load_transaction()   
    #把进店的顾客统计出来，未加transaction data

    merge(people,trans_data)
    
if __name__=='__main__':
    main()