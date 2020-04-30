import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from Company_class import Company

zte = Company('sz.000063')
zte.get_history_k()
x = pd.DataFrame(np.arange(30))
y = pd.DataFrame(zte.history_k.MA200[(len(zte.history_k) - 30):(len(zte.history_k))])
sc_x = StandardScaler()
sc_y = StandardScaler()
x_std = sc_x.fit_transform(x)
y_std = sc_y.fit_transform(y)
#plt.plot(x_std,y_std)


