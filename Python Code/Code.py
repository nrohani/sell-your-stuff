# -*- coding: utf-8 -*-
"""
Created on Mon Apr 15 22:49:16 2019

@author: Narjes Rohani (GreenBlueMind)
Contact me for more information: nasim.rohani74@gmail.com
"""
# This code analyse the performance of past campaigns,
#coupons, profit by countries, etc. and make data visualizing for better understanding data
#Import librarys
import pandas as pd
import numpy as np
from scipy import stats
import sqlite3 as sql
import matplotlib.pyplot as plt
import statsmodels.api as sm
import matplotlib.dates as mdates
import seaborn as sns
sns.set(style="ticks", color_codes=True)
#End of import librarys

#--------------------------------------------------------------------------------

# A function for selecting All data in the input table and return panda dataframe
def selectTable(tableName,connection):
    query = "select * from "+tableName
    data = pd.read_sql(query, connection)
    print ("Finished successfully")
    connection.close()
    return data
# End selectTable function
#--------------------------------------------------------------------------------

#Analyzing Campaigns Table
def compaignsAna(connection):
   compData=selectTable('Campaigns',connection)
   print('Head:::::::::::::',compData.head())
   print('Describtion:::::',compData.describe())
   print(compData.isnull().any().any())
   sns.distplot(compData['total_spend'])
   compData['start_date']=pd.to_datetime(compData['start_date'])
   compData['end_date']=pd.to_datetime(compData['end_date'])
   compData['len']=  compData['end_date']-compData['start_date']
   print('Compaign with max total spend:::::',compData.iloc[compData['total_spend'].argmax()])
   print('Compaign with min total spend:::::',compData.iloc[compData['total_spend'].argmin()])
   compData['len']=compData['len']/np.timedelta64(1, 'D')
   print( compData[['len','total_spend']].corr())
   sns.pairplot(compData,hue='country')
   compData = compData.set_index('start_date')
   compData['startYear'] = compData.index.year
   compData['startMonth'] = compData.index.month
   compData['startWeekday Name'] = compData.index.weekday_name
   sns.set(rc={'figure.figsize':(10, 4)})
   ax = compData.loc['2017-01':'2017-02', 'total_spend'].plot(marker='o', linestyle='-')
   ax.set_ylabel('total spend ');
   sns.boxplot(data=compData,x='startMonth',y='total_spend')
   sns.boxplot(data=compData,x='startWeekday Name',y='total_spend')
   print('WeekDay with max total spend:::::',compData.groupby('startWeekday Name').mean().sort_values(by='total_spend'))
   print('WeekDay with max total spend:::::',compData.groupby('country').mean().sort_values(by='total_spend'))
   z = np.abs(stats.zscore(compData['total_spend']))
   print(z)
   sns.barplot(x='country',y='total_spend',data=compData)
   sns.barplot(x='startWeekday Name',y='total_spend',data=compData,estimator=np.std)
   sns.countplot(x='startWeekday Name',data=compData)
   sns.violinplot(x="startWeekday Name",y='total_spend',data=compData,hue='startYear',split=True)
   sns.lmplot(x='')
#   compData.describe().to_excel('Campaignsdes.xlsx')
   sns.distplot(compData['total_spend'],kde=False,bins=30)
   sns.pairplot(compData,hue='country',size=8)
