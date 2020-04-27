# -*- coding: utf-8 -*-
"""
Created on Sat Nov 26 10:14:40 2016

@author: Daniel
"""

import urllib.request,re
import pandas as pd
import sqlite3

data = []
#max_fail_counter = 200

for i in range(1,4000):
    i_str_list = list(str(i))
    shenzhen_stock_id_list = list('600000') #initial 
    for j in range(len(i_str_list)):
        shenzhen_stock_id_list.pop()
    while i_str_list: 
        shenzhen_stock_id_list.append(i_str_list.pop(0))
    stock_id = ''.join(shenzhen_stock_id_list)
    
    print (stock_id)
    html = urllib.request.urlopen\
    ('http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx?type=CT&cmd=%s1&sty=MCSS&st=a&sr=1&p=1&ps=1000&cb=&js=var/%%c20hgticon=(x)&token=de1161e2380d231908d46298ae339369&_=1485487781886'\
     %stock_id).read().decode('UTF-8')
    html = html[html.find('"')+1:len(html)-1].split(',')
    data.append(html)
#    if len(html)!=1:
#        fail_counter = 0
#    else:
#        fail_counter +=1
#        if fail_counter >= max_fail_counter:
#            print ('number of failures:',fail_counter)
#            break
columns = ['market_id','stock_id','stock_name','listed_mark','sh_hk_mark','suspended_mark']    
df = pd.DataFrame(data,columns = columns)
conn = sqlite3.connect('stock_meta.db')
df.to_sql('sh_A',conn,index=False,if_exists='append')

#df_sz_selected = df2.query('listed_mark== "True"')    #选择部分df
                                 
#    stock_add = 'http://quote.eastmoney.com/sz%s.html'%stock_id
#    html = ''
#    try:
#        html = download(stock_add)
#    except Exception as e:
#        print (e)
#    try:
#        data.append(meta(html))
#    except Exception as e:
#        print (e)
#        
  
    

    
