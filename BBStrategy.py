from algorithm import Algorithm
from tools.graph import Graph
from tools.indicator import Indicator


class BBStrategy(Algorithm):
    BB_PERIOD = 25
    BB_M1_TRENDING = 0.0005
    BB_M5_TRENDING = 0.0017

    BB_SQUEEZE_WIDTH = 0.0006

    m5Candles = None

    bbTrending = 'no'
    bbSqueezing = None

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

        # if len(self.fxcm.getClosePositions('list')) > 0:  # TO REMOVE
        #     return

        askBbCandles = allCandles['askclose'][-self.BB_PERIOD:]
        bidBbCandles = allCandles['bidclose'][-self.BB_PERIOD:]
        bb = dict({'askbb': Indicator.bb(askBbCandles, self.BB_PERIOD),
                   'bidbb': Indicator.bb(bidBbCandles, self.BB_PERIOD)})

        # bbWidth = self.getBbWidth(bb['askbb'])

        bbWidth = bb['askbb']['up'][-1] - bb['askbb']['low'][-1]
        self.bbSqueezing = bbWidth <= self.BB_SQUEEZE_WIDTH

        if self.bbTrending != 'no':
            if (self.bbTrending == 'down' and self.isPriceAboveBbMid(nextCandle['askclose'], bb['askbb']['mid'])) or \
                    (self.bbTrending == 'up' and self.isPriceUnderBbMid(nextCandle['askclose'], bb['askbb']['mid'])):  # Look for end of trending
                self.bbTrending = 'no'
                # Graph.addAction(
                #     nextCandle.name, bb['askbb']['mid'][-1], 'TREENDLESS', False, 1)
                # Graph.addAction(
                #     nextCandle.name, bb['bidbb']['mid'][-1], 'TREENDLESS', False, 2)
        else:
            if self.isAnyPositionOpen():  # Look for closing position
                position = self.fxcm.getOpenPositions('list')[0]
                if (position['isBuy'] and self.isPriceAboveBbMid(nextCandle['askclose'], bb['askbb']['mid'])) or \
                        (not position['isBuy'] and self.isPriceUnderBbMid(nextCandle['bidclose'], bb['bidbb']['mid'])):
                    self.fxcm.closePosition(position['tradeId'])
            else:
                if self.isPriceAboveBbUp(nextCandle['askclose'], bb['askbb']['up']):
                    if self.bbSqueezing == True:
                        self.bbTrending = 'up'
                        # print("TREND UP")
                        # Graph.addAction(
                        #     nextCandle.name, bb['askbb']['mid'][-1], 'TRENDING UP', True, 1)
                        # Graph.addAction(
                        #     nextCandle.name, bb['bidbb']['mid'][-1], 'TRENDING UP', True, 2)
                    else:
                        print("SELL")
                        self.fxcm.sell(1500)
                elif self.isPriceUnderBbLow(nextCandle['bidclose'], bb['bidbb']['low']):
                    if self.bbSqueezing == True:
                        self.bbTrending = 'down'
                        # print("TREND DOWN")
                        # Graph.addAction(
                        #     nextCandle.name, bb['askbb']['mid'][-1], 'TRENDING DOWN', True, 1)
                        # Graph.addAction(
                        #     nextCandle.name, bb['bidbb']['mid'][-1], 'TRENDING DOWN', True, 2)
                    else:
                        print("BUY")
                        self.fxcm.buy(1500)

        # self.getBbTrending(bb, nextCandle)

        # if self.isAnyPositionOpen():  # Look for closing position
        #     position = self.fxcm.getOpenPositions('list')[0]
        #     if (position['isBuy'] and self.isPriceAboveBbMid(nextCandle['askclose'], bb['askbb']['mid'])) or \
        #             (not position['isBuy'] and self.isPriceUnderBbMid(nextCandle['bidclose'], bb['bidbb']['mid'])):
        #         self.fxcm.closePosition(position['tradeId'])
        # else:  # Try open position
        #     if self.isPriceAboveBbUp(nextCandle['askclose'], bb['askbb']['up']):
        #         print("SELL")
        #         self.fxcm.sell(1)
        #     elif self.isPriceUnderBbLow(nextCandle['bidclose'], bb['bidbb']['low']):
        #         print("BUY")
        #         self.fxcm.buy(1)

    def getBbWidth(self, bb):
        return list(map(lambda tuple: tuple[0] - tuple[1], list(zip(bb['up'], bb['low']))))

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

        askbb = Indicator.bb(allCandles['askclose'], self.BB_PERIOD)
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

        bidbb = Indicator.bb(allCandles['bidclose'], self.BB_PERIOD)
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

        bidbbWidth = self.getBbWidth(bidbb)
        Graph.addIndicator(
            x=allCandles.index.to_pydatetime(),
            y=bidbbWidth,
            name='Bid BB width',
            color="rgba(0, 0, 180, 0.4)",
            plot=3
        )

        askbbWidth = self.getBbWidth(askbb)
        Graph.addIndicator(
            x=allCandles.index.to_pydatetime(),
            y=askbbWidth,
            name='Ask BB width',
            color="rgba(0, 0, 180, 0.4)",
            plot=3
        )
