import sys
import datetime as dt
import pandas as pd
from time import sleep

from utils import dateDiffInMillisecond, parseConfigFile
from fxcm import Fxcm, FxcmTest
from algorithm import Algorithm
# from pylab import plt
# plt.style.use('seaborn')


class Bot():
    fxcm = None
    algo = Algorithm()

    isRunning = True

    config: None

    allCandles = []
    lastCandle = dict()
    newCandle = dict()

    def __init__(self, config, devMode=False, con=None):
        self.fxcm = Fxcm(devMode, con) if not config['test_mode'] else FxcmTest(config, devMode, con)
        self.config = config

    def run(self):
        self.fxcm.subscribeMarket([self.standardizeStreamEntry])
        while self.isRunning:
            sleep(12)
            self.fxcm.unsubscribeMarket()
            self.isRunning = False

    def standardizeStreamEntry(self, data, dataframe):
        print(data)
        print(dataframe)
        return

        # if not self.isRunning:
        #     return
        # if self.lastCandle:
        #     delta = dateDiffInMillisecond(pd.to_datetime(
        #         int(data['Updated']), unit='ms'), self.lastCandle["date"])
        #     print(delta)
        #     if delta > self.algo.STREAM_PERIOD:
        #         self.createLastCandle(data, dataframe)
        #         self.displayCandles(data, dataframe)
        #         order = self.fxcm.buy(rate=data['Rates'][0], amount=1, limit=data['Rates']
        #                               [0] + 10, stop=data['Rates'][0] - 5, inPips=True)
        #         self.closePosition(order)
        #         self.end()
        # else:
        #     self.createLastCandle(data, dataframe)

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


def mainDev(con, argv):
    config = parseConfigFile(argv)
    if not config:
        return

    bot = Bot(config, True, con)
    bot.run()


def main(argv):
    config = parseConfigFile(argv)
    if not config:
        return

    bot = Bot(config)
    bot.run()


if __name__ == "__main__":
    main(sys.argv)
