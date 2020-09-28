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
        """Subscribe to the realtime market price of the current Forex pair.

        Args:
            callback (list, optional): List of the callbacks to call each time the market price evolves. Callback's parameter should be as follow:
                - data (dict): All informations about the new market price (such as date, askPrice, bidPrice etc...).
                - dataframe (list): List of all the previous and newly added market prices since the subscription to the market.
                Defaults to [].
        """
        self.con.subscribe_market_data(self.forexPair, callback)

    def unsubscribeMarket(self):
        """Unsubscribe from current subscribed market.
        """
        self.con.subscribe_market_data(self.forexPair)

    def buy(self, rate, amount, orderType='AtMarket', marketRange=0.0, limit=None, stop=None, inPips=False, trailingStep=None):
        """Place a buy order for the current Forex pair.

        Args:
            rate (float): Price at which you want to place the order
            amount (int): Number of lot you want to buy
            orderType (str, optional): Type of order you want to place. Possible values are: 'AtMarket' or 'MarketRange'. Defaults to 'AtMarket'. For more informations on orderType see: https://www.fxcm.com/markets/education/video/order-types/market-range-vs-at-best-orders/
            marketRange (float, optional): If orderType equals 'MarketRange', defines in pips the range around the rate in which to place the order. Defaults to 0.
            limit (float, optional): Price above which it will automatically close the position. Defaults to None.
            stop (float, optional): Price under which it will automatically close the position. Defaults to None.
            inPips (bool, optional): Whether the limit and stop rates are defined in pips or not. Defaults to False.
            trailingStep (float, optional): Number of pips above which the stop rate will increase and guarantee the gains. Defaults to None.

        Returns:
            order: Order placed
        """
        return self.con.open_trade(symbol=self.forexPair, is_buy=True, amount=amount, order_type=orderType, time_in_force="GTC",
                                   rate=rate, is_in_pips=inPips, limit=limit, at_market=marketRange, stop=stop, trailing_step=trailingStep)

    def sell(self, rate, amount, orderType='AtMarket', marketRange=0.0, limit=None, stop=None, inPips=False, trailingStep=None):
        """Place a sell order for the current Forex pair.

        Args:
            rate (float): Price at which you want to place the order
            amount (int): Number of lot you want to sell
            orderType (str, optional): Type of order you want to place. Possible values are: 'AtMarket' or 'MarketRange'. Defaults to 'AtMarket'. For more informations on orderType see: https://www.fxcm.com/markets/education/video/order-types/market-range-vs-at-best-orders/
            marketRange (float, optional): If orderType equals 'MarketRange', defines in pips the range around the rate in which to place the order. Defaults to 0.
            limit (float, optional): Price under which it will automatically close the position. Defaults to None.
            stop (float, optional): Price above which it will automatically close the position. Defaults to None.
            inPips (bool, optional): Whether the limit and stop rates are defined in pips or not. Defaults to False.
            trailingStep (float, optional): Number of pips above which the stop rate will decrease and guarantee the gains. Defaults to None.

        Returns:
            order: Order placed
        """
        return self.con.open_trade(symbol=self.forexPair, is_buy=False, amount=amount, order_type=orderType, time_in_force="GTC",
                                   rate=rate, is_in_pips=inPips, limit=limit, at_market=marketRange, stop=stop, trailing_step=trailingStep)

    def closeByInfo(self, tradeId, amount):
        """Close a position by his trade id and his amount

        Args:
            tradeId (int): Id of the trade to close
            amount (int): Amount of the position in lot
        """
        self.con.close_trade(trade_id=tradeId, amount=amount)

    def closeByOrder(self, order):
        """Close a position by his order object

        Args:
            order ([type]): [description]
        """
        print("CLOSE ORDER %i OF %i lot" %
              (order.get_tradeId(), order.get_amount()))
        self.con.close_trade(trade_id=order.get_tradeId(), amount=order.get_amount())

    def displayDataFrame(self, dataFrame):
        """Display a panda's dataFrame object.

        Args:
            dataFrame (dataFrame): dataFrame object to display
        """
        pd.set_option('display.max_rows', dataFrame.shape[0] + 1)
        print(dataFrame)
        pd.reset_option('display.max_rows')

    def close(self):
        """Close the connection with fxcm API
        """
        self.con.close()
