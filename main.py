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
company_holder = map(Company, target)

result = []
counter = 0
for x in company_holder:
 #   x = next(company_holder)
    print(x.stock_id,x.gain_lose_ratio['lose_ratio'])
    try:
        if (x.gain_lose_ratio['gain_lose_ratio'] >= 3) \
            & (x.aboveMA200_mark)\
            & (x.gain_lose_ratio['lose_ratio'] < 0.1):

            result.append([x.code_name, x.stock_id, x.close, ])
    except (IndexError, ValueError)as e:
        print(e)
columns = ['id', 'ratio', 'close', 'high', 'low', 'up_rate', 'down_rate', 'MA200', 'peTTM', 'pbMRQ', 'coefficient']

print('完成任务，用时：%f' % (time.time() - start_time))
