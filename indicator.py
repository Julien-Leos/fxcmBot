#moving average to do

import numpy as np
import pandas as pd
from pyti import catch_errors
from pyti.simple_moving_average import simple_moving_average as sma
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def moving_average(data, period):
    """
    Simple Moving Average.
    Formula:
    sma = (A1+A2+...+An)n
    """
    return sma(data, period)
    
sample_close_data = [792.45, 802.88, 804.57, 809.93, 807.8,
        809.68, 812.2, 815.2, 812.5, 809.84, 815.65, 817.89, 815.34, 807.9,
        809.45, 795.17, 791.47, 776.18, 778.22, 764.46, 764.33, 775.88, 789.44,
        785.79, 780.2, 779, 785, 784.8, 775.97, 786.16, 779.98, 775.16, 753.22,
        771.75, 780.29, 805.59, 811.98, 802.03, 781.1, 782.19, 788.42, 805.48,
        809.9, 819.56, 817.35, 822.1, 828.55, 835.74, 824.06, 821.63, 827.09,
        821.49, 806.84, 804.6, 804.08, 811.77, 809.57, 814.17, 800.71, 803.08,
        801.23, 802.79, 800.38, 804.06, 802.64, 810.06, 810.73, 802.65, 814.96,
        815.95, 805.03, 799.78, 795.39, 797.97, 801.23, 790.46, 788.72, 798.82,
        788.48, 802.84, 807.99, 808.02, 796.87, 791.4, 789.85, 791.92, 795.82,
        793.22, 791.3, 793.6, 796.59, 796.95, 799.65, 802.75, 805.42, 801.19,
        805.96, 807.05, 808.2, 808.49, 807.48, 805.23, 806.93, 797.25, 798.92,
        800.12, 800.94, 791.34, 765.84, 761.97, 757.65, 757.52, 759.28, 754.41,
        757.08, 753.41, 753.2, 735.63, 735.8, 729.48, 732.51, 727.2, 717.78,
        707.26, 708.97, 704.89, 710.25]

period_6 = 6
ma = moving_average(sample_close_data, period_6)
for i in range(len(sample_close_data)):
    if 1.02*ma[i] < sample_close_data[i]:
        print("sell")
    elif 0.98*ma[i] > sample_close_data[i]:
        print("buy")
    else:
        print("wait")

plt.plot(moving_average(ma,period_6), 'r', sample_close_data, 'b')
plt.ylabel('data')
plt.xlabel('period')
plt.title('simple moving average chart')
plt.grid(True)
red_patch = mpatches.Patch(color='red', label='The simple moving average of the closing price')
blue_patch = mpatches.Patch(color='blue', label='The closing price')
plt.legend(handles=[red_patch, blue_patch])
plt.show()