#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  5 19:41:44 2018

@author: Tian
"""

import pandas as pd
import numpy as np

def load_data():
    
    data=[]
    for i in range(16):
        j=i+1
        f=open('/Users/apple/Desktop/Data/Feature-vector/F%d.txt'%j,'r')
        dic=f.read()
        data.append(eval(dic))
        f.close()
    
    return data

def vector_merge(data):
    
    matrix=[]
    for per in data[0]:
        vec=[]
        vec.append(per)
        vec.append(data[0][per])
        if per in data[1]:
            vec.append(data[1][per])
        else:
            vec.append(np.nan)
        
        if per in data[2]:
            vec.append(data[2][per])
        else:
            vec.append(np.nan)
        
        if per in data[3]:
            vec.append(data[3][per])
        else:
            vec.append(np.nan)
        
        if per in data[4]:
            vec.append(data[4][per])
        else:
            vec.append(np.nan)
        
        if per in data[5]:
            vec.append(data[5][per])
        else:
            vec.append(np.nan)
        
        if per in data[6]:
            vec.append(data[6][per])
        else:
            vec.append(np.nan)
        
        if per in data[7]:
            vec.append(data[7][per])
        else:
            vec.append(np.nan)
        
        if per in data[8]:
            vec.append(data[8][per])
        else:
            vec.append(np.nan)
        
        if per in data[9]:
            vec.append(data[9][per])
        else:
            vec.append(np.nan)
        
        if per in data[10]:
            vec.append(data[10][per])
        else:
            vec.append(np.nan)
        
        if per in data[11]:
            vec.append(data[11][per])
        else:
            vec.append(np.nan)
        
        if per in data[12]:
            vec.append(data[12][per])
        else:
            vec.append(np.nan)
        
        if per in data[13]:
            vec.append(data[13][per])
        else:
            vec.append(np.nan)
        
        if per in data[14]:
            vec.append(data[14][per])
        else:
            vec.append(np.nan)
        
        if per in data[15]:
            vec.append(data[15][per])
        else:
            vec.append(np.nan)
        
        matrix.append(vec)
    
    matrix_dataframe=pd.DataFrame(matrix,columns=['mac','Feature_1','Feature_2','Feature_3','Feature_4'\
                                                  ,'Feature_5','Feature_6','Feature_7','Feature_8','Feature_9'\
                                                  ,'Feature_10','Feature_11','Feature_12',\
                                                  'Feature_13','Feature_14','Feature_15','Feature_16'])
    matrix_dataframe.to_csv('/Users/apple/Desktop/Data/Feature-vector/Feature_vector.csv')

def main():
    
    data=load_data()
    vector_merge(data)
    
    
if __name__=='__main__':
    main()