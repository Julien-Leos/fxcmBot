import fxcmpy
import signal
import datetime as dt
import pandas as pd

from time import sleep
from utils import *


class FxcmBacktest():
    START_AMOUNT = 50000

    __con = None

    __forexPair = 'EUR/USD'
    __config = None

    __account = dict({
        'balance': START_AMOUNT,
        'equity': START_AMOUNT,
        'usableMargin': START_AMOUNT,
        'usdMr': 0,
        'grossPL': 0
    })
    __leftCandles = None
    __candles = None

    __openPositions = list()
    __closePositions = list()

    def __init__(self, config, con):
        if config['devEnv'] == False:
            self.__con = fxcmpy.fxcmpy(config_file='config/fxcm.cfg')
        else:
            self.__con = con

        startDate = dt.datetime.strptime(
            config['start_date'], "%Y/%m/%d %H:%M")
        endDate = dt.datetime.strptime(
            config['end_date'], "%Y/%m/%d %H:%M")

        self.__config = config
        self.__leftCandles = self.getCandles(
            config['period'], start=startDate, end=endDate)
        self.__candles = pd.DataFrame(columns=self.__leftCandles.columns)

        # End bot when Trigger Crtl-C
        signal.signal(signal.SIGINT, self.__end)

    def getAccountInfo(self):
        return self.__account

    def setForexPair(self, newForexPair):
        """Set a new pair of Forex to work with

        Args:
            newForexPair (str): New pair of Forex
        """
        self.__forexPair = newForexPair

    def getForexPair(self):
        """Get the actual pair of Forex

        Returns:
            str: Actual pair of Forex
        """
        return self.__forexPair

    def getCandles(self, period, number=10, start=None, end=None, columns=[]):
        """Return historical market data from the fxcm database

        Args:
            period (str): Granularity of the data. Possible values are: ‘m1’, ‘m5’, ‘m15’, ‘m30’, ‘H1’, ‘H2’, ‘H3’, ‘H4’, ‘H6’, ‘H8’, ‘D1’, ‘W1’, or ‘M1’.
            number (int, optional): Number of candles to receive. Defaults to 10.
            start (datetime, optional): First date to receive data for. Defaults to None.
            end (datetime, optional): Last date to receive data for. Defaults to None.
            columns (list, optional): List of column labels the result should include. If empty, all columns are returned. Possible values are: ‘date’, ‘bidopen’, ‘bidclose’, ‘bidhigh’, ‘bidlow’, ‘askopen’, ‘askclose’, ‘askhigh’, ‘asklow’, ‘tickqty’. Also available is ‘asks’ as shortcut for all ask related columns and ‘bids’ for all bid related columns, respectively. Defaults to [].

        Returns:
            DataFrame: Requested data
        """
        return self.__con.get_candles(self.__forexPair, period=period, number=number, start=start, end=end, columns=columns)

    def buy(self, amount, limit=None, stop=None):
        return self.__openPosition(True, amount, limit, stop)

    def sell(self, amount, limit=None, stop=None):
        return self.__openPosition(False, amount, limit, stop)

    def getOpenPositions(self, kind="dataframe"):
        """Get all opened positions

        Args:
            kind (str, optional): How to return the data. Possible values are: 'dataframe' or 'list'. Defaults to "dataframe"".
        """
        positionsList = [position.get_position()
                         for position in self.__openPositions]
        if kind == 'dataframe':
            return pd.DataFrame(data=positionsList)
        return positionsList

    def getOpenPosition(self, positionId):
        """Get an opened position by his Id

        Args:
            positionId (int): Id of the position
        """
        return next(position for position in self.__openPositions if position.get_tradeId() == positionId)

    def getClosePositions(self, kind="dataframe"):
        """Get all closed positions

        Args:
            kind (str, optional): How to return the data. Possible values are: 'dataframe' or 'list'. Defaults to "dataframe"".
        """
        positionsList = [position.get_position()
                         for position in self.__closePositions]
        if kind == 'dataframe':
            return pd.DataFrame(data=positionsList)
        return positionsList

    def getClosePosition(self, positionId):
        """Get a closed position by his Id

        Args:
            positionId (int): Id of the position
        """
        return next(position for position in self.__closePositions if position.get_tradeId() == positionId)

    def closePositions(self):
        for position in self.__openPositions:
            self.closePosition(position.get_tradeId())

    def closePosition(self, positionId):
        """Close a position by his Id

        Args:
            positionId (int): Id of the position
        """
        position = self.getPosition(positionId)

        self.__account['balance'] += position.get_grossPL()
        self.__account['usdMr'] -= position.get_usedMargin()
        self.__openPositions.remove(position)
        self.__closePositions.append(FxcmBacktestClosePosition(position))
        self.__updateAccountInfo()
        return True

    def __end(self, sig, frame):
        print("\nEnding Bot...")
        self.__leftCandles = self.__leftCandles[0:0]

    def __updateAccountInfo(self):
        newGrossPL = sum([position.get_grossPL()
                          for position in self.__openPositions])

        self.__account['grossPL'] = newGrossPL
        self.__account['equity'] = self.__account['balance'] + newGrossPL
        self.__account['usableMargin'] = self.__account['equity'] - \
            self.__account['usdMr']

    def __getNextCandle(self):
        # End bot when there is no leftover candles
        if self.__leftCandles.empty:
            return None

        # Get nextCandle and remove nextCandle from leftover candles
        nextCandle = self.__leftCandles.iloc[0]
        self.__candles = self.__candles.append(nextCandle)
        self.__leftCandles = self.__leftCandles.iloc[1:]

        # Update all positions with new Candle
        for position in self.__openPositions:
            position.update(nextCandle)
        self.__updateAccountInfo()

        return (nextCandle, self.__candles)

    def __openPosition(self, isBuy, amount, limit, stop):
        lastCandle = self.__getLastCandle()
        newPosition = FxcmBacktestOpenPosition(
            self.__con, lastCandle, len(self.__openPositions), self.__forexPair, isBuy, amount, limit, stop)

        self.__account['usdMr'] += newPosition.get_usedMargin()
        if self.__account['equity'] - self.__account['usdMr'] < 0:
            print("Bot: Can't open position %s: Not enough usable margin." %
                  newPosition.get_tradeId())
            return None

        self.__openPositions.append(newPosition)
        return newPosition.get_tradeId()

    def __getLastCandle(self):
        if len(self.__candles) == 0:
            return self.__leftCandles.iloc[0]
        return self.__candles.iloc[-1]


