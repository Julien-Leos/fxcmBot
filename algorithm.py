from graph import Graph
from datetime import datetime
from time import sleep
from indicator import Indicator
import pandas as pd


class Algorithm():
    BB_PERIOD = 20
    BB_M1_TRENDING = 0.0005
    BB_M5_TRENDING = 0.0017

    fxcm = None
    config = None

    askBbTrending = None
    bidBbTrending = None

    m5Candles = pd.DataFrame()

    def __init__(self, fxcm, config):
        self.fxcm = fxcm
        self.config = config

    def getUpperPeriod(self, periodCandles, period, newCandle, allCandles):
        if periodCandles.empty == True:
            periodCandles = periodCandles.append(newCandle)
        elif (newCandle.name - periodCandles.iloc[-1].name).seconds / 60 >= period:
            allPeriodCandles = allCandles.iloc[-period:]
            newPeriodCandle = pd.Series({'bidopen': allPeriodCandles.iloc[0]['bidopen'], 'bidlow': min(allPeriodCandles['bidlow']), 'bidhigh': max(allPeriodCandles['bidhigh']), 'bidclose': allPeriodCandles.iloc[-1]
                                         ['bidclose'], 'askopen': allPeriodCandles.iloc[0]['askopen'], 'asklow': min(allPeriodCandles['asklow']), 'askhigh': max(allPeriodCandles['askhigh']), 'askclose': allPeriodCandles.iloc[-1]['askclose'], 'tickqty': sum(allPeriodCandles['tickqty'])}, name=allPeriodCandles.iloc[-1].name)
            periodCandles = periodCandles.append(newPeriodCandle)
        return periodCandles

    def isTrending(self, bb):
        if bb['up'] - bb['low'] > self.BB_M5_TRENDING:
            return True
        return False

    def nextTick(self, newCandle, allCandles):
        if self.isFirstTick(allCandles):
            self.firstTick(newCandle, allCandles)
        elif self.isLastTick(newCandle):
            self.lastTick([self.m5Candles])
            return

        lastm5CandleSize = self.m5Candles.shape[0]
        self.m5Candles = self.getUpperPeriod(
            self.m5Candles, 5, newCandle, allCandles)
        if self.m5Candles.shape[0] == lastm5CandleSize:
            return

        if self.m5Candles.shape[0] < self.BB_PERIOD:
            return

        askBbCandles = self.m5Candles['askclose'][-20:]
        bidBbCandles = self.m5Candles['bidclose'][-20:]
        askbb = dict({'up': Indicator.bbup(askBbCandles, 20)[-1], 'low': Indicator.bblow(
            askBbCandles, 20)[-1], 'mid': Indicator.bbmid(askBbCandles, 20)[-1]})
        bidbb = dict({'up': Indicator.bbup(bidBbCandles, 20)[-1], 'low': Indicator.bblow(
            bidBbCandles, 20)[-1], 'mid': Indicator.bbmid(bidBbCandles, 20)[-1]})

        newAskBbTrending = self.isTrending(askbb)
        if self.askBbTrending == None or self.askBbTrending != newAskBbTrending:
            print("TREND CHANGE")
            self.askBbTrending = newAskBbTrending
            Graph.addAction(
                newCandle.name, askbb['mid'], 0, 'TRENDING' if newAskBbTrending else 'TRENDLESS', True if newAskBbTrending else False, True)

    def isFirstTick(self, allCandles):
        if len(allCandles) == 1:
            return True
        return False

    def firstTick(self, newCandle, allCandles):
        pass

    def isLastTick(self, newCandle):
        if newCandle.empty:
            return True
        return False

    def lastTick(self, allCandlesPeriods):
        self.fxcm.closePositions()

        accountInfo = self.fxcm.getAccountInfo()
        Graph.setTitle("Final Account Equity: {}".format(
            accountInfo['equity']))

        for allCandlesPeriod in allCandlesPeriods:
            period = (allCandlesPeriod.iloc[1].name -
                      allCandlesPeriod.iloc[0].name).seconds / 60

            Graph.addCandleSticks(
                x=allCandlesPeriod.index.to_pydatetime(),
                open=allCandlesPeriod['askopen'],
                high=allCandlesPeriod['askhigh'],
                low=allCandlesPeriod['asklow'],
                close=allCandlesPeriod['askclose'],
                name='Ask Candles ' + str(period))

            Graph.addCandleSticks(
                x=allCandlesPeriod.index.to_pydatetime(),
                open=allCandlesPeriod['bidopen'],
                high=allCandlesPeriod['bidhigh'],
                low=allCandlesPeriod['bidlow'],
                close=allCandlesPeriod['bidclose'],
                name='Ask Candles ' + str(period),
                plot=2)

            Graph.addIndicator(
                x=allCandlesPeriod.index.to_pydatetime(),
                y=Indicator.bbup(allCandlesPeriod['askclose'], 20),
                name='Ask BBup ' + str(period),
                color="rgba(0, 0, 255, 0.6)"
            )

            Graph.addIndicator(
                x=allCandlesPeriod.index.to_pydatetime(),
                y=Indicator.bbmid(allCandlesPeriod['askclose'], 20),
                name='Ask BBmid' + str(period),
                color="rgba(0, 0, 200, 0.5)"
            )

            Graph.addIndicator(
                x=allCandlesPeriod.index.to_pydatetime(),
                y=Indicator.bblow(allCandlesPeriod['askclose'], 20),
                name='Ask BBlow' + str(period),
                color="rgba(0, 0, 180, 0.4)"
            )

            Graph.addIndicator(
                x=allCandlesPeriod.index.to_pydatetime(),
                y=Indicator.bbup(allCandlesPeriod['bidclose'], 20),
                name='Bid BBup' + str(period),
                color="rgba(0, 0, 255, 0.6)",
                plot=2
            )

            Graph.addIndicator(
                x=allCandlesPeriod.index.to_pydatetime(),
                y=Indicator.bbmid(allCandlesPeriod['bidclose'], 20),
                name='Bid BBmid' + str(period),
                color="rgba(0, 0, 200, 0.5)",
                plot=2
            )

            Graph.addIndicator(
                x=allCandlesPeriod.index.to_pydatetime(),
                y=Indicator.bblow(allCandlesPeriod['bidclose'], 20),
                name='Bid BBlow' + str(period),
                color="rgba(0, 0, 180, 0.4)",
                plot=2
            )

            Graph.render()

        # print("DEBUG: Final Account Equity:", accountInfo['equity'])

        # # Buy Plot
        # Graph.addCandleSticks(
        #     x=allCandles.index.to_pydatetime(),
        #     open=allCandles['askopen'],
        #     high=allCandles['askhigh'],
        #     low=allCandles['asklow'],
        #     close=allCandles['askclose'],
        #     name='Ask Market Candles')

        # Graph.addIndicator(
        #     x=allCandles.index.to_pydatetime(),
        #     y=Indicator.ema(allCandles['askclose'], 20),
        #     name='EMA 20',
        #     color="rgba(0, 180, 0, 0.6)"
        # )

        # Graph.addIndicator(
        #     x=allCandles.index.to_pydatetime(),
        #     y=Indicator.ema(allCandles['askclose'], 100),
        #     name='EMA 100',
        #     color="rgba(0, 200, 0, 0.4)"
        # )

        # Graph.addIndicator(
        #     x=allCandles.index.to_pydatetime(),
        #     y=Indicator.bbup(allCandles['askclose'], 20),
        #     name='BBup',
        #     color="rgba(0, 0, 255, 0.6)"
        # )

        # Graph.addIndicator(
        #     x=allCandles.index.to_pydatetime(),
        #     y=Indicator.bbmid(allCandles['askclose'], 20),
        #     name='BBmid',
        #     color="rgba(0, 0, 200, 0.5)"
        # )

        # Graph.addIndicator(
        #     x=allCandles.index.to_pydatetime(),
        #     y=Indicator.bblow(allCandles['askclose'], 20),
        #     name='BBlow',
        #     color="rgba(0, 0, 180, 0.4)"
        # )

        # # Sell Plot
        # Graph.addCandleSticks(
        #     x=allCandles.index.to_pydatetime(),
        #     open=allCandles['bidopen'],
        #     high=allCandles['bidhigh'],
        #     low=allCandles['bidlow'],
        #     close=allCandles['bidclose'],
        #     name='Bid Market Candles',
        #     plot=2)

        # Graph.addIndicator(
        #     x=allCandles.index.to_pydatetime(),
        #     y=Indicator.ema(allCandles['bidclose'], 20),
        #     name='EMA 20',
        #     color="rgba(0, 180, 0, 0.6)",
        #     plot=2
        # )

        # Graph.addIndicator(
        #     x=allCandles.index.to_pydatetime(),
        #     y=Indicator.ema(allCandles['bidclose'], 100),
        #     name='EMA 100',
        #     color="rgba(0, 200, 0, 0.4)",
        #     plot=2
        # )

        # Graph.addIndicator(
        #     x=allCandles.index.to_pydatetime(),
        #     y=Indicator.bbup(allCandles['bidclose'], 20),
        #     name='BBup',
        #     color="rgba(0, 0, 255, 0.6)",
        #     plot=2
        # )

        # Graph.addIndicator(
        #     x=allCandles.index.to_pydatetime(),
        #     y=Indicator.bbmid(allCandles['bidclose'], 20),
        #     name='BBmid',
        #     color="rgba(0, 0, 200, 0.5)",
        #     plot=2
        # )

        # Graph.addIndicator(
        #     x=allCandles.index.to_pydatetime(),
        #     y=Indicator.bblow(allCandles['bidclose'], 20),
        #     name='BBlow',
        #     color="rgba(0, 0, 180, 0.4)",
        #     plot=2
        # )
        # Graph.render()
