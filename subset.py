#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 19:13:44 2017

@author: Tian
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def load_data(day):
    
    mac_data0300=pd.read_csv('/Users/apple/Desktop/Data/store0300/macs.details.东城涡岭美宜佳.%s.csv'%day)

    return mac_data0300

def drawing(show):
    
    fig,ax=plt.subplots()
    time=[1 for i in range(len(show))]
    ax.scatter(show,time,color='b')
    
    plt.xticks(show)
    plt.show()

def feature_instore(people):
    
    half_hour=pd.datetime(2015,1,1,10,40,0)-pd.datetime(2015,1,1,10,10,0)
    sixty_seconds=pd.datetime(2015,1,1,10,11,0)-pd.datetime(2015,1,1,10,10,0)
    group=people.groupby(['MAC地址'])
    
    total_showing=[]
    for i,j in group:
        thre=np.array([-56 for intensity in range(len(j))])
        if not (j['信号强度'].values>thre).any():
            continue
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
                    if time2-time1>sixty_seconds:
                        showingtime.append([str(time1),str(time2)])
                    break
                if time[t+1]-time[t]>half_hour:
                    if time[t]-time1>sixty_seconds:
                        time2=time[t]
                        showingtime.append([str(time1),str(time2)])
                        time1=time[t+1]
                    else:
                        time1=time[t+1]       #更改初始时间
    
        showingtime_dataframe=pd.DataFrame(showingtime,index=[i for a in range(len(showingtime))],\
                                                              columns=['showing time','vanish time'])
        total_showing.append(showingtime_dataframe)
    
    total_dataframe=pd.concat(total_showing)
    total_dataframe.to_csv('/Users/apple/Desktop/Data/Category_data/total_showing_times.csv')
    

def feature_trans_show_second(sample,show,trans):      #把每次交易与对应的时间间隔相对应
    
    half_hour=pd.datetime(2015,1,1,10,40,0)-pd.datetime(2015,1,1,10,10,0)  #定义时间间隔为半小时
    
    total_merge=[]
    for i in range(len(sample)):
        merge=[]
        time=list(trans[i])
        time.extend(list(show[i]))
        time=np.array(time)
        time=pd.to_datetime(time)
        time=time.sort_values()
        transi=pd.to_datetime(trans[i])
        for j in range(len(time)):
            if time[j] in transi:
                time1=0
                time2=0
                for mom in range(j,-1,-1):
                    if mom==0:
                        time1=time[mom]
                        break
                    if time[mom]-time[mom-1]>half_hour:   
                        time1=time[mom]
                        break
                for mom in range(j,len(time)):
                    if mom==len(time)-1:
                        time2=time[mom]
                        break
                    if time[mom+1]-time[mom]>half_hour:
                        time2=time[mom]
                        break
                merge.append([str(time1),str(time[j]),str(time2)])
        
        merge_dataframe=pd.DataFrame(merge,index=[sample[i][0] for a in range(len(merge))],\
                                                  columns=['showing time','transaction time','vanish time'])
        total_merge.append(merge_dataframe)
    
    total_dataframe=pd.concat(total_merge)
    total_dataframe.to_csv('/Users/apple/Desktop/Data/Category_data/transaction_time_second.csv')  
                
def feature_trans_show(sample,trans):   #把每次交易与对应的时间间隔相对应
    
    showing_interval=pd.read_csv('/Users/apple/Desktop/Data/Category_data/showing_interval.csv',index_col='Unnamed: 0')
    total_merge=[]
    
    for i in range(len(sample)):   #mac地址
        
        merge=[]
        time=showing_interval.loc[sample[i][0]].values
        for moment in trans[i]:    #交易时间
            moment=pd.to_datetime(moment)
            if type(showing_interval.loc[sample[i][0]])==pd.Series:      #元素可能为Series!
                time1=pd.to_datetime(time)
                if time1[0]<moment<time1[1]:
                    merge.append([str(time1[0]),str(moment),str(time1[1])])
            else:
                for j in range(len(time)):   #每个人出现的时间
                    time1=pd.to_datetime(time[j])
                    if time1[0]<moment<time1[1]:
                        merge.append([str(time1[0]),str(moment),str(time1[1])])        
        merge_dataframe=pd.DataFrame(merge,index=[sample[i][0] for a in range(len(merge))],\
                                                  columns=['showing time','transaction time','vanish time'])
        total_merge.append(merge_dataframe)
    
    total_dataframe=pd.concat(total_merge)
    total_dataframe.to_csv('/Users/apple/Desktop/Data/Category_data/transaction_time.csv')
    
