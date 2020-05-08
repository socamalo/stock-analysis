import os
import time, datetime
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import baostock as bs
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, PolynomialFeatures

lg = bs.login()


class Company:

    delta_history_k = timedelta(days=665)  # 365天前开始
    start_date = (datetime.now() - delta_history_k).strftime("%Y-%m-%d")
    delta_pe = timedelta(days=10)
    start_date_pe = (datetime.now() - delta_pe).strftime("%Y-%m-%d")

    @staticmethod
    def wwma(values, n):
        """
         J. Welles Wilder's EMA
        """
        return values.ewm(alpha=1 / n, adjust=False).mean()

    @classmethod
    def pop_3(x):
        x_list = list(x)
        for i in range(3):
            x_list.pop()
        x_list.append(',')
        x_str = ''.join(x_list)
        return x_str

    @classmethod
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

    @classmethod
    def zz500(cls):
        rs = bs.query_zz500_stocks()
        zz500_stocks = []
        while (rs.error_code == '0') & rs.next():
            zz500_stocks.append(rs.get_row_data())
        result = pd.DataFrame(zz500_stocks, columns=rs.fields)
        return result.code

    @classmethod
    def hs300(cls):
        rs = bs.query_hs300_stocks()
        hs300_stocks = []
        while (rs.error_code == '0') & rs.next():
            hs300_stocks.append(rs.get_row_data())
        result = pd.DataFrame(hs300_stocks, columns=rs.fields)
        return result.code

    @classmethod
    def sz50(cls):
        rs = bs.query_sz50_stocks()
        sz50_stocks = []
        while (rs.error_code == '0') & rs.next():
            sz50_stocks.append(rs.get_row_data())
        result = pd.DataFrame(sz50_stocks, columns=rs.fields)
        return result.code

    @classmethod
    def cyb50(cls):
        os.chdir('/Users/D_Dj/PycharmProjects/Stock_analysis/Stock_analysis/stock_id')
        cyb50 = pd.read_excel('CYB50.xlsx', index_col=0)
        return cyb50.stock_id

    @staticmethod
    def lin_regplot(x, y, model):
        plt.scatter(x, y, c='blue')
        plt.plot(x, model.predict(x), color='red')
        return None

    def __init__(self, stock_id):
        self.stock_id = stock_id
        self.end_date = (time.strftime("%Y-%m-%d", time.localtime()))
        rs = bs.query_history_k_data_plus(self.stock_id,
                                          "date,code,open,high,low,close,preclose,volume,"
                                          "amount,adjustflag,turn,tradestatus,pctChg,isST",
                                          start_date=self.start_date, end_date=self.end_date,
                                          frequency="d", adjustflag="2")
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)
        cols = ['open', 'close', 'low', 'high', 'preclose', 'volume', 'amount', 'turn', 'pctChg']  # 多列转化成数字
        result[cols] = result[cols].apply(pd.to_numeric, errors='coerce', axis=1)
        result['MA300'] = result.high.rolling(300).mean()  # 计算好200日移动平均
        result['MA200'] = result.high.rolling(200).mean()  # 计算好200日移动平均
        result['MA50'] = result.high.rolling(50).mean()  # 计算好200日移动平均
        result['MA20'] = result.high.rolling(20).mean()  # 计算好200日移动平均
        result.dropna(inplace=True)
        self.history_k = result
        try:
            self.last_close_price = self.history_k['close'].tail(1).iloc[0]
        except:
            pass

    @property
    def aboveMA200_mark(self):
        return self.last_close_price > self.history_k['MA200'].tail(1).iloc[0]

    @property
    def MA50_above_MA300(self):
        return self.history_k['MA50'].tail(1).iloc[0] >= self.history_k['MA200'].tail(1).iloc[0]

