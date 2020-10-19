import sys
from utils import *


class Algorithm():
    fxcm = None
    config = None

    positionId = None

    def __init__(self, fxcm, config):
        self.fxcm = fxcm
        self.config = config

    def runNextInstance(self, newCandle, allCandles):
        # Example algorithm which:
        # - Open a buy position if there is no opened position
        # - Try to close it imediatly but failed most of the time (see below why)
        # - Close the position if at least one in opened

        accountInfo = self.fxcm.getAccountInfo()
        print("DEBUG: Account Equity:", accountInfo['equity'])

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
            self.fxcm.closePositions()
