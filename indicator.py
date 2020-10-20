from pyti.exponential_moving_average import exponential_moving_average as ema
from pyti.bollinger_bands import upper_bollinger_band as ubb
from pyti.bollinger_bands import middle_bollinger_band as mbb
from pyti.bollinger_bands import lower_bollinger_band as lbb
from pyti.bollinger_bands import percent_bandwidth as percent_b
from pyti.relative_strength_index import relative_strength_index as rsi
from pyti.double_smoothed_stochastic import double_smoothed_stochastic as dss


# Some tips by stan:
# 1. Define a *trend* by using 2 emas (50, 200) + rsi.
# 2. Then try to open positions.
# Mix periods, to get better signals. (mostly trend).
#
# Stop loss and take profits. (Money Management! after strategy confirm).
# Define those % on the getgo.
# Use stop loss/tak profits AND also closePositions. (If signals are good enough)
def indicator(data, period):
    """""
    _res is the result of the indicator analysis
    _res can be -3, -2, -1, 0, 1, 2, 3
    The lowest it is the more one should sell
    The bigger it is the more one should buy
    If _res equals 0 then one should stay put
    Coherency depicts the relation between the difference analysis results and how coinciding the indicator results are
    """""

    _res = {'bb_res': None, 'rsi_res':None, 'dss_res':None, 'ema_res':None}
    _res['bb_res'] = bb_analysis(data, period) # Should be around 21 Period. // When to buy/sell
    _res['rsi_res'] = rsi_analysis(data, period.convertH.last14) # Should be around 14 Period. // When to buy/sell
    _res['dss_res'] = dss_analysis(data, period) # Should be around 14 ? // When to buy/sell
    _res['ema_res'] = ema_analysis(data, period) # Should be around 20 Period. (Trend)

    result = round(sum(_res.values())/len(_res))
    if (-1 > result >= -3):
        return('Sell')
    elif (1 >= result >= -1):
        return('Wait')
    elif (3 >= result > 1):
        return('Buy')

def dss_analysis(data, period):
    anal = dss(data, period)

    if (anal[-1] > 70):
        return -3
    elif (anal[-1] < 30):
        return 3
    elif (30 <= anal[-1] < 50):
        return 1
    elif (50 < anal[-1] <= 70):
        return -1
    else:
        return 0

def bb_analysis(data, period):
    upperband = ubb(data, period)
    lowerband = lbb(data, period)
    midband = mbb(data,period)

    if (data[-1] > upperband[-1]):
        return -3
    elif (data[-1] < lowerband[-1]):
        return 3
    elif (midband[-1] < data[-1] <= upperband[-1]):
        return -1
    elif (midband[-1] > data[-1] >= lowerband[-1]):
        return 1
    else:
        return 0

def rsi_analysis(data, period):
    anal = rsi(data, period)
    if (anal[-1] > 70):
        return -3
    elif (anal[-1] < 30):
        return 3
    elif (30 <= anal[-1] < 50):
        return 1
    elif (50 < anal[-1] <= 70):
        return -1
    else:
        return 0

def ema_analysis(data, period):
    anal = ema(data, period)
    if (anal[-1] > data[-1]):
        return 3
    elif (anal[-1] < data[-1]):
        return -3
    else:
        return 0


########## EXAMPLE TO SHOW
########## AN INDICATOR


