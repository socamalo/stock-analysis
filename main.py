import os
import time, datetime
import pandas as pd
import numpy as np
import baostock as bs
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from Company_class import Company

os.chdir('/Users/D_Dj/PycharmProjects/Stock_analysis/Stock_analysis/stock_id')

A500 = pd.read_excel('A500.xlsx', index_col=0)
SH50 = pd.read_excel('SH50.xlsx',index_col=0)
CYB50 = pd.read_excel('CYB50.xlsx',index_col=0)