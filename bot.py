import sys
import datetime as dt
import pandas as pd
from time import sleep

from utils import dateDiffInMillisecond, parseConfigFile
from fxcm import Fxcm, FxcmTest
from algorithm import Algorithm


class Bot():
    fxcm = None
    algo = None
    config: None

    isRunning = True

    def __init__(self, config, devEnd, con=None):
        if config.getboolean('test_mode') == False:
            self.fxcm = Fxcm(config, devEnd, con)
        else:
            self.fxcm = FxcmTest(config, devEnd, con)
        self.algo = Algorithm(self.fxcm, config)
        self.config = config

    def run(self):
        self.fxcm.subscribeMarket([self.algo.runNextInstance])
        while self.isRunning:
            sleep(10.5)  # Le programme dure 2 secondes et s'arrête
            self.fxcm.unsubscribeMarket()
            self.isRunning = False


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

    bot = Bot(config, False)
    bot.run()


if __name__ == "__main__":
    main(sys.argv)
