import time
import pandas as pd
import baostock as bs

lg = bs.login()


class stock:

    def __init__(self, id):
        self.id = id
        self.start_date = '2019-01-01'
        self.end_date = (time.strftime("%Y-%m-%d", time.localtime()))

    def get_history_k(self):
        stock_id = self.id
        rs = bs.query_history_k_data_plus(stock_id,
                                          "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
                                          start_date=self.start_date, end_date=self.end_date,
                                          frequency="d", adjustflag="2")
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        result = pd.DataFrame(data_list, columns=rs.fields)
        return result

    def get_pe_pb(self):
        stock_id = self.id
        rs = bs.query_history_k_data_plus(stock_id,
                                          "date,code,close,peTTM,pbMRQ,psTTM,pcfNcfTTM",
                                          start_date=self.start_date, end_date=self.end_date,
                                          frequency="d", adjustflag="3")

        #### 打印结果集 ####
        result_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            result_list.append(rs.get_row_data())
        result = pd.DataFrame(result_list, columns=rs.fields)
        return result

    @property
    def code_name(self):
        rs = bs.query_stock_basic(code=self.id)
        data_list = []
        while (rs.error_code == '0') & rs.next():
            # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
        return data_list[0][1]
