import fxcmpy
import datetime as dt
from fxcm import Fxcm
from pylab import plt
plt.style.use('seaborn')

# con = fxcmpy.fxcmpy(config_file='fxcm.cfg')

# data = con.get_candles('EUR/USD', period='m5', number=250)
# data['askclose'].plot(figsize=(10, 6))
# plt.show()

fxcm = Fxcm()

df = fxcm.getCandles("H1", 100, columns=["askclose"])
df.plot(figsize=(10, 6), lw=0.8)
plt.show()
# fxcm.displayDataFrame(df)

fxcm.close()
