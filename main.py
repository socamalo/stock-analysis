import os
import time, datetime
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import baostock as bs
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from Company_class import Company

start_time = time.time()

lg = bs.login()
target = Company.hs300().append((Company.cyb50(), Company.zz500(), Company.cyb50()))
#target = Company.cyb50()

company_holder = map(Company, target)

result = []
counter = 0
for x in company_holder:
    counter += 1
    print(counter)
    try:
        result.append([x.stock_id, x.gain_lose_ratio['gain_lose_ratio'], x.gain_lose_ratio['lose_ratio'],
                       x.last_close_price, x.gain_lose_ratio['pre_high'], x.gain_lose_ratio['pre_low'],
                       x.MA50_above_MA300, x.aboveMA200_mark,  x.pe_pb['peTTM'], x.pe_pb['pbMRQ'],
                       x.coefficient_MA200
                      ])

    except (IndexError, ValueError, AttributeError)as e:
        print(e)
columns = ['id', 'ratio', 'down_ratio', 'close', 'high', 'low', 'MA50_above_MA300', 'MA200', 'peTTM', 'pbMRQ', 'coefficient']
df = pd.DataFrame(result, columns=columns)
df_filtered = df[(df.MA200 == True) & (df.down_ratio < 0.1) & (df.ratio >= 3)\
                 & (df.MA50_above_MA300 == True) \
                 #& (df.peTTM < df.peTTM.mean() * 1.5)\
                & (df.peTTM > 0) & (df.pbMRQ < df.pbMRQ.mean() * 1.55)]

df_filtered = df_filtered.sort_values(by=['ratio'], ascending=False, axis=0)
df_filtered = df_filtered.reset_index(drop=True)
df_filtered.drop_duplicates(keep='first', inplace=True) #删除重复的行

time_stamp = (time.strftime("%m-%d-%H-%M", time.localtime()))
os.chdir('/Users/D_Dj/PycharmProjects/Stock_analysis/Stock_analysis/Daily_result')
df_filtered.to_excel(f'收益率+MA50 above MA300-{time_stamp}.xlsx')

# 把股票代码变成 000001，0000002类型------
stock_id_list = list(df_filtered.id)
stock_id_temp = []
for i in stock_id_list:
    stock_id_temp.append(pop_3(b_to_a(i)))
stock_id_str = ''.join(stock_id_temp)
print(stock_id_str)
print('完成任务，用时：%f' % (time.time() - start_time))