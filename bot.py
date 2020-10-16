import sys
import datetime as dt
import pandas as pd
from time import sleep

from utils import dateDiffInMillisecond, parseConfigFile
from fxcm import Fxcm
from fxcmTest import FxcmTest
from algorithm import Algorithm


class Bot():
    fxcm = None
    algo = None
    config: None

    def __init__(self, config, devEnd, con=None):
        if config['test_mode'] == 'false':
            self.fxcm = Fxcm(config, devEnd, con)
        else:
            self.fxcm = FxcmTest(config, devEnd, con)
        self.algo = Algorithm(self.fxcm, config)
        self.config = config

    def run(self):
        while True:
            nextCandle = self.fxcm.getNextCandle()
            if not nextCandle:
                break
            self.algo.runNextInstance(nextCandle[0], nextCandle[1])

    def end(self, sig, frame):
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
