import time, datetime
import pandas as pd
import numpy as np
import baostock as bs
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler


lg = bs.login()


class Company:
    start_date = '2019-01-01'

    @staticmethod
    def lin_regplot(x, y, model):
        plt.scatter(x, y, c='blue')
        plt.plot(x, model.predict(x), color='red')
        return None

    def __init__(self, stock_id):
        self.stock_id = stock_id
        self.end_date = (time.strftime("%Y-%m-%d", time.localtime()))
        self.peTTM = 'na'
        self.pbMRQ = 'na'
        self.last_close_price = 'na'
        self.aboveMA200_mark = 'na'
        self.history_k = 'na'
        self.coefficient_MA200 = 'na'

    def get_history_k(self):
        rs = bs.query_history_k_data_plus(self.stock_id,
                                          "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                          start_date=self.start_date, end_date=self.end_date,
                                          frequency="d", adjustflag="2")
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)
        cols = ['open', 'close', 'low', 'high', 'preclose', 'volume', 'amount', 'turn', 'pctChg']  # 多列转化成数字
        result[cols] = result[cols].apply(pd.to_numeric, errors='coerce', axis=1)
        result['MA200'] = result.high.rolling(200).mean()  # 计算好200日移动平均
        self.last_close_price = result['close'][len(result) - 1]  # 初始化最后一个交易日收盘价
        self.aboveMA200_mark = self.last_close_price > result['MA200'][len(result) - 1]  # 初始化最后交易日收盘价是否在MA300之上
        self.history_k = result
        #----------------Linear Regression----------------
        x = pd.DataFrame(np.arange(30))
        y = pd.DataFrame(self.history_k.MA200[(len(self.history_k) - 30):(len(self.history_k))])
        sc_x = StandardScaler()
        sc_y = StandardScaler()
        x_std = sc_x.fit_transform(x)
        y_std = sc_y.fit_transform(y)
        LR = LinearRegression()
        LR.fit(x_std, y_std)
        self.coefficient_MA200 = LR.coef_[0][0]# model.coef结果为二位数列

    def get_pe_pb(self):
        now = datetime.datetime.now()
        delta = datetime.timedelta(days=-90)
        pe_start_time = (now + delta).strftime('%Y-%m-%d')
        # pe_start_time = (time.strftime("%Y-%m-%d", temp_time))
        # 避免获取太久前的数据，仅获取过去90天的数据。需要注意时间的格式。
        stock_id = self.stock_id
        rs = bs.query_history_k_data_plus(stock_id,
                                          "date,code,close,peTTM,pbMRQ,psTTM,pcfNcfTTM",
                                          start_date=pe_start_time, end_date=self.end_date,
                                          frequency="d", adjustflag="3")
        result_list = []
        while (rs.error_code == '0') & rs.next():
            result_list.append(rs.get_row_data())
        result = pd.DataFrame(result_list, columns=rs.fields)
        cols = ['peTTM', 'pbMRQ']  # 多列转化成数字
        result[cols] = result[cols].apply(pd.to_numeric, errors='coerce', axis=1)
        self.peTTM = result['peTTM'][len(result) - 1]
        self.pbMRQ = result['pbMRQ'][len(result) - 1]  # MRQ: most recent quarter

    @property
    def code_name(self):
        rs = bs.query_stock_basic(code=self.stock_id)
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        return data_list[0][1]

    def draw(self):
        x = pd.DataFrame(np.arange(30))
        y = pd.DataFrame(self.history_k.MA200[(len(self.history_k) - 30):(len(self.history_k))])
        sc_x = StandardScaler()
        sc_y = StandardScaler()
        x_std = sc_x.fit_transform(x)
        y_std = sc_y.fit_transform(y)
        LR = LinearRegression()
        LR.fit(x_std, y_std)
        print('LR:', LR.coef_)
        self.lin_regplot(x_std, y_std, LR)


