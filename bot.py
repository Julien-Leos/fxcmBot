from fxcm import Fxcm
from FxcmBacktest import FxcmBacktest
from algorithm import Algorithm
import sys
import utils


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
            (newCandle, allCandles) = self.fxcm.getNewCandle()
            self.algo.nextTick(newCandle, allCandles)
            if newCandle.empty:
                break


def mainDev(con, argv):
    config = utils.parseConfigFile(argv)
    if not config:
        return

    config['devEnv'] = True
    bot = Bot(config, con)
    bot.run()


def main(argv):
    config = utils.parseConfigFile(argv)
    if not config:
        return

    config['devEnv'] = False
    bot = Bot(config)
    bot.run()


if __name__ == "__main__":
    main(sys.argv)
