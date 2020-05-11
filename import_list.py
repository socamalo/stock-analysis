import time, datetime
import pandas as pd
import numpy as np
import baostock as bs
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from Company_class import Company

def test():
    print('just for test')

    https://medium.com/datadriveninvestor/turtle-trading-with-python-is-the-trend-really-your-friend-d178160be6e5

        
df['date2'] = df.date.apply(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'))
