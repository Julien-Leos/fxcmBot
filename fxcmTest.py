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
        self.leftCandles = self.getCandles(config['period'], start=startDate, end=endDate)
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

    def buy(self, amount, limit=None, stop=None, trailingStep=None):
        return self.initOrder(True, amount, limit, stop, trailingStep)

    def sell(self, amount, limit=None, stop=None, trailingStep=None):
        return self.initOrder(False, amount, limit, stop, trailingStep)

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

    def initOrder(self, isBuy, amount, limit, stop, trailingStep):
        lastCandle = self.getLastCandle()
        print(lastCandle)
        newOrder = pd.Series({
            "amountK": amount,
            "currency": self.forexPair,
            "isBuy": isBuy,
            "limit": limit,
            "stop": stop,
            "time": int(dt.datetime.timestamp(lastCandle.name)),
            "tradeId": len(self.orders),
            # Should be calculated every tick but it is too consuming
            "pipCost": self.getPipCost(self.forexPair, lastCandle.name)
        })
        newOrder['open'] = lastCandle['askclose'] if newOrder['isBuy'] == True else lastCandle['bidclose']
        newOrder = self.updateOrderValues(newOrder, lastCandle)

        self.orders.append(newOrder)
        return newOrder['tradeId']

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


# class FxcmOrderTest():
#     order = None

#     fxcm = None

#     def __init__(self, fxcm, orderId, tradeId, forexPair, isBuy, amount, limit, stop, lastCandle):
#         self.fxcm = fxcm

#         self.order = pd.Series({
#             amountK: amount,
#             isBuy: isBuy,
#             buy: lastCandle['askclose'] if isBuy == True else 0,
#             sell: lastCandle['bidclose'] if isBuy == False else 0,
#             currency: forexPair,
#             limit: limit if limit != None else 0,
#             stop: stop if stop != None else 0,
#             isLimitOrder: True if limit != None else False,
#             isStopOrder: True if stop != None else False,
#             orderId: orderId,
#             tradeId: tradeId,
#             status: "Waiting",
#             time: int(dt.datetime.timestamp(lastCandle.name)),
#             type: 'AM'
#         })

#     def get_amount():
#         return self.order['amountK']

#     def get_associated_trade():
#         return self.fxcm.get
