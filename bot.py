import sys
import datetime as dt
import pandas as pd
from time import sleep

from utils import dateDiffInMillisecond, parseConfigFile
from fxcm import Fxcm
from FxcmBacktest import FxcmBacktest
from algorithm import Algorithm


class Bot():
    fxcm = None
    algo = None
    config = None

    def __init__(self, config, con=None):
        if config['backtest'] == 'false':
            self.fxcm = Fxcm(config, con)
        else:
            self.fxcm = FxcmBacktest(config, con)
        self.algo = Algorithm(self.fxcm, config)
        self.config = config

    def run(self):
        while True:
            nextCandle = self.fxcm.getNextCandle()
            if not nextCandle:
                break
            self.algo.nextTick(nextCandle[0], nextCandle[1])


def mainDev(con, argv):
    config = parseConfigFile(argv)
    if not config:
        return

    config['devEnv'] = True
    bot = Bot(config, con)
    bot.run()


def main(argv):
    config = parseConfigFile(argv)
    if not config:
        return

    config['devEnv'] = False
    bot = Bot(config)
    bot.run()


if __name__ == "__main__":
    main(sys.argv)
