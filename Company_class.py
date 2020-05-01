import time, datetime
import pandas as pd
import numpy as np
import baostock as bs
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, PolynomialFeatures


lg = bs.login()


class Company:
    start_date = '2010-01-01'

    @staticmethod
    def lin_regplot(x, y, model):
        plt.scatter(x, y, c='blue')
        plt.plot(x, model.predict(x), color='red')
        return None

    def __init__(self, stock_id):
        self.stock_id = stock_id
        self.end_date = (time.strftime("%Y-%m-%d", time.localtime()))
        self.peTTM = 'NaN'
        self.pbMRQ = 'NaN'
        self.last_close_price = 'NaN'
        self.aboveMA200_mark = 'NaN'
        self.history_k = 'NaN'
        self.coefficient_MA200 = 'NaN'

    def get_history_k(self):
        rs = bs.query_history_k_data_plus(self.stock_id,
                                          "date,code,open,high,low,close,preclose,volume,"
                                          "amount,adjustflag,turn,tradestatus,pctChg,isST",
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
        #result.dropna(inplace=True)
        self.last_close_price = result['close'][len(result) - 1]  # 初始化最后一个交易日收盘价
        self.aboveMA200_mark = self.last_close_price > result['MA200'][len(result) - 1]  # 初始化最后交易日收盘价是否在MA300之上
        self.history_k = result
        #----------------Linear Regression----------------
        y = pd.DataFrame(self.history_k.MA200[(len(self.history_k) - 30):(len(self.history_k))])
        x = pd.DataFrame(np.arange(len(y)))
        sc_x = StandardScaler()
        sc_y = StandardScaler()
        x_std = sc_x.fit_transform(x)
        y_std = sc_y.fit_transform(y)
        lr = LinearRegression()
        lr.fit(x_std, y_std)
        self.coefficient_MA200 = lr.coef_[0][0]# model.coef结果为二位数列

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

    def linear_fit(self, length=300):
        if self.last_close_price == 'NaN':
            self.get_history_k()
        y = pd.DataFrame(self.history_k.MA200[(len(self.history_k) - length):(len(self.history_k))])
        print(self.history_k.date[len(self.history_k)-length])
        x = pd.DataFrame(np.arange(len(y)))
        sc_x = StandardScaler()
        sc_y = StandardScaler()
        self.x_std = sc_x.fit_transform(x)
        self.y_std = sc_y.fit_transform(y)
        lr = LinearRegression()
        lr.fit(self.x_std, self.y_std)
        print('LR:', lr.coef_)
        self.lin_regplot(self.x_std, self.y_std, lr)

    def quatratic_fit(self,length=60):
        if self.last_close_price == 'NaN':
            self.get_history_k()
        y = pd.DataFrame(self.history_k.MA200[(len(self.history_k) - length):(len(self.history_k))])
        print(self.history_k.date[len(self.history_k)-length])
        x = pd.DataFrame(np.arange(len(y)))
        sc_x = StandardScaler()
        sc_y = StandardScaler()
        self.x_std = sc_x.fit_transform(x)
        self.y_std = sc_y.fit_transform(y)
        self.pr = LinearRegression()
        quadratic = PolynomialFeatures(degree=2)
        self.x_quad = quadratic.fit_transform(self.x_std)
       # self.x_fit = np.linspace(-1.7262869,1.7262869,300)[:, np.newaxis]
        self.pr.fit(self.x_quad, self.y_std)
        self.y_quad_fit = self.pr.predict(quadratic.fit_transform(self.x_std))
      #  self.lin_regplot(self.x_std, self.y_std, self.pr)
        plt.scatter(self.x_std, self.y_std)
        plt.plot(self.x_std, self.y_quad_fit)

    def cubic_fit(self, length=50, draw_length=50):
        if self.last_close_price == 'NaN':
            self.get_history_k()
        y = pd.DataFrame(self.history_k.close[(len(self.history_k) - length):(len(self.history_k))])
        print(self.history_k.date[len(self.history_k)-length])
        x = pd.DataFrame(np.arange(len(y)))
        sc_x = StandardScaler()
        sc_y = StandardScaler()
        sc_x_future = StandardScaler()
        self.x_std = sc_x.fit_transform(x)
        self.y_std = sc_y.fit_transform(y)
        self.regr = LinearRegression()
        cubic = PolynomialFeatures(degree=3)
        self.x_cubic = cubic.fit_transform(self.x_std)
        #-------预测未来5天------------
        self.x_future_std = self.x_std[len(self.x_std)-draw_length:len(self.x_std)-1] #只画出最近30天，用length天训练
        forecast_length = int(draw_length * 0.1)
        for i in range(forecast_length):
            self.x_future_std = np.append(self.x_future_std,\
                                          (self.x_future_std[len(self.x_future_std)-1][0]+(self.x_future_std[len(self.x_future_std)-1][0]-self.x_future_std[len(self.x_future_std)-2][0]) )).reshape(-1,1)
        self.regr.fit(self.x_cubic, self.y_std)
        self.y_cubic_fit = self.regr.predict(cubic.fit_transform(self.x_future_std))
        x_std_plot = self.x_std[len(self.x_std)-draw_length:len(self.x_std)-1]
        y_std_plot = self.y_std[len(self.y_std)-draw_length:len(self.y_std)-1]
        plt.scatter(x_std_plot, y_std_plot)
        plt.plot(self.x_future_std, self.y_cubic_fit)


