import pandas as pd
from matplotlib import pyplot as plt
import matplotlib
import datetime as dt
from datetime import datetime
x= dt.datetime.strptime("2020-02-01",'%Y-%m-%d').date()
print(type(x))
print(x.month)
print(dt.datetime(2016,1,1))