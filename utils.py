import configparser
import pandas as pd


def displayDataFrame(dataFrame):
    """Display a panda's dataFrame object.

    Args:
        dataFrame (dataFrame): dataFrame object to display
    """
    pd.set_option('display.max_rows', dataFrame.shape[0] + 1)
    pd.set_option('display.max_columns', dataFrame.shape[1] + 1)
    print(dataFrame)
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')


def isDiffCandle(candle1, candle2):
    return candle1.name == candle2.name


def parseConfigFile(argv):
    config = configparser.ConfigParser()
    try:
        config.read(argv[1])
        if not 'FXCM_BOT' in config or not 'backtest' in config['FXCM_BOT']:
            raise Exception("Missing FXCM_BOT section or backtest field")
        if not 'end_date' in config['FXCM_BOT'] or (config['FXCM_BOT']['backtest'] == 'true' and not 'start_date' in config['FXCM_BOT']):
            raise Exception("Missing start_date or end_date fields")
        return dict(config['FXCM_BOT'])
    except Exception as error:
        print("Error while parsing config file '%s': %s" % (argv[1], error))
        return None
