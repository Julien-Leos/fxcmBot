import fxcmpy
import signal
import datetime as dt
import pandas as pd

from time import sleep
from utils import *


class Fxcm():
    con = None

    forexPair = 'EUR/USD'
    config = None
    isRunning = True

    candles = None

    def __init__(self, config, con):
        if config['devEnv'] == False:
            self.con = fxcmpy.fxcmpy(config_file='config/fxcm.cfg')
        else:
            self.con = con

        self.config = config
        candleColumns = self.getCandles(config['period'], number=1).columns
        self.candles = pd.DataFrame(columns=candleColumns)

        # End bot when Trigger Crtl-C
        signal.signal(signal.SIGINT, self.__end)

    def getAccountInfo(self):
        return self.con.get_accounts('list')[0]

    def setForexPair(self, newForexPair):
        """Set a new pair of Forex to work with

        Args:
            newForexPair (str): New pair of Forex
        """
        self.forexPair = newForexPair

    def getForexPair(self):
        """Get the actual pair of Forex

        Returns:
            str: Actual pair of Forex
        """
        return self.forexPair

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
        return self.con.get_candles(self.forexPair, period=period, number=number, start=start, end=end, columns=columns)

    def buy(self, amount, limit=None, stop=None):
        """Open a buy position for the current Forex pair.

        Args:
            amount (int): Number of lot you want to buy
            limit (float, optional): Price above which it will automatically close the position. Defaults to None.
            stop (float, optional): Price under which it will automatically close the position. Defaults to None.

        Returns:
            positionId: Id of the position opened
        """
        order = self.con.open_trade(symbol=self.forexPair, is_buy=True, amount=amount,
                                    order_type="AtMarket", time_in_force="GTC", limit=limit, stop=stop)
        sleep(10)  # Sleep so the order can became an opened position

        if order:
            return order.get_tradeId()
        return None

    def sell(self, amount, limit=None, stop=None):
        """Open a sell position for the current Forex pair.

        Args:
            amount (int): Number of lot you want to sell
            limit (float, optional): Price under which it will automatically close the position. Defaults to None.
            stop (float, optional): Price above which it will automatically close the position. Defaults to None.

        Returns:
            positionId: Id of the position opened
        """
        order = self.con.open_trade(symbol=self.forexPair, is_buy=False, amount=amount,
                                    order_type="AtMarket", time_in_force="GTC", limit=limit, stop=stop)
        sleep(10)  # Sleep so the order can became an opened position

        if order:
            return order.get_tradeId()
        return None

    def getOpenPositions(self, kind="dataframe"):
        """Get all opened positions

        Args:
            kind (str, optional): How to return the data. Possible values are: 'dataframe' or 'list'. Defaults to "dataframe"".
        """
        return self.con.get_open_positions(kind)

    def getOpenPosition(self, positionId):
        """Get an opened position by his Id

        Args:
            positionId (int): Id of the position
        """
        try:
            return self.con.get_open_position(positionId)
        except:
            return None

    def getClosePositions(self, kind="dataframe"):
        """Get all closed positions

        Args:
            kind (str, optional): How to return the data. Possible values are: 'dataframe' or 'list'. Defaults to "dataframe"".
        """
        return self.con.get_closed_positions(kind)

    def getClosePosition(self, positionId):
        """Get a closed position by his Id

        Args:
            positionId (int): Id of the position
        """
        try:
            return self.con.get_closed_position(positionId)
        except:
            return None

    def closePositions(self):
        self.con.close_all()

    def closePosition(self, positionId):
        """Close a position by his Id

        Args:
            positionId (int): Id of the position
        """
        positionToClose = self.getOpenPosition(positionId)

        if positionToClose:
            positionToClose.close()
            return True
        return False

    def __end(self, sig, frame):
        print("\nEnding Bot...")
        self.isRunning = False

    def __getNextCandle(self):
        while self.isRunning:
            nextCandle = self.getCandles(
                self.config['period'], number=1).iloc[0]

            # End bot when end_date is reached
            if nextCandle.name >= dt.datetime.strptime(self.config['end_date'], "%Y/%m/%d %H:%M"):
                print("Bot 'end_date' reached.\nEnding Bot...")
                break

            # Return next candle if not the same as previous candle
            if self.candles.empty or not isDiffCandle(nextCandle, self.candles.iloc[-1]):
                self.candles = self.candles.append(nextCandle)
                return (nextCandle, self.candles)

            # Display prompt and sleep 1 second
            print("# Algorithm's last run at %s" %
                  nextCandle.name, end="\r")
            print("\033[A")
            sleep(1)
        return None
