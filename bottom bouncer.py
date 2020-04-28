import os
import time
import baostock as bs
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


start_time = time.time()
window = 30
start_date = '2019-01-01'
end_date = (time.strftime("%Y-%m-%d", time.localtime()))


def get_history_k(stock_id, s_date=start_date, e_date=end_date):
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


os.chdir('/Users/D_Dj/PycharmProjects/Stock_analysis/Stock_analysis/stock_id')
A500 = pd.read_excel('A500.xlsx', index_col=0)
SH50 = pd.read_excel('SH50.xlsx',index_col=0)
CYB50 = pd.read_excel('CYB50.xlsx',index_col=0)
