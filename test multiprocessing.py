åfrom multiprocessing import Pool
from functools import partial
import pandas as pd
import baostock as bs
import time
lg = bs.login()
sh_A = pd.read_excel('sh_A.xlsx', index_col=0)
s_date = '2019-01-01'
e_date = (time.strftime("%Y-%m-%d", time.localtime()))


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
    print(stock_id)

    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    return result

partial_work = partial(get_history_k,  s_date='2019-01-01', e_date='2020-01-01')
pool = Pool(processes=4)
pool.map(partial_work, sh_A[0])

