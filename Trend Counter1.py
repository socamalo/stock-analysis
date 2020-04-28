#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 22 19:02:10 2020

@author: D_Dj
"""


import baostock as bs
import pandas as pd
from matplotlib import pyplot as plt


#stock_id = 'sh.600183'#生益科技
#stock_id = 'sz.300197'#铁汉生态
#stock_id = 'sh.603806'#福斯特
#stock_id = 'sh.600703'#三安光电
stock_id = 'sh.600703'#三安光电



#stock_id = 'sz.000063'中兴
#stock_id = 'sz.000876'#新希望

window = 20
s_date='2010-11-01'


#### 登陆系统 ####
lg = bs.login()
# 显示登陆返回信息
print('login respond error_code:'+lg.error_code)
print('login respond  error_msg:'+lg.error_msg)

#### 获取沪深A股历史K线数据 ####
# 详细指标参数，参见“历史行情指标参数”章节；“分钟线”参数与“日线”参数不同。
# 分钟线指标：date,time,code,open,high,low,close,volume,amount,adjustflag
rs = bs.query_history_k_data_plus(stock_id,
    "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
    start_date=s_date, end_date='2020-04-01',
    frequency="d", adjustflag="2")
print('query_history_k_data_plus respond error_code:'+rs.error_code)
print('query_history_k_data_plus respond  error_msg:'+rs.error_msg)

#### 打印结果集 ####
data_list = []
while (rs.error_code == '0') & rs.next():
    # 获取一条记录，将记录合并在一起
    data_list.append(rs.get_row_data())
result = pd.DataFrame(data_list, columns=rs.fields)

#----------------------------------------------------------------------------------
#处理数据
#result['SMA'] = result.close.rolling(window).mean()
result['close'] = pd.to_numeric(result['close'])
result['low'] = pd.to_numeric(result['low'])
result['high'] = pd.to_numeric(result['high'])


result['min'] = result.low.rolling(window,center=True).min()
result['max'] = result.high.rolling(window,center=True).max()

#result['close'] = result['close'].apply(lambda x: round(x,2))

result = result.dropna()
result = result.reset_index(drop=True)
#数趋势-------------------------------------=---------------------------------------
pre_low = result.low[0]
pre_high = result.high[0]


result_trend_counter = []
length = 1

for i in range(1,len(result)):
    if (result.low[i] == result['min'][i]) & (result.close[i] != result.close[i-1]):
        trend_rate = (pre_high - result.low[i])/pre_high
        trend_point= pre_high - result.low[i]
        trend_len = length
        trend_mark = 'down'
        pre_low = result.low[i]
        length = 1
        result_trend_counter.append([trend_mark,trend_len,trend_rate,result['date'][i],pre_low,trend_point])
    elif (result.high[i] == result['max'][i]) & (result.close[i] != result.close[i-1]):
        trend_rate = (result.high[i] - pre_low)/pre_low
        trend_point= result.high[i] - pre_low
        trend_len = length
        trend_mark = 'up'
        pre_high = result.high[i]
        length = 1
        result_trend_counter.append([trend_mark,trend_len,trend_rate,result['date'][i],pre_high,trend_point])
    else:
        length += 1

'''
result_trend_counter = []
length = 1


pre_value = result['SMA'][0]
for i in range(2,len(result)):
               if (result['SMA'][i-1]>result['SMA'][i-2]) & (result['SMA'][i]>result['SMA'][i-1]):#11
                   length += 1
               elif (result['SMA'][i-1]>result['SMA'][i-2]) & (result['SMA'][i]<result['SMA'][i-1]):#10
                   trend_rate = (result['SMA'][i-1]-pre_value)/pre_value
                   trend_len = length
                   trend_mark = 'up'
                   pre_value = result['SMA'][i-1]
                   length = 1
                   result_trend_counter.append([trend_mark,trend_len,trend_rate])
               elif (result['SMA'][i-1]<result['SMA'][i-2]) & (result['SMA'][i]<result['SMA'][i-1]):#00
                   length +=1
               elif (result['SMA'][i-1]<result['SMA'][i-2]) & (result['SMA'][i]>result['SMA'][i-1]):#01
                   trend_rate = (pre_value-result['SMA'][i-1])/pre_value
                   trend_len = length
                   trend_mark = 'down'
                   pre_value = result['SMA'][i-1]
                   length = 1
                   result_trend_counter.append([trend_mark,trend_len,trend_rate])
               else:
                   length += 1
'''

'''
# 隔一天，效果不好
for i in range(5,len(result)):
    if (result['SMA'][i-5]<result['SMA'][i-3]) & (result['SMA'][i-3]>result['SMA'][i]): #10
        trend_rate = (result['SMA'][i-3]-pre_value)/pre_value
        trend_len = length
        trend_mark = 'up'
        pre_value = result['SMA'][i-3]
        length = 1
        result_trend_counter.append([trend_mark,trend_len,trend_rate])
    elif (result['SMA'][i-5]>result['SMA'][i-3]) & (result['SMA'][i-3]<result['SMA'][i]): #01 '0'代表下跌 
        trend_rate = (pre_value-result['SMA'][i-3])/pre_value
        trend_len = length
        trend_mark = 'down'
        pre_value = result['SMA'][i-3]
        ength = 1
        result_trend_counter.append([trend_mark,trend_len,trend_rate])
    else:
        length += 1

pre_apex = 0
change_rate = 0.01# 变化阈值
#5个比较，不准确
for i in range(5,len(result)):
    if (result['SMA'][i-5]<result['SMA'][i-4]) & (result['SMA'][i-4]<result['SMA'][i-3]) & (result['SMA'][i-3]>result['SMA'][i-2]) & (result['SMA'][i-2]>result['SMA'][i-1]) & (  result['SMA'][i-1] > result['SMA'][i]): #11000
        trend_rate = (result['SMA'][i-3]-pre_value)/pre_value
        trend_len = length
        trend_mark = 'up'
        pre_value = result['SMA'][i-3]
        length = 1
        result_trend_counter.append([trend_mark,trend_len,trend_rate])
    elif (result['SMA'][i-5]>result['SMA'][i-4]) & (result['SMA'][i-4]>result['SMA'][i-3]) & (result['SMA'][i-3]<result['SMA'][i-2]) & (result['SMA'][i-2]<result['SMA'][i-1]) & (  result['SMA'][i-1] < result['SMA'][i]):#00111 '0'代表下跌 
        trend_rate = (pre_value-result['SMA'][i-3])/pre_value
        trend_len = length
        trend_mark = 'down'
        pre_value = result['SMA'][i-3]
        ength = 1
        result_trend_counter.append([trend_mark,trend_len,trend_rate])
    else:
        length += 1
        

               if (result['SMA'][i-1]>result['SMA'][i-2]) & (result['SMA'][i]>result['SMA'][i-1]):#11
                   length += 1
               elif (result['SMA'][i-1]>result['SMA'][i-2]) & (result['SMA'][i]<result['SMA'][i-1]):#10
                   trend_rate = (result['SMA'][i-1]-pre_value)/pre_value
                   trend_len = length
                   trend_mark = 'up'
                   pre_value = result['SMA'][i-1]
                   length = 1
                   result_trend_counter.append([trend_mark,trend_len,trend_rate])
               elif (result['SMA'][i-1]<result['SMA'][i-2]) & (result['SMA'][i]<result['SMA'][i-1]):#00
                   length +=1
               elif (result['SMA'][i-1]<result['SMA'][i-2]) & (result['SMA'][i]>result['SMA'][i-1]):#01
                   trend_rate = (pre_value-result['SMA'][i-1])/pre_value
                   trend_len = length
                   trend_mark = 'down'
                   pre_value = result['SMA'][i-1]
                   length = 1
                   result_trend_counter.append([trend_mark,trend_len,trend_rate])
               else:
                   length += 1
#------------------------------------------------------------

for i in range(12,len(result)):
               if (result['SMA'][i-1]>result['SMA'][i-2]) & (result['SMA'][i]>result['SMA'][i-1]):#11
                   length += 1
               elif (result['SMA'][i-1]>result['SMA'][i-2]) & (result['SMA'][i]<result['SMA'][i-1]):#10
                   trend_rate = (result['SMA'][i-1]-pre_value)/pre_value
                   trend_len = length
                   trend_mark = 'up'
                   pre_value = result['SMA'][i-1]
                   length = 1
                   result_trend_counter.append([trend_mark,trend_len,trend_rate])
               elif (result['SMA'][i-1]<result['SMA'][i-2]) & (result['SMA'][i]<result['SMA'][i-1]):#00
                   length +=1
               elif (result['SMA'][i-1]<result['SMA'][i-2]) & (result['SMA'][i]>result['SMA'][i-1]):#01
                   trend_rate = (pre_value-result['SMA'][i-1])/pre_value
                   trend_len = length
                   trend_mark = 'down'
                   pre_value = result['SMA'][i-1]
                   length = 1
                   result_trend_counter.append([trend_mark,trend_len,trend_rate])
               else:
                   length += 1
         
for i in range(12,len(result)):
               if (result['SMA'][i-1]>=result['SMA'][i-2]) & (result['SMA'][i]>=result['SMA'][i-1]):#11
                   length += 1
               elif (result['SMA'][i-1]>=result['SMA'][i-2]) & (result['SMA'][i]<result['SMA'][i-1]):#10
                   trend_rate = (result['SMA'][i-1]-pre_value)/pre_value
                   trend_len = length
                   trend_mark = 'up'
                   pre_value = result['SMA'][i-1]
                   length = 1
                   result_trend_counter.append([trend_mark,trend_len,trend_rate])
               elif (result['SMA'][i-1]<result['SMA'][i-2]) & (result['SMA'][i]<result['SMA'][i-1]):#00
                   length +=1
               elif (result['SMA'][i-1]<result['SMA'][i-2]) & (result['SMA'][i]>=result['SMA'][i-1]):#01
                   trend_rate = (pre_value-result['SMA'][i-1])/pre_value
                   trend_len = length
                   trend_mark = 'down'
                   pre_value = result['SMA'][i-1]
                   length = 1
                   result_trend_counter.append([trend_mark,trend_len,trend_rate])
                     
       
'''  
                   
tc_df = pd.DataFrame(result_trend_counter,columns=['mark','len','rate','date','close','point'])
tc_df.rate = tc_df['rate'].apply(lambda x:round(x,1))
tc_df.point = tc_df['point'].apply(lambda x:round(x,0))

tc_df_up = tc_df[tc_df.mark == 'up']
tc_df_down = tc_df[tc_df.mark == 'down']

point_count_up = tc_df_up.groupby('point').count()
point_count_down = tc_df_down.groupby('point').count()

plt.plot(point_count_up,color='red')
plt.plot(point_count_down,color='blue')


up_rate_p = tc_df_up.groupby('rate').count()
down_rate_p = tc_df_down.groupby('rate').count()
up_len_p = tc_df_up.groupby('len').count()
down_len_p = tc_df_down.groupby('len').count()
up_len_p['p'] = up_len_p.mark.apply(lambda x: x/up_len_p.mark.sum())
down_len_p['p'] = down_len_p.mark.apply(lambda x: x/down_len_p.mark.sum())
up_rate_p['p'] = up_rate_p.mark.apply(lambda x: x/up_rate_p.mark.sum())
down_rate_p['p'] = down_rate_p.mark.apply(lambda x: x/down_rate_p.mark.sum())
len_plot = plt.figure( '%s Trend Rate & length'%stock_id)
ax1 = plt.subplot(211)
ax1.plot(up_rate_p.p,color='red')
ax1.plot(down_rate_p.p,color='blue')
ax2 = plt.subplot(212)
ax2.plot(up_len_p.p,color='red')
ax2.plot(down_len_p.p,color='blue')

tc_count = tc_df.groupby(['mark','rate'])[['len','rate']].count()
tc_mean = tc_df.groupby(['mark','rate'])[['len','rate']].mean().round()
print(tc_count,tc_mean)
#plt.plot(up_len_p.p)

'''                 
      
df.groupby('Rate').count()
result_df['New Rate'] = result_df['Rate'].apply(lambda x:round(x,2))
result_droped = result.dropna()

'''