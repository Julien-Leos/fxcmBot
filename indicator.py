from pyti.exponential_moving_average import exponential_moving_average as ema
from pyti.bollinger_bands import upper_bollinger_band as bbup
from pyti.bollinger_bands import middle_bollinger_band as bbmid
from pyti.bollinger_bands import lower_bollinger_band as bblow

class Indicator():

    @staticmethod
    def ema(data, period):
        return ema(data, period)

    @staticmethod
    def bbup(data, period):
        return bbup(data, period)

    @staticmethod
    def bbmid(data, period):
        return bbmid(data, period)

    @staticmethod
    def bblow(data, period):
        return bblow(data, period)