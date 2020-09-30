import datetime as dt
import pandas as pd
from time import sleep

from src.utils import *
from src.fxcm import Fxcm
from src.algorithm import Algorithm
# from pylab import plt
# plt.style.use('seaborn')


class Bot():
    fxcm = None
    algo = Algorithm()

    isRunning = True

    isRealTime = None
    startDate = None
    endDate = None

    allCandles = []
    lastCandle = dict()
    newCandle = dict()

    def __init__(self, config, devMode=False, con=None):
        self.fxcm = Fxcm(devMode, con)

        self.isRealTime = config["isRealTime"]
        self.startDate = dt.datetime.strptime(
            config["startDate"], "%Y/%m/%d %H:%M")
        self.endDate = dt.datetime.strptime(
            config["endDate"], "%Y/%m/%d %H:%M")

    def runBot(self):
        if self.isRealTime == True:
            self.runStreamMode()
        else:
            self.runHistoryMode()

    def runStreamMode(self):
        self.fxcm.subscribeMarket([self.standardizeStreamEntry])
        while self.isRunning:
            pass

    def standardizeStreamEntry(self, data, dataframe):
        if not self.isRunning:
            return
        if self.lastCandle:
            delta = dateDiffInMillisecond(pd.to_datetime(
                int(data['Updated']), unit='ms'), self.lastCandle["date"])
            print(delta)
            if delta > self.algo.STREAM_PERIOD:
                self.createLastCandle(data, dataframe)
                self.displayCandles(data, dataframe)
                order = self.fxcm.buy(rate=data['Rates'][0], amount=1, limit=data['Rates']
                                      [0] + 10, stop=data['Rates'][0] - 5, inPips=True)
                self.closePosition(order)
                self.end()
        else:
            self.createLastCandle(data, dataframe)

    def closePosition(self, order):
        if order.get_status() == "Executing":
            self.fxcm.closePosition(order.get_tradeId())
        else:
            self.fxcm.deleteOrder(order)

    def end(self):
        self.fxcm.unsubscribeMarket()
        self.isRunning = False

    def createLastCandle(self, data, dataframe):
        self.lastCandle["date"] = pd.to_datetime(
            int(data['Updated']), unit='ms')

    def displayCandles(self, data, dataframe):
        print('%3d | %s | %s, %s, %s, %s, %s'
              % (len(dataframe), data['Symbol'],
                 pd.to_datetime(int(data['Updated']), unit='ms'),
                 data['Rates'][0], data['Rates'][1], data['Rates'][2],
                 data['Rates'][3]))


def mainDev(con):
    bot = Bot({"isRealTime": True, "startDate": "2020/09/20 00:00",
               "endDate": "2020/09/21 00:00"}, True, con)
    bot.runBot()


def mainProd():
    bot = Bot({"isRealTime": True, "startDate": "2020/09/20 00:00",
               "endDate": "2020/09/21 00:00"})
    bot.runBot()


if __name__ == "__main__":
    mainProd()