class FxcmBacktestOpenPosition():
    LOT_SIZE = 10000
    ACCOUNT_CURRENCY = 'EUR'
    MMR = 16.65

    __con = None
    __position = None

    def __init__(self, con, lastCandle, tradeId, forexPair, isBuy, amount, limit, stop):
        self.__con = con

        self.__position = pd.Series({
            'tradeId': tradeId,
            'currency': forexPair,
            'currencyPoint': self.__getPipCost(forexPair, lastCandle.name),
            'isBuy': isBuy,
            'amountK': amount,
            'time': lastCandle.name,
            'limit': limit or 0,
            'stop': stop or 0,
            'open': lastCandle['askclose'] if isBuy else lastCandle['bidclose'],
            'close': 0,
            'grossPL': 0,
            'visiblePL': 0,
            # I don't know how to compute MMR (16.65 is commonly used but not always)
            'usedMargin': self.MMR
        })
        self.update(lastCandle)

    def update(self, lastCandle):
        if self.__position['isBuy'] == True:
            self.__position['close'] = lastCandle['bidclose']
            self.__position['grossPL'] = (self.__position['close'] -
                                          self.__position['open']) * self.LOT_SIZE
        else:
            self.__position['close'] = lastCandle['askclose']
            self.__position['grossPL'] = (
                self.__position['open'] - self.__position['close']) * self.LOT_SIZE
        self.__position['visiblePL'] = self.__position['grossPL'] * \
            self.__position['currencyPoint']

    def get_position(self):
        return self.__position

    def get_tradeId(self):
        return self.__position['tradeId']

    def get_currency(self):
        return self.__position['currency']

    def get_currencyPoint(self):
        return self.__position['currencyPoint']

    def get_isBuy(self):
        return self.__position['isBuy']

    def get_amount(self):
        return self.__position['amountK']

    def get_time(self):
        return self.__position['time']

    def get_limit(self):
        return self.__position['limit']

    def get_stop(self):
        return self.__position['stop']

    def get_open(self):
        return self.__position['open']

    def get_close(self):
        return self.__position['close']

    def get_grossPL(self):
        return self.__position['grossPL']

    def get_visiblePL(self):
        return self.__position['visiblePL']

    def get_usedMargin(self):
        return self.__position['usedMargin']

    def __getPipCost(self, forexPair, date):
        if forexPair.find('JPY') == -1:
            multiplier = 0.0001
        else:
            multiplier = 0.01

        forexPairExchange = self.__con.get_candles(
            forexPair, period='m1', number=1, start=date, end=date, columns=["askopen"])
        if forexPairExchange.size == 0:
            return self.__getPipCost(forexPair, date - dt.timedelta(minutes=1))
        forexPairExchangeValue = forexPairExchange['askopen'].iloc[0]
        if forexPair.find(self.ACCOUNT_CURRENCY) != -1:
            return multiplier / forexPairExchangeValue * (self.LOT_SIZE / 10)
        else:
            forexPairSecond = forexPair.split('/')[1]
            return self.__getPipCost(self.ACCOUNT_CURRENCY + '/' + forexPairSecond)


class FxcmBacktestClosePosition():
    __position = None

    def __init__(self, openPosition):
        self.__position = pd.Series({
            'tradeId': openPosition.get_tradeId(),
            'currency': openPosition.get_currency(),
            'currencyPoint': openPosition.get_currencyPoint(),
            'isBuy': openPosition.get_isBuy(),
            'amountK': openPosition.get_amount(),
            'open': openPosition.get_open(),
            'close': openPosition.get_close(),
            'grossPL': openPosition.get_grossPL(),
            'visiblePL': openPosition.get_visiblePL(),
        })

    def get_position(self):
        return self.__position

    def get_tradeId(self):
        return self.__position['tradeId']

    def get_currency(self):
        return self.__position['currency']

    def get_currencyPoint(self):
        return self.__position['currencyPoint']

    def get_isBuy(self):
        return self.__position['isBuy']

    def get_amount(self):
        return self.__position['amountK']

    def get_open(self):
        return self.__position['open']

    def get_close(self):
        return self.__position['close']

    def get_grossPL(self):
        return self.__position['grossPL']

    def get_visiblePL(self):
        return self.__position['visiblePL']
