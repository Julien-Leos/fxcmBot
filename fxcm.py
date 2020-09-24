import fxcmpy
import datetime as dt
import pandas as pd
from utils import Singleton


class Fxcm(Singleton):
    con = fxcmpy.fxcmpy(config_file='fxcm.cfg')

    forexPair = 'EUR/USD'

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

    def subscribeMarket(self, callback=[]):
        self.con.subscribe_market_data(self.forexPair, callback)

    def unsubscribeMarket(self):
        self.con.subscribe_market_data(self.forexPair)

    def displayDataFrame(self, dataFrame):
        pd.set_option('display.max_rows', dataFrame.shape[0] + 1)
        print(dataFrame)
        pd.reset_option('display.max_rows')

    def close(self):
        """Close the connection with fxcm API
        """
        self.con.close()
