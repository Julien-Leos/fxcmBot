import sys
import datetime as dt
import pandas as pd
from time import sleep

from utils import dateDiffInMillisecond, parseConfigFile
from fxcm import Fxcm, FxcmTest
from algorithm import Algorithm


class Bot():
    fxcm = None
    algo = Algorithm()

    config: None

    isRunning = True

    def __init__(self, config, devMode=False, con=None):
        if config.getboolean('test_mode') == False:
            self.fxcm = Fxcm(config, devMode, con)
        else:
            self.fxcm = FxcmTest(config, devMode, con)
        self.config = config

    def run(self):
        self.fxcm.subscribeMarket([self.newCandleEntry])
        while self.isRunning:
            sleep(2) # Le programme dure 2 secondes et s'arrête
            self.fxcm.unsubscribeMarket()
            self.isRunning = False

    def newCandleEntry(self, newCandle, allCandles):
        print(newCandle) # nouvelle bougie
        print(allCandles) # historique des bougies depuis le subscribe
        return

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
