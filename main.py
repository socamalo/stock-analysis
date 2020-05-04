import os
import time, datetime
import pandas as pd
import numpy as np
import baostock as bs
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from Company_class import Company


company_holder = {}
for i in Company.cyb50():
    company_holder[i] = Company(i)

result = []
lg = bs.login()
for key in company_holder:
    print(key)
    if company_holder[key].gain_lose_ratio['gain_lose_ratio'] >= 3:
        result.append(company_holder[key])