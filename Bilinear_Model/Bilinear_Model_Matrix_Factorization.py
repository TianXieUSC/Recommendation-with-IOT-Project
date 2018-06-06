import pandas as pd
import numpy as np
import os
import re

class Bilinear_Matrix_Factorization(object):

    '''
    Initiate the parameters used in the model
    ratings: the rating data (csv form)
    feature: the feature data (csv form)
    sale: the sale data (csv form)
    Lambda_1, Lambda_2, Lambda_3: the regulation hyperparameteres for user matrix, item matrix, correlation matrix
    eTa: Iteration step
    L: Latent dimension
    K: Iteration times
    '''
    def __init__(self,rating_path,feature_path,sale_path,Lambda_1=0.01,Lambda_2=0.01,Lambda_3=0.01,eTa=0.01,L=8,K=1000):

        self.ratings=pd.read_csv(rating_path,index_col='Unnamed: 0')
        self.feature=pd.read_csv(feature_path,index_col='Unnamed: 0')
        self.sale=pd.read_csv(sale_path,index_col='Unnamed: 0')
        self.sale['所属大品类代码']=self.sale['所属大品类代码'].astype('int')
        self.sale['商品代码']=self.sale['商品代码'].astype('int')   

        # the items should both in ratings and sale
        ratings_item=set(list(self.ratings.ItemId))
        sale_item=set(list(self.sale['商品代码'].values))
        self.sale=self.sale.loc[self.sale['商品代码'].map(lambda x: x in ratings_item)]
        self.ratings=self.ratings.loc[self.ratings.ItemId.map(lambda x: x in sale_item)]

        # the user should both in ratings and feature
        ratings_user=set(list(self.ratings.UserId))
        feature_user=set(list(self.feature.UserId))
        self.ratings=self.ratings.loc[self.ratings.UserId.map(lambda x: x in feature_user)]
        self.feature=self.feature.loc[self.feature.UserId.map(lambda x: x in ratings_user)]

        # the hash table for item code and item category
        self.Hash={1:[1],2:[2,4,8,9],3:[5,6,10,12,15,17,18,30],4:[11,28],5:[13,20,21,22,23,24,25,26,27],\
            6:[14,49,50,51,52,53,54,55,56,57],7:[16,60,66,80,98]}
        self.new_item_code_word={1:'Cigarette',2:'Snack',3:'Food',4:'Alcohol',5:'Beverage',6:'Daily Use',7:'Spiritual Needs'}

        self.Lambda_1=Lambda_1
        self.Lambda_2=Lambda_2
        self.Lambda_3=Lambda_3
        self.eTa=eTa
        self.L=L
        self.K=K

    '''
    This part is for changing the elements user feature matrix into discrete variables
    '''
    def user_feature_generate(self):

        feature=self.feature
        # here are some magic numbers which need set by human

        #variance to standard deviation 
        feature['genre23']=feature.genre23.map(lambda x:np.sqrt(x))     
        feature['genre24']=feature.genre24.map(lambda x:np.sqrt(x))
        feature['genre25']=feature.genre25.map(lambda x:np.sqrt(x))
        feature['genre26']=feature.genre26.map(lambda x:np.sqrt(x))
        feature['genre27']=feature.genre27.map(lambda x:np.sqrt(x))

        #genre0 平均停留时间
        feature=feature.sort_values(by='genre0')      
        feature['genre0']=self.Bin(feature['genre0'].values) 

        #genre1  总出现次数
        result=[]       
        for i in feature['genre1'].values:
            # turn the Mac set into two
            val=list(np.zeros(2))    
            # 3 is the number that divide the mac equally
            if i<=3:
                val[0]=1
                result.append(val)
            else:
                val[1]=1
                result.append(val)
        feature['genre1']=result

        #genre2  周中出现次数
        result=[]       
        for i in feature['genre2'].values:
            val=list(np.zeros(2))
            if i<=3:
                val[0]=1
                result.append(val)
            else:
                val[1]=1
                result.append(val)
        feature['genre2']=result

        #genre3   周末出现次数
        result=[]       
        for i in feature['genre3'].values:
            val=list(np.zeros(2))
            if i<=3:
                val[0]=1
                result.append(val)
            else:
                val[1]=1
                result.append(val)
        feature['genre3']=result

        #genre4   交易次数
        result=[]       
        for i in feature['genre4'].values:
            val=list(np.zeros(2))
            if i==1:
                val[0]=1
                result.append(val)
            else:
                val[1]=1
                result.append(val)
        feature['genre4']=result

        #genre5    最长停留时间
        feature=feature.sort_values(by='genre5')   
        feature['genre5']=self.Bin(feature['genre5'].values)

        #genre6    最短停留时间
        feature=feature.sort_values(by='genre6')   
        feature['genre6']=self.Bin(feature['genre6'].values)

        #genre  7,8,9,10  在时区1，2，3，4出现次数  genre 11,12,13,14  在时区1，2，3，4平均停留时间
        for i in range(7,15):     
            genre='genre%d'%i
            result=[]
            for j in feature[genre].values:
                val=list(np.zeros(2))
                if j==0:
                    val[0]=1
                    result.append(val)
                else:
                    val[1]=1
                    result.append(val)
            feature[genre]=result


        #15  购物平均停留时间 16  路过平均停留时间  17  mac平均停留时间与总时间之比   
        for i in range(15,18):   
            genre='genre%d'%i
            feature=feature.sort_values(by=genre)
            feature[genre]=self.Bin(feature[genre].values) 

        #genre  18  同一天出现多次的天数 19,20,21,22   第一，二，三，四周的出现次数 genre 23,24,25,26 在时区1，2，3，4的停留时间标准差
        for i in range(18,27):     
            genre='genre%d'%i
            result=[]
            for j in feature[genre].values:
                val=list(np.zeros(2))
                if j==0:
                    val[0]=1
                    result.append(val)
                else:
                    val[1]=1
                    result.append(val)
            feature[genre]=result

        #  27  停留时间标准差  
        genre='genre%d'%27
        feature=feature.sort_values(by=genre)
        feature[genre]=self.Bin(feature[genre].values) 

        #genre28   最后一次出现的时间
        result=[]       
        for i in feature['genre28'].values:
            val=list(np.zeros(2))
            if i<=28:
                val[0]=1
                result.append(val)
            else:
                val[1]=1
                result.append(val)
        feature['genre28']=result

        #genre29  进店没有购物的次数
        result=[]       
        for i in feature['genre29'].values:
            val=list(np.zeros(2))
            if i==0:
                val[0]=1
                result.append(val)
            else:
                val[1]=1
                result.append(val)
        feature['genre29']=result

        #genre20    路过次数
        result=[]       
        for i in feature['genre30'].values:
            val=list(np.zeros(2))
            if i<=5:
                val[0]=1
                result.append(val)
            else:
                val[1]=1
                result.append(val)
        feature['genre30']=result

        feature['feature']=feature.genre0
        del feature['genre0']
        for i in range(1,31):
            genre='genre%d'%i
            feature['feature']+=feature[genre]
            del feature[genre]

        feature=feature.reset_index()
        del feature['index']
        feature['feature']=feature.feature.map(lambda x:np.array(x))
        feature=feature.set_index('UserId')
        # user feature csv,
        return feature


    # for continuous user feature
    def Bin(self,genre):

        length=len(genre)
        bins=np.array([0,genre[int(length/2)],genre[length-1]+1])
        output=[]

        place=np.digitize(genre,bins)
        for i in place:
            val=list(np.zeros(2))
            val[i-1]=1
            output.append(val)
        return output

    '''
    This part is for changing the elements item feature matrix into discrete variables
    '''
    def item_feature_generate(self):

        #category vector
        category={}
        count=0
        number=len(self.Hash)
        for i in sorted(self.Hash.keys()):
            category[i]=list(np.zeros(number))
            category[i][count]=1
            count+=1

        # connect 商品代码with 商品单价and 所属大品类代码
        var_1=dict(set(zip(self.sale['商品代码'],self.sale['商品单价'])))
        var_2=dict(set((zip(self.sale['商品代码'],self.sale['所属大品类代码']))))

        # chaning the dic_2 connecting 商品代码 with new item categories
        for new in self.Hash:
            for old in self.Hash[new]:
                for i in var_2:
                    if var_2[i]==old:
                        var_2[i]=new

        # connect the 商品代码 with vector
        item_price={}
        item_cat={}
        for i in set(var_1.keys()):
            item_price[i]=self.interval(var_1[i])
            item_cat[i]=category[var_2[i]]

        output=[]
        for i in item_price:
            output.append([i,item_cat[i]+item_price[i]])
        output=pd.DataFrame(output,columns=['ItemId','feature'])
        output['feature']=output.feature.map(lambda x:np.array(x))
        output=output.set_index('ItemId')
        # item feature csv
        return output

    def interval(self,p):

        # the range of the price
        # set the price into 4 interval 
        val=[0,5,10,20]
        price=list(np.zeros(4))
        price[np.digitize(p,val)-1]=1
        return price

    # seperate the ratings data into rain data and test data
    def data_process(self):

        train=self.ratings.sample(int(0.8*len(self.ratings)))
        test=self.ratings.loc[list(set(self.ratings.index)-set(train.index))]    
        users_train=set(list(train.UserId))
        items_train=set(list(train.ItemId))
        # only users and items in training set can be recommended
        test=test.loc[test.UserId.map(lambda x: x in users_train)]
        test=test.loc[test.ItemId.map(lambda x: x in items_train)]

        print('The data size for modeling')
        print('Ratings: ',self.ratings.shape)
        print('Training: ',train.shape)
        print('Testing: ',test.shape)

        # return the train set, test set
        return (train,test)

    # get the matrix of training and testing of validation
    def data_matrix(self,train,test,user_feature,item_feature):

        #rating matrix
        train_dataframe = train.pivot(index = 'UserId', columns ='ItemId', values = 'Rating').fillna(0)
        train_matrix=train_dataframe.values

        test_dataframe = test.pivot(index = 'UserId', columns ='ItemId', values = 'Rating').fillna(0)
        test_matrix = test_dataframe.values

        user_feature_matrix=[]
        for i in sorted(set(train['UserId'].values)):
            user_feature_matrix.append(list(user_feature.loc[i]['feature']))
        item_feature_matrix=[]
        for i in sorted(set(train['ItemId'].values)):
            item_feature_matrix.append(list(item_feature.loc[i]['feature']))

        #feature matirx
        user_feature_matrix=np.array(user_feature_matrix)
        item_feature_matrix=np.array(item_feature_matrix)

        return train_matrix,test_matrix,user_feature_matrix,item_feature_matrix

    # Hash the order of user and item in training data
    def Hash_train_index(self,train):

        hash_userid={}
        hash_itemid={}
        count=0
        for i in sorted(set(train['UserId'].values)):
            hash_userid[i]=count
            count+=1
        count=0
        for i in sorted(set(train['ItemId'].values)):
            hash_itemid[i]=count
            count+=1
        return (hash_userid,hash_itemid)

    # get the index of test data in train dat
    def Test_index(self,train,test):

        hash_userid,hash_itemid=self.Hash_train_index(train)
        user_select=[]
        item_select=[]
        for i in set(test['UserId'].values):
            user_select.append(hash_userid[i])
        for i in set(test['ItemId'].values):
            item_select.append(hash_itemid[i])
        return user_select,item_select

    # calculating RMSE
    def rmse(self,train_matrix,user,item,user_feature_matrix,item_feature_matrix,W,index):

        M=np.dot(user,item.T)+np.dot(user_feature_matrix,np.dot(W,item_feature_matrix.T))
        diff=M-train_matrix
        diff[index]=0
        return np.sqrt(np.sum(np.power(diff,2))/np.count_nonzero(train_matrix))

    # update the item matrix
    def update_item(self,row,item_row,user,train_matrix_row,item_feature_row,user_feature_matrix_rows,W,index):

        user=user[index]
        temp_2=train_matrix_row[index]

        temp_3=np.dot(user,item_row.T)+np.dot(user_feature_matrix_rows,np.dot(W,item_feature_row.T))-temp_2
        result=0
        for i in range(len(temp_3)):
            item_feature_row=item_feature_row.reshape(len(item_feature_row),1)
            temp_user_feature_row=user_feature_matrix_rows[i].reshape(len(user_feature_matrix_rows[i]),1)
            temp_W=np.dot(temp_user_feature_row,item_feature_row.T)
            temp_W=temp_W*temp_3[i]
            result+=user[i]*temp_3[i]
        return temp_W,result/len(temp_3)

    # update the user matrix
    def update_user(self,row,user_row,item,train_matrix_row,user_feature_row,item_feature_matrix_rows,W,index):

        item=item[index]
        temp_2=train_matrix_row[index]

        temp_3=np.dot(user_row,item.T)+np.dot(user_feature_row,np.dot(W,item_feature_matrix_rows.T))-temp_2
        result=0
        for i in range(len(temp_3)):
            user_feature_row=user_feature_row.reshape(len(user_feature_row),1)
            temp_item_feature_row=item_feature_matrix_rows[i].reshape(len(item_feature_matrix_rows[i]),1)
            temp_W=np.dot(user_feature_row,temp_item_feature_row.T)
            temp_W=temp_W*temp_3[i]
            result+=item[i]*temp_3[i]
        return temp_W,result/len(temp_3)


    # bilinear model implement
    def model_implement(self,train_matrix,test_matrix,user_feature_matrix,\
                item_feature_matrix,user_select,item_select):     

        train_rmse=[]
        validation_rmse=[]

        #Latent matrix
        user=np.random.randn(user_feature_matrix.shape[0],self.L)/5
        item=np.random.randn(item_feature_matrix.shape[0],self.L)/5
        W=np.random.randn(user_feature_matrix.shape[1],item_feature_matrix.shape[1])/5

        # record the zero ratings in training data
        index_row=[]
        index_column=[]
        for row in train_matrix:
            index_row.append(np.where(row!=0))
        for col in range(train_matrix.shape[1]):
            index_column.append(np.where(train_matrix[:,col]!=0))
        # for calculating rmse
        index_train=np.where(train_matrix==0)
        index_test=np.where(test_matrix==0)

        # record the rmse for training and validation and test set
        train_rmse=[]
        test_rmse=[]

        for i in range(self.K):
            if i%100==0:
                print('Number of Iteration: ',i)
            addition_W=0
            for row in range(len(user)):

                temp_W,temp_update=self.update_user(row,user[row],item,train_matrix[row],\
                    user_feature_matrix[row],item_feature_matrix[index_row[row]],W,index_row[row])

                addition_W+=temp_W
                user[row]-=self.eTa*(temp_update+self.Lambda_1*user[row])
            for row in range(len(item)):

                temp_W,temp_update=self.update_item(row,item[row],user,train_matrix[:,row],\
                    item_feature_matrix[row],user_feature_matrix[index_column[row]],W,index_column[row])

                addition_W+=temp_W
                item[row]-=self.eTa*(temp_update+self.Lambda_2*item[row])
            W-=self.eTa*(addition_W/np.count_nonzero(train_matrix)+self.Lambda_3*W)
            train_rmse.append(self.rmse(train_matrix,user,item,user_feature_matrix,item_feature_matrix,W,index_train)) 
            test_rmse.append(self.rmse(test_matrix,user[user_select],item[item_select],user_feature_matrix[user_select],item_feature_matrix[item_select],W,index_test)) 
        return (user,item,W,train_rmse,test_rmse)

    # model start point
    def start(self):

        # the csv form or user and item feature
        user_feature=self.user_feature_generate()
        item_feature=self.item_feature_generate()

        # train, test data and their matrix form
        train,test=self.data_process()
        train_matrix,test_matrix,user_feature_matrix,item_feature_matrix=self.data_matrix(train,test,user_feature,item_feature)

        # select the index of test data in train data
        user_select,item_select=self.Test_index(train,test)

        # model starts!!!!!
        user,item,W,train_rmse,test_rmse=self.model_implement(train_matrix,test_matrix,user_feature_matrix,\
                item_feature_matrix,user_select,item_select)

        return user,item,W,train_rmse,test_rmse,user_select,item_select

    # draw the figure of W
    def painting(self,W,f1,f2):

        g=f1/2
        fig,ax=plt.subplots()
        fig.set_size_inches(10,6)
        index=np.arange(0,2*len(new_item_code_word),2)
        bar_with=0.8
        pic=plt.bar(index,W[f1][:7],bar_with,alpha=0.6,color='r')
        pic=plt.bar(index+bar_with,W[f2][:7],bar_with,alpha=0.6,color='b')
    
        plt.legend(labels=['First Half','Second Half'],fontsize=15)
        plt.xticks(index,list(new_item_code_word.values()),rotation=-20,fontsize=15)
        plt.yticks(fontsize=10)
        plt.title('genre%d'%g,fontsize=15)
        ax.set_xlabel('Items',fontsize=15)
        ax.set_ylabel('Percentage',fontsize=15)
        plt.show()
        plt.close()













