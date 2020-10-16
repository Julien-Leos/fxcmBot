import fxcmpy
import datetime as dt
import pandas as pd
import signal
from time import sleep
from threading import Timer
from utils import *


class Fxcm():
    con = None

    forexPair = 'EUR/USD'
    config = None
    isRunning = True

    candles = None

    def __init__(self, config, devEnv, con):
        if devEnv == False:
            self.con = fxcmpy.fxcmpy(config_file='config/fxcm.cfg')
        else:
            self.con = con

        self.config = config
        candleColumns = self.getCandles(config['period'], number=1).columns
        self.candles = pd.DataFrame(columns=candleColumns)

        # End bot when Trigger Crtl-C
        signal.signal(signal.SIGINT, self.end)

    def end(self, sig, frame):
        print("\nEnding Bot...")
        self.isRunning = False

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

    def getNextCandle(self):
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
            print("SLEEP")
            sleep(1)
        return None

    def buy(self, amount, limit=None, stop=None, trailingStep=None):
        """Open a buy position for the current Forex pair.

        Args:
            amount (int): Number of lot you want to buy
            limit (float, optional): Price above which it will automatically close the position. Defaults to None.
            stop (float, optional): Price under which it will automatically close the position. Defaults to None.
            trailingStep (float, optional): Number of pips above which the stop rate will increase and guarantee the gains. Defaults to None.

        Returns:
            positionId: Id of the position opened
        """
        return self.con.open_trade(symbol=self.forexPair, is_buy=True, order_type="AtMarket", amount=amount, time_in_force="GTC", limit=limit, stop=stop, trailing_step=trailingStep).get_tradeId()

    def sell(self, amount, limit=None, stop=None, trailingStep=None):
        """Open a sell position for the current Forex pair.

        Args:
            amount (int): Number of lot you want to sell
            limit (float, optional): Price under which it will automatically close the position. Defaults to None.
            stop (float, optional): Price above which it will automatically close the position. Defaults to None.
            trailingStep (float, optional): Number of pips above which the stop rate will decrease and guarantee the gains. Defaults to None.

        Returns:
            positionId: Id of the position opened
        """
        return self.con.open_trade(symbol=self.forexPair, is_buy=False, order_type="AtMarket", amount=amount, time_in_force="GTC", limit=limit, stop=stop, trailing_step=trailingStep).get_tradeId()

    def getPositions(self, kind="dataframe"):
        """Get all positions

        Args:
            kind (str, optional): How to return the data. Possible values are: 'datframe' or 'list'. Defaults to "dataframe"".
        """
        return self.con.get_open_positions(kind)

    def getPosition(self, positionId):
        """Get a position by his Id

        Args:
            positionId (int): Id of the position
        """
        try:
            return self.con.get_open_position(positionId)
        except:
            return None

    def closePositions(self):
        positions = self.getPositions('list')

        for position in positions:
            self.closePosition(position['tradeId'])

    def closePosition(self, positionId):
        """Close a position by his Id

        Args:
            positionId (int): Id of the position

        Returns:
            [bool]: True if the position has been closed. False otherwise.
        """
        positionToClose = self.getPosition(positionId)

        if not positionToClose:
            return False
        positionToClose.close()
        return True
