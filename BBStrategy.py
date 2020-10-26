from algorithm import Algorithm
from tools.graph import Graph
from tools.indicator import Indicator


class BBStrategy(Algorithm):
    BB_PERIOD = 20
    BB_M1_TRENDING = 0.0005
    BB_M5_TRENDING = 0.0017

    m5Candles = None

    bbTrending = None

    def tick(self, nextCandle, allCandles):
        # lastm5CandleSize = self.m5Candles.shape[0]
        # self.m5Candles = self.getUpperPeriod(
        #     self.m5Candles, 5, nextCandle, allCandles)
        # if self.m5Candles.shape[0] == lastm5CandleSize:
        #     return

        # if self.m5Candles.shape[0] < self.BB_PERIOD:
        #     return

        if allCandles.shape[0] < self.BB_PERIOD:
            return

        if len(self.fxcm.getClosePositions('list')) > 0:  # TO REMOVE
            return

        askBbCandles = allCandles['askclose'][-20:]
        bidBbCandles = allCandles['bidclose'][-20:]
        bb = dict({'askbb': Indicator.bb(askBbCandles, 20),
                   'bidbb': Indicator.bb(bidBbCandles, 20)})

        self.getBbTrending(bb, nextCandle)

        if self.bbTrending == False:
            if self.isAnyPositionOpen():  # Look for closing position
                position = self.fxcm.getOpenPositions('list')[0]
                if (position['isBuy'] and self.isPriceAboveBbMid(nextCandle['askclose'], bb['askbb']['mid'])) or (not position['isBuy'] and self.isPriceUnderBbMid(nextCandle['bidclose'], bb['bidbb']['mid'])):
                    print(position)
                    self.fxcm.closePosition(position['tradeId'])
            else:  # Try open position
                if self.isPriceAboveBbUp(nextCandle['askclose'], bb['askbb']['up']):
                    print("SELL")
                    self.fxcm.sell(1, limit=4, stop=-2)
                elif self.isPriceUnderBbLow(nextCandle['bidclose'], bb['bidbb']['low']):
                    print("BUY")
                    self.fxcm.buy(1, limit=4, stop=-2)
        else:
            self.fxcm.closePositions()

    def getBbTrending(self, bb, nextCandle):
        newBbTrending = self.isTrending(bb['askbb'])
        if self.bbTrending == None or self.bbTrending != newBbTrending:
            print("TREND CHANGE")
            self.bbTrending = newBbTrending
            Graph.addAction(
                nextCandle.name, bb['askbb']['mid'][-1], 0, 'TRENDING' if newBbTrending else 'TRENDLESS', True if newBbTrending else False, 1)
            Graph.addAction(
                nextCandle.name, bb['bidbb']['mid'][-1], 0, 'TRENDING' if newBbTrending else 'TRENDLESS', True if newBbTrending else False, 2)

    def isPriceAboveBbUp(self, price, bbUp):
        return price >= bbUp[-1]

    def isPriceUnderBbLow(self, price, bblow):
        return price <= bblow[-1]

    def isPriceUnderBbMid(self, price, bbMid):
        return price <= bbMid[-1]

    def isPriceAboveBbMid(self, price, bbMid):
        return price >= bbMid[-1]

    def isTrending(self, bb):
        return bb['up'][-1] - bb['low'][-1] > self.BB_M1_TRENDING

    def start(self, firstCandle, allCandles):
        return

    def end(self, lastCandle, allCandles):
        accountInfo = self.fxcm.getAccountInfo()
        Graph.setTitle(
            "Final Account Equity: {} / BBStrategy".format(accountInfo['equity']))

        askbb = Indicator.bb(allCandles['askclose'], 20)
        Graph.addIndicator(
            x=allCandles.index.to_pydatetime(),
            y=askbb['up'],
            name='Ask BBup ',
            color="rgba(0, 0, 255, 0.6)"
        )

        Graph.addIndicator(
            x=allCandles.index.to_pydatetime(),
            y=askbb['mid'],
            name='Ask BBmid',
            color="rgba(0, 0, 200, 0.5)"
        )

        Graph.addIndicator(
            x=allCandles.index.to_pydatetime(),
            y=askbb['low'],
            name='Ask BBlow',
            color="rgba(0, 0, 180, 0.4)"
        )

        bidbb = Indicator.bb(allCandles['bidclose'], 20)
        Graph.addIndicator(
            x=allCandles.index.to_pydatetime(),
            y=bidbb['up'],
            name='Bid BBup ',
            color="rgba(0, 0, 255, 0.6)",
            plot=2
        )

        Graph.addIndicator(
            x=allCandles.index.to_pydatetime(),
            y=bidbb['mid'],
            name='Bid BBmid',
            color="rgba(0, 0, 200, 0.5)",
            plot=2
        )

        Graph.addIndicator(
            x=allCandles.index.to_pydatetime(),
            y=bidbb['low'],
            name='Bid BBlow',
            color="rgba(0, 0, 180, 0.4)",
            plot=2
        )
