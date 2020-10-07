import configparser
import pandas as pd
from threading import Timer


def displayDataFrame(dataFrame):
    """Display a panda's dataFrame object.

    Args:
        dataFrame (dataFrame): dataFrame object to display
    """
    pd.set_option('display.max_rows', dataFrame.shape[0] + 1)
    print(dataFrame)
    pd.reset_option('display.max_rows')


def dateDiffInMillisecond(date1, date2):
    delta = date1 - date2
    return (delta.days * 24 * 60 * 60 * 1000) + (delta.seconds * 1000) + (delta.microseconds / 1000)


def parseConfigFile(argv):
    config = configparser.ConfigParser()
    try:
        config.read(argv[1])
        if not 'FXCM_BOT' in config or not 'test_mode' in config['FXCM_BOT']:
            raise Exception("No FXCM_BOT section or test_mode field")
        if config['FXCM_BOT']['test_mode'] == 'true' and (not 'start_date' in config['FXCM_BOT'] or not 'end_date' in config['FXCM_BOT']):
            raise Exception("No start_date or end_date fields")
        return config['FXCM_BOT']
    except Exception as error:
        print("Error while parsing config file '%s': %s" % (argv[1], error))
        return None


class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
