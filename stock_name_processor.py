import pandas as pd

'''for i in range(1,4000):
    i_str_list = list(str(i))
    shenzhen_stock_id_list = list('600000') #initial 
    for j in range(len(i_str_list)):
        shenzhen_stock_id_list.pop()
    while i_str_list: 
        shenzhen_stock_id_list.append(i_str_list.pop(0))
    stock_id = ''.join(shenzhen_stock_id_list)'''


def num_stock_id(number):
    if number >= 600000:
        starting_point = list('600000')
        tail = 'sh.'
    elif (number >= 300000) & (number <600000):
        starting_point = list("300000")
        tail = 'sz.'
    elif number < 300000:
        starting_point = list('000000')
        tail = 'sz.'

    number_str_list = list(str(number))
    for i in range(len(number_str_list)):
        starting_point.pop()
    while number_str_list:
        starting_point.append(number_str_list.pop(0))
    result = tail + ''.join(starting_point)

    return result




df = pd.read_excel('CYB50_raw.xlsx')
å
df_temp = df.iloc[1:,1]
df_list = list(df_temp)
df_id = pd.DataFrame(df_list,columns=['stock_id'])
df_id = df_id.stock_id.apply(lambda x: num_stock_id(x))