def feature_showing_time(sample,show):   #每一次出现的时间间隔
    
    half_hour=pd.datetime(2015,1,1,10,40,0)-pd.datetime(2015,1,1,10,10,0)   #间隔为半小时
    
    showing_times=[]   #每一项对应每一个人的出现时间
    for i in range(len(sample)):
        per_showing=[]
        time=pd.to_datetime(show[i])
        time=time.sort_values()
        time1=time[0]
        for j in range(len(time)):
            if j+1==len(time):
                break
            if time[j+1]-time[j]>half_hour:
                per_showing.append([time1,time[j]])
                time1=time[j+1]
        if per_showing==[]:
            per_showing.append([time[0],time[len(time)-1]])
        per_dataframe=pd.DataFrame(per_showing,index=[sample[i][0] for t in range(len(per_showing))],\
                                                      columns=['showing_time','vanish_time'])
        showing_times.append(per_dataframe)
    
    showing_dataframe=pd.concat(showing_times)
    showing_dataframe.to_csv('/Users/apple/Desktop/Data/Category_data/showing_interval.csv')

def feature_generation(sample,show):     #出现次数 每一项与sample相对应
    
    half_hour=pd.datetime(2015,1,1,10,40,0)-pd.datetime(2015,1,1,10,10,0)  #半小时
    
    showing_times=[]
    for i in range(len(sample)):
        count=0
        time=pd.to_datetime(show[i])
        time=time.sort_values()
        for j in range(len(time)):
            if j+1==len(time):
                break
            if time[j+1]-time[j]>half_hour:
                count+=1
        if count==0:
            showing_times.append(1)
        else:
            showing_times.append(count)
        
    show_dataframe=pd.DataFrame(showing_times,sample[:,0],columns=['showing_time'])
    show_dataframe.to_csv('/Users/apple/Desktop/Data/Category_data/showing_times.csv')
        

def data_output(sample,show,trans):
    
    person=[]
    for i in range(len(sample)):
        person.append(pd.Series([sample[i][0],list(show[i]),list(trans[i])],\
                      index=['mac','showing','transaction']))
        
    result=pd.concat(person,axis=1)
    result=result.T
    result.to_csv('/Users/apple/Desktop/Data/Category_data/trajectory.csv')
    
    
def trajectory(sample,show):
    
    one_hour=pd.datetime(2015,1,1,11,10,0)-pd.datetime(2015,1,1,10,10,0)
    
    traj=[]
    showing_times=[]
    for i in range(len(sample)):
        count=0
        time=pd.to_datetime(show[i])
        mac=[sample[i][0] for m in range(len(show[i]))]
        merge=pd.DataFrame(time,index=mac,columns=['showing'])
        merge.sort_values(by='showing',inplace=True)
        traj.append(merge)
        
        time=merge.loc[sample[i][0]].values
        for j in range(len(time)):
            if j+1==len(time):
                break
            if time[j+1]-time[j]>one_hour:
                count+=1
        showing_times.append(count)
    print(showing_times)
        
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

    
    sales_data0300=pd.read_csv('/Users/apple/Desktop/Data/Category_data/transaction_0300(商品代码).csv')
    
    time_index=sales_data0300.set_index('交易时间')   #所有的交易时间（包括没有merge的）
    mac_index=people.set_index('MAC地址')      #所有人的所有trajectory记录（包括没有merge的）
    trans_index=data.set_index('mac')      #merge之后的记录
        
    show=[]   #总共出现时间（是merge之后的人对应的所有轨迹） 每一项分别按顺序对应sample中每一个人
    trans=[]  #总共交易记录（merge之后的数据） 每一项分别按顺序对应sample中每一个人
    for i in sample:
        val1=mac_index.loc[i[0]]
        if type(val1)==pd.Series:
            show.append(np.array([val1['出现时间']]))
        else:
            show.append(val1['出现时间'].values)
        
        val2=trans_index.loc[i[0]]
        if type(val2)==pd.Series:
            trans.append(np.array([val2['time']]))
        else:
            trans.append(trans_index.loc[i[0]]['time'].values)
    
    feature_trans_show_second(sample,show,trans)
    feature_showing_time(sample,show)   #生成两个feature
    feature_generation(sample,show)
    feature_trans_show(sample,trans)   #将transaction的时间和出现区间相对应
    feature_instore(people)    #归类出所有进店人的出现-消失时间
    print('generation done')
    
    trans_goods=[]   #个人消费basket
    for i in range(len(sample)):
        people=[]
        items=[]
        people.append(sample[i][0])
        for j in trans[i]:
            items.extend([time_index.loc[j]['商品代码']])
        people.append(items)
        trans_goods.append(people)
    
    data_output(sample,show,trans)
    
    trans_goods=pd.DataFrame(trans_goods,columns=['MAC','Items'])
    trans_goods.to_csv('/Users/apple/Desktop/Data/Category_data/basket.csv')
    
if __name__=='__main__':
    main()