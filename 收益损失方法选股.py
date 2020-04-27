import os
import time
import baostock as bs
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# from matplotlib import pyplot as plt
#os.chdir('/Users/D_Dj/Python_projects/stock/Stock Reload')

'''sh_A = pd.read_excel('sh_A.xlsx', index_col=0)
sz_A = pd.read_excel('sz_A.xlsx', index_col=0)
cyb = pd.read_excel('cyb.xlsx', index_col=0)'''
A500 = pd.read_excel('A500.xlsx', index_col=0)
SH50 = pd.read_excel('SH50.xlsx',index_col=0)
CYB50 = pd.read_excel('CYB50.xlsx',index_col=0)
# 获取最近股票的阶段最高价和最低价
start_time = time.time()
window = 30
s_date = '2019-01-01'
e_date = (time.strftime("%Y-%m-%d", time.localtime()))
total_result = pd.DataFrame()

#### 登陆系统 ####
lg = bs.login()


def b_to_a(x):
    x_list = list(x)
    poped = []
    poped.append(x_list.pop(0))
    poped.append(x_list.pop(0))
    poped.insert(0, x_list.pop(0))
    x_str = ''.join(x_list)
    if poped == ['.', 's', 'h']:  # apple Numbers 的stock函数中沪市的股票代码为600xxxx.ss
        poped = ['.', 's', 's']
    else:
        pass
    poped_str = ''.join(poped)
    result = x_str + poped_str
    return result


def pop_3(x):
    x_list = list(x)
    for i in range(3):
        x_list.pop()
    x_list.append(',')
    x_str = ''.join(x_list)
    return x_str


def get_history_k(stock_id, s_date, e_date):
    rs = bs.query_history_k_data_plus(stock_id,
                                      "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                      start_date=s_date, end_date=e_date,
                                      frequency="d", adjustflag="2")
    # print('query_history_k_data_plus respond error_code:'+rs.error_code)
    # print('query_history_k_data_plus respond  error_msg:'+rs.error_msg)
    # print(stock_id)
    #### 打印结果集 ####
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    return result


def get_pe_pb(stock_id, s_date, e_date):
    rs = bs.query_history_k_data_plus(stock_id,
                                      "date,code,close,peTTM,pbMRQ,psTTM,pcfNcfTTM",
                                      start_date=s_date, end_date=e_date,
                                      frequency="d", adjustflag="3")

    #### 打印结果集 ####
    result_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        result_list.append(rs.get_row_data())
    result = pd.DataFrame(result_list, columns=rs.fields)
    return result


# ----------------------------------------------------------------------------------
# 处理数据
def find_low_high(result, result_pe_pb, window):
    result['close'] = pd.to_numeric(result['close'])
    result['low'] = pd.to_numeric(result['low'])
    result['high'] = pd.to_numeric(result['high'])

    result_pe_pb['peTTM'] = pd.to_numeric(result_pe_pb['peTTM'])
    result_pe_pb['pbMRQ'] = pd.to_numeric(result_pe_pb['pbMRQ'])

    result['min'] = result.low.rolling(window).min()
    result['max'] = result.high.rolling(window).max()
    result['MA200'] = result.high.rolling(200).mean()
    result = result.dropna()
    result = result.reset_index(drop=True)
    # 线性回归，计算MA200斜率
    model = LinearRegression(fit_intercept=True)
    x = pd.DataFrame(np.arange(30))
    y = pd.DataFrame(result.MA200[(len(result) - 30):(len(result))])
    model.fit(x, y)
    coefficient = model.coef_

    # 获取最近股票的阶段最高价和最低价
    # pre_low = result.low[len(result)-1]
    # pre_high = result.high[len(result)-1]
    low_list = []
    high_list = []
    for i in range(len(result) - 1, 0, -1):
        if (result.high[i] == result['max'][i]) & (result.close[i] != result.close[i - 1]):
            high_list.append(result.high[i])
        elif (result.low[i] == result['min'][i]) & (result.close[i] != result.close[i - 1]):
            low_list.append(result.low[i])

    pre_close = result.close[len(result) - 1]
    up_rate = (high_list[0] - pre_close) / pre_close
    down_rate = (pre_close - low_list[0]) / pre_close
    if down_rate == 0:
        ratio = 1000
    else:
        ratio = up_rate / down_rate
    MA200 = pre_close >= result.MA200[len(result) - 1]

    return [
        b_to_a(result.code[0]),
        ratio,
        result.close[len(result) - 1],
        high_list[0],
        low_list[0],
        up_rate,
        down_rate,
        MA200,
        result_pe_pb.peTTM[len(result_pe_pb) - 1],
        result_pe_pb.pbMRQ[len(result_pe_pb) - 1],
        coefficient[0][0]
    ]


# id,ratio,close,high,low,up_rate,down_rate,MA200,peTTM,pb,MA200斜率

# 找近期高低点函数

error_list = []
gain_lose_rate = []
stock_to_check = A500.append((SH50, CYB50))
#sh_sz_cyb = sh_A.append((sz_A, cyb))
for i in stock_to_check.stock_id:
    try:
        result = get_history_k(i, s_date, e_date)
        result_pe_pb = get_pe_pb(i, s_date, e_date)
        single_stock_result = find_low_high(result, result_pe_pb, window)
        gain_lose_rate.append(single_stock_result)
        print(i)
    except (IndexError, ValueError)as e:
        print(e)
        error_list.append([e, i])

time_stamp = (time.strftime("%m-%d-%H-%M", time.localtime()))

columns = ['id', 'ratio', 'close', 'high', 'low', 'up_rate', 'down_rate', 'MA200', 'peTTM', 'pbMRQ', 'coefficient']

df = pd.DataFrame(gain_lose_rate, columns=columns)
df_MA_True = df[(df.MA200 == True) & \
                (df.down_rate < 0.1) \
                & (df.ratio >= 3) & \
                (df.peTTM < df.peTTM.mean() * 1.3) & \
                (df.peTTM > 0) & \
                (df.pbMRQ < df.pbMRQ.mean() * 1.55)]
df_MA_True = df_MA_True.sort_values(by=['ratio'], ascending=False, axis=0)
df_MA_True = df_MA_True.reset_index(drop=True)
df_MA_True.to_excel(f'收益率-{window}窗口-{time_stamp}.xlsx')

# 把股票代码变成 000001，0000002类型------
stock_id_list = list(df_MA_True.id)
stock_id_temp = []
for i in stock_id_list:
    stock_id_temp.append(pop_3(i))
stock_id_str = ''.join(stock_id_temp)
print(stock_id_str)
print('完成任务，用时：%f' % (time.time() - start_time))
