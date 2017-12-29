#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 19 20:51:44 2017

@author: Tian
"""
import pandas as pd
import numpy as np

def load_data(day):
    
    mac_data0300=pd.read_csv('/Users/apple/Desktop/Data/store0300/macs.details.东城涡岭美宜佳.%s.csv'%day)

    return mac_data0300

def feature_instore(people):    #所有出现的人（包括路人和消费者）
    
    half_hour=pd.datetime(2015,1,1,10,40,0)-pd.datetime(2015,1,1,10,10,0)
    group=people.groupby(['MAC地址'])
    
    total_showing=[]
    for i,j in group:
        if len(j)==1:
            continue
        if len(j)>8000:  #店员
            continue
        else:
            showingtime=[]
            time=j['出现时间'].values
            time=pd.to_datetime(time)
            time=time.sort_values()
            time1=time[0]
            for t in range(len(time)):
                if t==len(time)-1:
                    time2=time[t]
                    showingtime.append([str(time1),str(time2)])
                    break
                if time[t+1]-time[t]>half_hour:
                    time2=time[t]
                    showingtime.append([str(time1),str(time2)])
                    time1=time[t+1]
    
        showingtime_dataframe=pd.DataFrame(showingtime,index=[i for a in range(len(showingtime))],\
                                                              columns=['showing time','vanish time'])
        total_showing.append(showingtime_dataframe)
    
    total_dataframe=pd.concat(total_showing)
    total_dataframe.to_csv('/Users/apple/Desktop/Data/Category_data/showing_times(instore_passby).csv')
    
    return total_dataframe

def feature_2():     #有过购买记录的人停留时间
    
    data=pd.read_csv('/Users/apple/Desktop/Data/Category_data/showing_interval.csv',index_col='Unnamed: 0')
    people=list(set(data.index))
    zero=pd.datetime(2015,1,1,10,10,0)-pd.datetime(2015,1,1,10,10,0)
    
    enter=[]
    for per in people:
        if type(data.loc[per])==pd.Series:
            show=data.loc[per]['showing_time']
            vanish=data.loc[per]['vanish_time']
            timeshow=pd.to_datetime(show)
            timevanish=pd.to_datetime(vanish)
            interval=timevanish-timeshow
            if interval==zero:
                continue
            entering=pd.DataFrame([[show,vanish,str(interval)[7:15]]],index=[per],columns=['showing time','vanish time','duration'])
            enter.append(entering)
        else:
            show=data.loc[per]['showing_time'].values
            vanish=data.loc[per]['vanish_time'].values
            timeshow=pd.to_datetime(show)
            timevanish=pd.to_datetime(vanish)
            interval=timevanish-timeshow
            interval_v=[]
            show_v=[]
            vanish_v=[]
            for a in range(len(interval)):
                if interval[a]==zero:
                    continue
                interval_v.append(str(interval[a])[7:15])
                show_v.append(show[a])
                vanish_v.append(vanish[a])
            interval=np.array([interval_v])
            show=np.array([show_v])
            vanish=np.array([vanish_v])
            entering=pd.DataFrame(np.concatenate((show.T,vanish.T,interval.T),axis=1),index=[per for t in range(len(show_v))]\
                                     ,columns=['showing time','vanish time','duration'])
            enter.append(entering)
    
    enter_dataframe=pd.concat(enter)
    enter_dataframe.to_csv('/Users/apple/Desktop/Data/Category_data/enter.csv') 

def feature_passby(sample):      #没有购买记录的人的停留时间
    
    data=pd.read_csv('/Users/apple/Desktop/Data/Category_data/showing_times(instore_passby).csv',index_col='Unnamed: 0')
    people=list(set(data.index))
    sample=sample[:,0]
    zero=pd.datetime(2015,1,1,10,10,0)-pd.datetime(2015,1,1,10,10,0)
    
    passby=[]
    for per in people:
        if per not in sample:
            if type(data.loc[per])==pd.Series:
                show=data.loc[per]['showing time']
                vanish=data.loc[per]['vanish time']
                timeshow=pd.to_datetime(show)
                timevanish=pd.to_datetime(vanish)
                interval=timevanish-timeshow
                if interval==zero:
                    continue
                passing=pd.DataFrame([[show,vanish,str(interval)[7:15]]],index=[per],columns=['showing time','vanish time','duration'])
                passby.append(passing)
            else:
                show=data.loc[per]['showing time'].values
                vanish=data.loc[per]['vanish time'].values
                timeshow=pd.to_datetime(show)
                timevanish=pd.to_datetime(vanish)
                interval=timevanish-timeshow
                interval_v=[]
                show_v=[]
                vanish_v=[]
                for a in range(len(interval)):
                    if interval[a]==zero:
                        continue
                    interval_v.append(str(interval[a])[7:15])
                    show_v.append(show[a])
                    vanish_v.append(vanish[a])
                interval=np.array([interval_v])
                show=np.array([show_v])
                vanish=np.array([vanish_v])
                passing=pd.DataFrame(np.concatenate((show.T,vanish.T,interval.T),axis=1),index=[per for t in range(len(show_v))]\
                                     ,columns=['showing time','vanish time','duration'])
                passby.append(passing)
    
    passby_dataframe=pd.concat(passby)
    passby_dataframe.to_csv('/Users/apple/Desktop/Data/Category_data/passby.csv')      

def feature_3():    #交易发生的停留时间
    
    data=pd.read_csv('/Users/apple/Desktop/Data/Category_data/transaction_time_second.csv',index_col='Unnamed: 0')
    trans=pd.read_csv('/Users/apple/Desktop/Data/Category_data/transaction_0300(商品代码).csv',index_col='交易时间')
    data=data.drop_duplicates(['transaction time'])
    
    trans_time=data['transaction time'].values
    showing=data['showing time'].values
    vanish=data['vanish time'].values
    timeshowing=pd.to_datetime(showing)
    timevanish=pd.to_datetime(vanish)
    timedelta=timevanish-timeshowing
    
    result=[]
    for i in range(len(data)):
        transtime=data['transaction time'].values[i]
        item=trans.loc[transtime]['商品代码']
        result.append([data.index[i],showing[i],trans_time[i],vanish[i],str(timedelta[i])[7:15],item])
    result_dataframe=pd.DataFrame(result,columns=['mac','showing time','transaction time','vanish time','duration','items'])
    result_dataframe.to_csv('/Users/apple/Desktop/Data/Category_data/transaction_duration.csv')

def main():
    
    data=pd.read_csv('/Users/apple/Desktop/Data/Mergedata.csv')
    data=data.drop_duplicates(['transaction_no'])
    group=data.groupby('mac')
    name=[]
    mac=[]
    for i,j in group:
        name.append(i)
        mac.append(j)
    times=[]
    for i in range(len(mac)):
        times.append([name[i],len(mac[i])])
    number=np.array(times)             #若原list里有string 则变成array全是string 无法排序
    number2=number[:,1].astype(int)
    index=np.argsort(-number2)
    sample=number[index]
    sim_dataframe=pd.DataFrame(sample,columns=['mac','times'])
    sim_dataframe.to_csv('/Users/apple/Desktop/Data/Category_data/times.csv')


    
    macdata=[]     #所有人的所有trajectory记录（包括没有merge的）
    date=pd.date_range('20150716','20150905')
    for day in date:
        day=str(day)
        macdata.append(load_data(day[:10])) 
    people=pd.concat(macdata)      #所有人的所有trajectory记录（包括没有merge的）

    feature_3()

if __name__=='__main__':
    main()