sample_close_data = [792.65, 802.44, 804.97, 810.1, 809.36, 809.74,
813.47, 817.09, 813.84, 808.33, 816.82, 818.1, 814.88, 808.54, 809.14,
793.75, 792.27, 777.49, 776.23, 765.78, 764.03, 777.64, 789.16, 785.8,
779.42, 777.89, 784.3, 784.15, 777.1, 784.32, 780.36, 773.55, 751.27,
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
707.26, 708.97, 704.89, 700]
sample_open_data = [792.65, 802.44, 804.97, 810.1, 809.36, 809.74,
813.47, 817.09, 813.84, 808.33, 816.82, 818.1, 814.88, 808.54, 809.14,
793.75, 792.27, 777.49, 776.23, 765.78, 764.03, 777.64, 789.16, 785.8,
779.42, 777.89, 784.3, 784.15, 777.1, 784.32, 780.36, 773.55, 751.27,
773.14, 780.74, 806.06, 811.36, 802.77, 780.58, 783.8, 789.48, 803.57,
810.31, 819.63, 817.57, 822.32, 827.92, 836.26, 825.95, 820.36, 827.71,
822.4, 805.46, 804.97, 805.58, 811.53, 809.3, 812.61, 800.13, 804.02,
801.56, 802.09, 801.82, 803.7, 803.34, 811.66, 811.08, 804.18, 816.33,
816.32, 803.74, 799.0, 794.39, 797.65, 801.18, 788.73, 788.24, 799.76,
787.64, 804.34, 807.17, 807.71, 795.59, 793.3, 789.95, 790.57, 796.19,
793.37, 791.55, 794.59, 795.42, 796.95, 799.32, 802.44, 806.66, 799.92,
805.57, 806.8, 809.1, 807.58, 806.91, 806.56, 806.8, 798.0, 797.97,
798.52, 801.33, 791.09, 764.68, 761.23, 757.27, 756.87, 758.1, 753.83,
755.59, 752.34, 753.65, 737.24, 735.76, 730.05, 732.79, 728.37, 717.19,
707.42, 708.66, 703.46, 709.32]
sample_high_data = [794.91, 805.3, 807.25, 812.88, 810.12, 812.05,
814.66, 817.28, 814.84, 812.23, 818.64, 820.57, 818.29, 809.92, 812.34,
797.73, 794.17, 778.71, 781.01, 767.06, 766.79, 778.32, 792.06, 787.82,
782.73, 781.69, 787.13, 787.34, 778.89, 788.7, 782.51, 777.94, 755.72,
774.1, 782.54, 808.14, 814.27, 804.36, 783.85, 784.19, 790.85, 808.37,
812.32, 821.94, 819.38, 824.33, 831.01, 837.91, 826.29, 824.61, 829.38,
823.9, 809.73, 806.96, 806.73, 814.6, 811.89, 816.2, 803.4, 805.91,
803.84, 805.49, 802.58, 806.15, 805.4, 812.68, 812.88, 805.16, 817.83,
818.51, 807.5, 802.37, 797.86, 800.07, 803.67, 793.35, 791.6, 801.07,
790.55, 805.22, 810.23, 810.59, 798.98, 793.47, 792.58, 794.07, 798.18,
795.72, 793.78, 795.88, 798.6, 799.11, 801.99, 805.62, 808.3, 803.94,
808.05, 809.17, 810.42, 811.04, 809.84, 807.83, 809.04, 799.62, 801.36,
802.27, 803.5, 793.89, 768.29, 764.1, 760.17, 760.06, 761.37, 756.72,
759.35, 756.19, 755.8, 738.45, 738.62, 732.28, 734.98, 729.78, 719.97,
709.99, 711.9, 707.4, 713.1]
sample_low_data = [789.93, 800.42, 802.02, 807.1, 804.93, 807.34,
810.0, 812.69, 810.45, 807.59, 813.25, 815.38, 812.94, 805.34, 807.21,
792.78, 788.57, 773.93, 776.03, 762.46, 761.82, 773.87, 786.76, 783.52,
778.02, 776.7, 782.61, 782.4, 773.05, 783.8, 777.94, 772.5, 750.74,
769.26, 777.73, 803.46, 809.37, 799.27, 778.14, 779.91, 786.17, 803.02,
807.05, 817.19, 814.46, 819.59, 825.75, 832.86, 821.76, 819.23, 824.87,
819.47, 803.97, 802.26, 801.18, 809.5, 807.38, 811.34, 798.17, 800.12,
799.14, 799.87, 797.48, 801.69, 799.9, 807.34, 807.84, 800.27, 812.84,
813.54, 802.7, 797.21, 793.24, 795.63, 798.42, 788.0, 786.02, 795.97,
785.85, 800.06, 805.14, 805.42, 794.71, 788.66, 786.9, 789.34, 793.47,
790.34, 788.86, 791.24, 793.62, 794.67, 796.65, 800.24, 802.65, 798.96,
803.41, 804.48, 805.43, 806.46, 804.76, 802.65, 804.44, 794.63, 796.36,
797.94, 798.2, 789.16, 763.28, 759.63, 754.81, 755.09, 756.97, 752.26,
754.28, 750.9, 750.26, 732.9, 733.42, 727.07, 730.1, 724.76, 715.58,
704.91, 106.26, 102.58, 100.78]
"""
    key_min = min(_res.keys(), key=(lambda k: _res[k]))
    key_max = max(_res.keys(), key=(lambda k: _res[k]))
    _min = _res[key_min]
    _max = _res[key_max]
    coherency = {'relative': None, 'overall': None, 'similitary': None} ### CHECK THE COHERENCY BETWEEN THE 3 INDICATORS
    coherency['overall'] = round(sum(_res.values())/len(_res))          ### THE AVERAGE VALUE GIVEN BY THE INDICATORS
    if (_min > 0 and _max <= 3):
        coherency['relative'] = 3                                       ### ARE THE INDICATORS IN A POSITIVE OR A NEGATIVE TREND ?
    elif (_max < 0 and _min >= -3):
        coherency['relative'] = -3
    else:
        coherency['relative'] = 0
    temp_simil = {'a': None, 'b': None, 'c': None}
    _length = range(len(_res)*2+1)
    for i in _length:
        if ((_res['sma_res'] - _res['bb_res']) in range(-i,i+1)):
            temp_simil['a'] = -1*(i-len(_res))
            break
    for j in _length:
        if ((_res['sma_res'] - _res['rsi_res']) in range(-j,j+1)):
            temp_simil['b'] = -1*(j-len(_res))
            break
    for l in _length:
        if ((_res['rsi_res'] - _res['bb_res']) in range(-l,l+1)):
            temp_simil['c'] = -1*(l-len(_res))
            break
    simil_key = min(temp_simil.keys(), key=(lambda k: temp_simil[k]))
    coherency['similitary'] = temp_simil[simil_key]                      ### HOW BIG IS THE GAP BETWEEN EACH INDICATOR'S VALUE
    result = sum(coherency.values())
"""
"""
ma = sma(sample_close_data, period_6)
for i in range(len(sample_close_data)):
    if 1.02*ma[i] < sample_close_data[i]:
        print("sell")
    elif 0.98*ma[i] > sample_close_data[i]:
        print("buy")
    else:
        print("wait")

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

plt.plot(sma(ma,period_6), 'r', sample_close_data, 'b')
plt.ylabel('data')
plt.xlabel('period')
plt.title('simple moving average chart')
plt.grid(True)
red_patch = mpatches.Patch(color='red', label='The simple moving average of the closing price')
blue_patch = mpatches.Patch(color='blue', label='The closing price')
plt.legend(handles=[red_patch, blue_patch])
plt.show()
"""
#period_6 = 6

#print(indicator(sample_close_data, period_6))
