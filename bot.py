import fxcmpy
import datetime as dt
import pandas as pd
import utils as utl
from fxcm import Fxcm
from algorithm import Algorithm
from utils import Singleton
# from pylab import plt
# plt.style.use('seaborn')


class Bot():
    fxcm = Fxcm()
    algo = Algorithm()

    isRealTime = None
    startDate = None
    endDate = None

    allCandles = []
    lastCandle = dict()
    newCandle = dict()

    def __init__(self, config):
        self.isRealTime = config["isRealTime"]
        self.startDate = dt.datetime.strptime(
            config["startDate"], "%Y/%m/%d %H:%M")
        self.endDate = dt.datetime.strptime(
            config["endDate"], "%Y/%m/%d %H:%M")

    def run(self):
        if self.isRealTime == True:
            self.runStreamMode()
        else:
            self.runHistoryMode()

    def runStreamMode(self):
        self.fxcm.subscribeMarket([self.standardizeStreamEntry])

    def standardizeStreamEntry(self, data, dataframe):
        if self.lastCandle:
            delta = utl.dateDiffInMillisecond(pd.to_datetime(
                int(data['Updated']), unit='ms'), self.lastCandle["date"])
            print(delta)
            if delta > self.algo.STREAM_PERIOD:
                self.createLastCandle(data, dataframe)
                self.displayCandles(data, dataframe)
        else:
            self.createLastCandle(data, dataframe)

    def createLastCandle(self, data, dataframe):
        self.lastCandle["date"] = pd.to_datetime(
            int(data['Updated']), unit='ms')

    def displayCandles(self, data, dataframe):
        print('%3d | %s | %s, %s, %s, %s, %s'
              % (len(dataframe), data['Symbol'],
                 pd.to_datetime(int(data['Updated']), unit='ms'),
                 data['Rates'][0], data['Rates'][1], data['Rates'][2],
                 data['Rates'][3]))


bot = Bot({"isRealTime": True, "startDate": "2020/09/20 00:00",
           "endDate": "2020/09/21 00:00"})

bot.run()


# fxcm = Fxcm()

# fxcm.subscribeMarket([print_data])
# fxcm.unsubscribeMarket()

# fxcm.close()
