from functools import partial
from multiprocessing import Pool




def work(x, y):
    return x + y
pool = Pool(processes=4)
x = [x for x in range(100)]
partial_work = partial(work, y=1) #  提取x作为partial函数的输入变量
results = pool.map(partial_work, x)