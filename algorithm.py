from tools.graph import Graph
from tools.indicator import Indicator
from datetime import datetime
from time import sleep
import pandas as pd


class Algorithm():
    fxcm = None
    config = None

    def __init__(self, fxcm, config):
        self.fxcm = fxcm
        self.config = config

    def nextTick(self, newCandle, allCandles):
        if self.isFirstTick(allCandles):
            self.firstTick(newCandle, allCandles)
        elif self.isLastTick(newCandle):
            self.lastTick(newCandle, allCandles)
            return
        self.tick(newCandle, allCandles)

    def isFirstTick(self, allCandles):
        if len(allCandles) == 1:
            return True
        return False

    def firstTick(self, newCandle, allCandles):
        self.start(newCandle, allCandles)

    def isLastTick(self, newCandle):
        if newCandle.empty:
            return True
        return False

    def lastTick(self, lastCandle, allCandles):
        self.fxcm.closePositions()
        self.end(lastCandle, allCandles)

        Graph.addCandleSticks(
            x=allCandles.index.to_pydatetime(),
            open=allCandles['askopen'],
            high=allCandles['askhigh'],
            low=allCandles['asklow'],
            close=allCandles['askclose'],
            name='Ask Candles ')

        Graph.addCandleSticks(
            x=allCandles.index.to_pydatetime(),
            open=allCandles['bidopen'],
            high=allCandles['bidhigh'],
            low=allCandles['bidlow'],
            close=allCandles['bidclose'],
            name='Bid Candles ',
            plot=2)
        Graph.render()

    def start(self, firstCandle, allCandles):
        raise NotImplementedError(
            "Your algorithm should implement a start function.")

    def tick(self, newCandle, allCandles):
        raise NotImplementedError(
            "Your algorithm should implement a tick function.")

    def end(self, lastCandle, allCandles):
        raise NotImplementedError(
            "Your algorithm should implement an end function.")
