import sys
from graph import Graph
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from collections import namedtuple
import numpy as np


class Algorithm():
    fxcm = None
    config = None

    positionId = None

    def __init__(self, fxcm, config):
        self.fxcm = fxcm
        self.config = config

    def isLastTick(self, date):
        endDate = datetime.strptime(self.config['end_date'], '%Y/%m/%d %H:%M')
        currentDate = date.to_pydatetime()
        return currentDate == endDate

    def runNextInstance(self, newCandle, allCandles):  # Tick
        # Example algorithm which:
        # - Open a buy position if there is no opened position
        # - Try to close it imediatly but failed most of the time (see below why)
        # - Close the position if at least one in opened

        if (len(allCandles) == 1):  # Is first Tick
            accountInfo = self.fxcm.getAccountInfo()
            print("DEBUG: Start Account Equity:", accountInfo['equity'])
        if (self.isLastTick(newCandle.name)):  # Is last Tick
            self.lastTick(newCandle, allCandles)
            return

        if len(self.fxcm.getPositions('list')) == 0:
            self.positionId = self.fxcm.buy(1)
            print("Buy position %s" % self.positionId)
        elif self.positionId != None:
            position = self.fxcm.getPosition(self.positionId)
            if position:
                grossPL = position.get_grossPL()
                print("DEBUG: Position GrossPL:", grossPL)
                if grossPL > 0.15:
                    if self.fxcm.closePosition(self.positionId):
                        print("Close position %s" % self.positionId)
        else:
            # Close positions (only in) realtime where positions could be opened on the external service
            self.fxcm.closePositions()

    def lastTick(self, newCandle, allCandles):
        position = self.fxcm.getPosition(self.positionId)
        if position and self.fxcm.closePosition(self.positionId):
            print("Close position %s" % self.positionId)

        accountInfo = self.fxcm.getAccountInfo()
        Graph.setTitle("Final Account Equity: {}".format(accountInfo['equity']))
        print("DEBUG: Final Account Equity:", accountInfo['equity'])

        Graph.addCandleSticks(
            x=allCandles.index.to_pydatetime(),
            open=allCandles['askopen'],
            high=allCandles['askhigh'],
            low=allCandles['asklow'],
            close=allCandles['askclose'],
            name='Market Candles')

        # Graph.addIndicator(
        #     x=allCandles.index.to_pydatetime(),
        #     y=allCandles['askhigh'],
        #     name='Example Indicator',
        #     color="#0000ff"
        # )

        Graph.render()
