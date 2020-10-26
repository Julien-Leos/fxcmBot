from fxcm import Fxcm
from dev.FxcmBacktest import FxcmBacktest
import sys
import tools.utils as utils


class Bot():
    fxcm = None
    algo = None
    config = None

    def __init__(self, config, algo, con=None):
        if config['backtest'] == 'false':
            self.fxcm = Fxcm(config, con)
        else:
            self.fxcm = FxcmBacktest(config, con)
        # Will automatically import strategy instead by .config.strategy
        self.algo = algo(self.fxcm, config)
        self.config = config

    def run(self):
        while True:
            (newCandle, allCandles) = self.fxcm.getNewCandle()
            self.algo.nextTick(newCandle, allCandles)
            if newCandle.empty:
                break


def mainDev(config, algo, con):
    config['devEnv'] = True
    bot = Bot(config, algo, con)
    bot.run()


def main(argv):
    config = utils.parseConfigFile(argv)
    if not config:
        return

    config['devEnv'] = False
    algo = getattr(__import__(config['strategy']), config['strategy'])
    bot = Bot(config, algo)
    bot.run()


if __name__ == "__main__":
    main(sys.argv)