#    @property
 #   def last_close_price(self):
  #      return self.history_k['close'].tail(1).iloc[0]

    @property
    def coefficient_MA200(self):
        y = pd.DataFrame(self.history_k.MA200[(len(self.history_k) - 30):(len(self.history_k))])
        x = pd.DataFrame(np.arange(len(y)))
        sc_x = StandardScaler()
        sc_y = StandardScaler()
        x_std = sc_x.fit_transform(x)
        y_std = sc_y.fit_transform(y)
        lr = LinearRegression()
        lr.fit(x_std, y_std)
        return lr.coef_[0][0]

    @property
    def pe_pb(self):
        rs = bs.query_history_k_data_plus(self.stock_id,
                                          "date,code,close,peTTM,pbMRQ,psTTM,pcfNcfTTM",
                                          start_date=self.start_date_pe, end_date=self.end_date,
                                          frequency="d", adjustflag="3")
        result_list = []
        while (rs.error_code == '0') & rs.next():
            result_list.append(rs.get_row_data())
        result = pd.DataFrame(result_list, columns=rs.fields)
        cols = ['peTTM', 'pbMRQ']  # 多列转化成数字
        result[cols] = result[cols].apply(pd.to_numeric, errors='coerce', axis=1)
        peTTM = result['peTTM'][len(result) - 1]
        pbMRQ = result['pbMRQ'][len(result) - 1]  # MRQ: most recent quarter
        return {'peTTM': peTTM, 'pbMRQ': pbMRQ}

    @property
    def gain_lose_ratio(self):

       #----------
        window = 30
        history_k = self.history_k
        history_k['min'] = self.history_k.low.rolling(window).min()
        history_k['max'] = self.history_k.high.rolling(window).max()
        history_k = history_k.dropna()
        history_k = history_k.reset_index(drop=True)

        low_list = []
        high_list = []
        for i in range(len(history_k) - 1, 0, -1):
            if (history_k.high[i] == history_k['max'][i]) & (history_k.close[i] != history_k.close[i - 1]):
                high_list.append(history_k.high[i])
            elif (history_k.low[i] == history_k['min'][i]) & (history_k.close[i] != history_k.close[i - 1]):
                low_list.append(history_k.low[i])
        try:
            pre_close = history_k.close[len(history_k) - 1]
            up_rate = (high_list[0] - pre_close) / pre_close
            down_rate = (pre_close - low_list[0]) / pre_close
            if down_rate == 0:
                ratio = 1000
            else:
                ratio = up_rate / down_rate

            return {'gain_lose_ratio': ratio, 'gain_ratio': up_rate, 'lose_ratio': down_rate,
                    'pre_high': high_list[0], 'pre_low': low_list[0]}
        except (IndexError, ValueError)as e:
            print(e)
            return {'gain_lose_ratio': 0.0, 'gain_ratio': 0.0, 'lose_ratio': 0.0,
                    'pre_high': 0.0, 'pre_low': 0.0}

    @property
    def code_name(self):
        rs = bs.query_stock_basic(code=self.stock_id)
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        return data_list[0][1]

    @property
    def close_MA20_std(self):
        if not self.ran_get_history_k_mark:
            self.history_k
        df = self.history_k
        df['close_MA20'] = df.apply(lambda x: x['close']-x['MA20'], axis=1)
        return {'std': df.close_MA20.describe()['std'], 'min': df.close_MA20.describe()['min'],
                'max': df.close_MA20.describe()['max']}

    def linear_fit(self, length=300):
        if self.last_close_price == 'NaN':
            self.get_history_k()
        y = pd.DataFrame(self.history_k.MA200[(len(self.history_k) - length):(len(self.history_k))])
        print(self.history_k.date[len(self.history_k) - length])
        x = pd.DataFrame(np.arange(len(y)))
        sc_x = StandardScaler()
        sc_y = StandardScaler()
        self.x_std = sc_x.fit_transform(x)
        self.y_std = sc_y.fit_transform(y)
        lr = LinearRegression()
        lr.fit(self.x_std, self.y_std)
        print('LR:', lr.coef_)
        self.lin_regplot(self.x_std, self.y_std, lr)
        plt.show()

    def quatratic_fit(self, length=60):
        if self.last_close_price == 'NaN':
            self.get_history_k()
        y = pd.DataFrame(self.history_k.MA200[(len(self.history_k) - length):(len(self.history_k))])
        print(self.history_k.date[len(self.history_k) - length])
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
        plt.show()

    def cubic_fit(self, length=50, draw_length=50):
        if not self.ran_get_history_k_mark:
            self.history_k
      #  y = pd.DataFrame(self.history_k.close[(len(self.history_k) - length):(len(self.history_k))])
        y = pd.DataFrame(self.history_k.close.tail(length))
        print(self.history_k.date.iloc[len(self.history_k) - length])
        x = pd.DataFrame(np.arange(len(y)))
        sc_x = StandardScaler()
        sc_y = StandardScaler()
        sc_x_future = StandardScaler()
        x_std = sc_x.fit_transform(x)
        y_std = sc_y.fit_transform(y)
        self.regr = LinearRegression()
        cubic = PolynomialFeatures(degree=3)
        x_cubic = cubic.fit_transform(x_std)
        # -------预测未来5天------------
        x_future_std = x_std[len(x_std) - draw_length:len(x_std) - 1]  # 只画出最近30天，用length天训练
        forecast_length = int(draw_length * 0.1)
        for i in range(forecast_length):
            x_future_std = np.append(x_future_std, \
                                     (x_future_std[len(x_future_std) - 1][0] + (x_future_std[len(x_future_std) - 1][0] -
                                                                                x_future_std[len(x_future_std) - 2][
                                                                                    0]))).reshape(-1, 1)
        self.regr.fit(x_cubic, y_std)
        y_cubic_fit = self.regr.predict(cubic.fit_transform(x_future_std))
        x_std_plot = x_std[len(x_std) - draw_length:len(x_std) - 1]
        y_std_plot = y_std[len(y_std) - draw_length:len(y_std) - 1]
        plt.scatter(x_std_plot, y_std_plot)
        plt.plot(x_future_std, y_cubic_fit)
        plt.show()

    def atr(self, n=14):
        data = self.history_k.copy()
        high = data['high']
        low = data['low']
        close = data['close']
        data['tr0'] = abs(high - low)
        data['tr1'] = abs(high - close.shift())
        data['tr2'] = abs(low - close.shift())
        tr = data[['tr0', 'tr1', 'tr2']].max(axis=1)
        atr = Company.wwma(tr, n)
        self.history_k['atr'] = atr
        return self.history_k

    def unit(self, amount=100000):
        return  self.last_close_price * (amount/100) / self.atr().atr.tail(1).iloc[0]  #最近一天atr值

'''
    def ATR(df, n):
        i = 0
        TR_l = [0]
        while i < df.index[-1]:
            TR = max(df._get_value(i + 1, 'high'), df._get_value(i, 'close')) - min(df._get_value(i + 1, 'low'),
                                                                                  df._get_value(i, 'close'))
            TR_l.append(TR)
            i = i + 1
        TR_s = pd.Series(TR_l)
        ATR = pd.Series(pd.ewma(TR_s, span=n, min_periods=n), name='ATR_' + str(n))
        df = df.join(ATR)
        return df'''