import fxcmpy
import datetime as dt
import pandas as pd
import time
from threading import Timer
from utils import *


class Fxcm():
    con = None

    forexPair = 'EUR/USD'
    config = None

    def __init__(self, config, devEnv, con):
        if devEnv == False:
            self.con = fxcmpy.fxcmpy(config_file='config/fxcm.cfg')
        else:
            self.con = con

        self.config = config

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

    def subscribeMarket(self, callbacks=[]):
        """Subscribe to the realtime market price of the current Forex pair.

        Args:
            callbacks (list, optional): List of the callbacks to call each time the market price evolves. Callback's parameter should be as follow:
                - data (dict): All informations about the new market price (such as date, askPrice, bidPrice etc...).
                - dataframe (list): List of all the previous and newly added market prices since the subscription to the market.
                Defaults to [].
        """
        self.con.subscribe_market_data(self.forexPair, callbacks)

    def unsubscribeMarket(self):
        """Unsubscribe from current subscribed market.
        """
        self.con.unsubscribe_market_data(self.forexPair)

    def buy(self, amount, orderType='AtMarket', rate=0.0, marketRange=0.0, limit=None, stop=None, inPips=False, trailingStep=None):
        """Place a buy order for the current Forex pair.

        Args:
            amount (int): Number of lot you want to buy
            orderType (str, optional): Type of order you want to place. Possible values are: 'AtMarket' or 'MarketRange'. Defaults to 'AtMarket'. For more informations on orderType see: https://www.fxcm.com/markets/education/video/order-types/market-range-vs-at-best-orders/
            rate (float): If orderType equals 'MarketRange', price at which you want to place the order. Defaults to 0.
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

    def sell(self, amount, orderType='AtMarket', rate=0.0, marketRange=0.0, limit=None, stop=None, inPips=False, trailingStep=None):
        """Place a sell order for the current Forex pair.

        Args:
            amount (int): Number of lot you want to sell
            orderType (str, optional): Type of order you want to place. Possible values are: 'AtMarket' or 'MarketRange'. Defaults to 'AtMarket'. For more informations on orderType see: https://www.fxcm.com/markets/education/video/order-types/market-range-vs-at-best-orders/
            rate (float): If orderType equals 'MarketRange', price at which you want to place the order. Defaults to 0.
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

    def getOpenPosition(self, positionId):
        """Get a position by his Id

        Args:
            positionId (int): Id of the position
        """
        return self.con.get_open_position(positionId)

    def closePosition(self, positionId):
        """Close a position by his Id

        Args:
            positionId (int): Id of the position
        """
        self.getOpenPosition(positionId).close()

    def deleteOrder(self, order):
        """Delete an unexecuted order

        Args:
            orderId (int): Id of the order
        """
        order.delete()


class FxcmTest():
    con = None

    forexPair = 'EUR/USD'
    config = None

    leftCandles = None
    candles = None
    orders = list()
    marketThread = None

    LOT_SIZE = 10000
    ACCOUNT_CURRENCY = 'EUR'

    def __init__(self, config, devEnv, con):
        if devEnv == False:
            self.con = fxcmpy.fxcmpy(config_file='config/fxcm.cfg')
        else:
            self.con = con

        startDate = dt.datetime.strptime(
            config['start_date'], "%Y/%m/%d %H:%M")
        endDate = dt.datetime.strptime(
            config['end_date'], "%Y/%m/%d %H:%M")

        self.config = config
        self.leftCandles = self.getCandles('m1', start=startDate, end=endDate)
        self.candles = pd.DataFrame(columns=self.leftCandles.columns)

    def setForexPair(self, newForexPair):
        self.forexPair = newForexPair

    def getForexPair(self):
        return self.forexPair

    def getCandles(self, period, number=10, start=None, end=None, columns=[]):
        return self.con.get_candles(self.forexPair, period=period, number=number, start=start, end=end, columns=columns)

    def subscribeMarket(self, callbacks=[]):
        self.marketThread = RepeatedTimer(
            int(self.config['stream_period']) / 1000, self.feedMarketThread, callbacks)

    def unsubscribeMarket(self):
        self.marketThread.stop()

    def buy(self, amount, orderType='AtMarket', rate=0.0, marketRange=0.0, limit=None, stop=None, inPips=False, trailingStep=None):
        return self.initOrder(True, amount, limit, stop)

    def sell(self, amount, orderType='AtMarket', rate=0.0, marketRange=0.0, limit=None, stop=None, inPips=False, trailingStep=None):
        return self.initOrder(False, amount, limit, stop)

    def getOpenPosition(self, positionId):
        pass

    def closePosition(self, positionId):
        pass

    def deleteOrder(self, order):
        pass

    def feedMarketThread(self, callbacks):
        # Get newCandle and remove newCandle from leftover candles
        newCandle = self.leftCandles.iloc[0]
        self.candles = self.candles.append(newCandle)
        self.leftCandles = self.leftCandles.iloc[1:]

        # Update all orders with new Candle
        for order in self.orders:
            order = self.updateOrderValues(order, newCandle)

        # Call each callbacks with newCandle
        for callback in callbacks:
            callback(newCandle, self.candles)

    def initOrder(self, isBuy, amount, limit, stop):
        lastCandle = self.getLastCandle()
        print(lastCandle)
        newOrder = pd.Series({
            "amountK": amount,
            "currency": self.forexPair,
            "isBuy": isBuy,
            "limit": limit,  # Transformer de pips en valeur brute si inPips == True
            "stop": stop,  # Transformer de pips en valeur brute si inPips == True
            "time": int(dt.datetime.timestamp(lastCandle.name)),
            "tradeId": len(self.orders),
            # Should be calculated every tick but it is too consuming
            "pipCost": self.getPipCost(self.forexPair, lastCandle.name)
        })
        newOrder['open'] = lastCandle['askclose'] if newOrder['isBuy'] == True else lastCandle['bidclose']
        newOrder = self.updateOrderValues(newOrder, lastCandle)

        self.orders.append(newOrder)
        return newOrder

    def updateOrderValues(self, order, lastCandle):
        if order['isBuy'] == True:
            order['close'] = lastCandle['bidclose']
            order['grossPL'] = (order['close'] - order['open']) * self.LOT_SIZE
        else:
            order['close'] = lastCandle['askclose']
            order['grossPL'] = (order['open'] - order['close']) * self.LOT_SIZE
        order['visiblePL'] = order['grossPL'] * order['pipCost']

        return order

    def getPipCost(self, forexPair, date):
        if forexPair.find('JPY') == -1:
            multiplier = 0.0001
        else:
            multiplier = 0.01

        forexPairExchangeValue = self.con.get_candles(
            forexPair, period='m1', number=1, start=date, end=date)['askclose'].iloc[0]
        if forexPair.find(self.ACCOUNT_CURRENCY) != -1:
            return multiplier / forexPairExchangeValue * (self.LOT_SIZE / 10)
        else:
            forexPairSecond = forexPair.split('/')[1]
            return self.getPipCost(self.ACCOUNT_CURRENCY + '/' + forexPairSecond)

    def getLastCandle(self):
        if len(self.candles) == 0:
            return self.leftCandles.iloc[0]
        return self.candles.iloc[-1]