#--------------------------------------------------------------------
  
  
#Analyzing Clients Table
def clientsAna(connection):
    
    clientData=selectTable('Clients',connection)
    print(clientData.head(),clientData.describe())
    print(clientData.info())
    print(clientData.isnull().any())
    clientData['first_deposit_amount']=clientData['first_deposit_amount'].fillna(value=0)
    clientData['first_transaction_amount']=clientData['first_transaction_amount'].fillna(value=0)
    clientData['balance_amount']=clientData['balance_amount'].fillna(value=0)
    clientData['first_transaction_date']=clientData['first_transaction_date'].fillna(value="0000-00-00")
    clientData['first_deposit_date']=clientData['first_deposit_date'].fillna(value="0000-00-00")
    #clientData.to_excel("Clients.xlsx")
    z = np.abs(stats.zscore(clientData['balance_amount']))
    print(z)
    print("client with most balance:",clientData.iloc[clientData['balance_amount'].argmax()])
    print(clientData.groupby('residence').mean()['balance_amount'])
    print(clientData.groupby('type').mean()['balance_amount'])
    print(clientData.groupby('date_joined').mean()['balance_amount'])
    print(clientData.groupby('indication_coupon').mean()['balance_amount'])
    print(clientData.groupby('first_transaction_date').mean()['balance_amount'])
    print(clientData['residence'].value_counts().head(10))
    df=clientData.groupby('residence').mean()['balance_amount']
    df=pd.DataFrame(df)
    print(df.sort_values(by="balance_amount",ascending=False).head(10))
    print(clientData[['first_transaction_amount','balance_amount']].corr())
    print(clientData['first_transaction_amount'].min(),clientData['first_transaction_amount'].max())
    print(clientData['residence'].value_counts().head(10))
    print(clientData['type'].value_counts().head(10))
#    sns.distplot(clientData['balance_amount'])
#    sns.jointplot(x='first_transaction_amount',y='balance_amount',data=clientData,kind='hex')
#    sns.pairplot(clientData,hue="residence")
#    sns.rugplot(clientData['first_transaction_amount'])
#--------------------------------------------------------------------------------
#Analyzing Transaction Table

def transactionAna(connection):
    trsData=selectTable('Transactions',connection)
    print(trsData.head(),trsData.describe(),trsData.info())
    print(trsData.isnull().any())
#    sns.distplot(trsData['total_buy'].notnull())
#    sns.distplot(trsData['total_sell'].notnull())
#    sns.distplot(trsData['total_deposits'].notnull())
#    sns.distplot(trsData['total_withdrawals'].notnull())
#    sns.distplot(trsData['count_contracts'].notnull())
#    sns.distplot(trsData['count_withdrawals'].notnull())
#    sns.distplot(trsData['count_deposits'].notnull())
    trsData=trsData.fillna(value=0)
    #Who sold the most?
    print('    #Who sold the most?',trsData.groupby(["account"]).sum().sort_values("total_sell", ascending=False).head())
    #What country sold the most?
    connection =sql.connect(dbName)

    clients=selectTable('Clients',connection)
    allData=pd.merge(clients,trsData,on='account')
    print(allData.head())
    group = allData.groupby(["residence","account"]).sum()
    total_price = group["total_sell"].groupby(level=0, group_keys=False)
    print(total_price.nlargest(5))
    #------------------------
    #Who bought the most?
    print('    #Who bought the most?',trsData.groupby(["account"]).sum().sort_values("total_buy", ascending=False).head())
    #What country bought the most?
    total_price = group["total_buy"].groupby(level=0, group_keys=False)
    print(total_price.nlargest(5))
    #------------------------
    allData['transaction_date']=pd.to_datetime(allData['transaction_date'])
    allData = allData.set_index('transaction_date')
    allData['startYear'] = allData.index.year
    allData['startMonth'] = allData.index.month
    allData['startWeekday Name'] = allData.index.weekday_name
    sns.violinplot(x="startWeekday Name",y='total_sell',data=allData,hue='startYear',split=True)
    sns.barplot(x="startWeekday Name",y='total_sell',data=allData)
    sns.barplot(x="startWeekday Name",y='total_buy',data=allData)

#    trsData.head().to_excel('Transactionshead.xlsx')
#    trsData.describe().to_excel('Transactionsdes.xlsx')
#    trsData.to_excel('Transactions.xlsx')
#--------------------------------------------------------------------------------
#creat cunnection to sqlite db
dbName="Database.db"
connection =sql.connect(dbName)
#Uncomment to call functions.
#compaignsAna(connection)
#transactionAna(connection)
#transactionAna(connection)

#--------------------------------------------------------------------------------









