from graph import Graph
from datetime import datetime
from time import sleep


class Algorithm():
    fxcm = None
    config = None

    positionId = None

    def __init__(self, fxcm, config):
        self.fxcm = fxcm
        self.config = config

    def nextTick(self, newCandle, allCandles):  # Tick
        if (len(allCandles) == 1):  # Is first Tick
            accountInfo = self.fxcm.getAccountInfo()
            print("DEBUG: Start Account Equity:", accountInfo['equity'])
        if newCandle.empty:  # Is last Tick
            accountInfo = self.fxcm.getAccountInfo()
            print("DEBUG: End Account Equity:", accountInfo['equity'])
            self.lastTick(allCandles)
            return

        if len(self.fxcm.getOpenPositions('list')) == 0:
            self.positionId = self.fxcm.buy(1, limit=2, stop=-10)
            print("Buy position %s" % self.positionId)
        elif self.positionId == None:
            # Close positions (only in) realtime where positions could be opened on the external service
            self.fxcm.closePositions()
            print("Close all positions")
            return

        # grossPL = self.fxcm.getOpenPosition(self.positionId).get_grossPL()
        # print("DEBUG: Position GrossPL:", grossPL)

    def lastTick(self, allCandles):
        self.fxcm.closePositions()

        # closedPositions = self.fxcm.getClosePositions('list')
        # print(closedPositions)

        accountInfo = self.fxcm.getAccountInfo()
        Graph.setTitle("Final Account Equity: {}".format(
            accountInfo['equity']))
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
