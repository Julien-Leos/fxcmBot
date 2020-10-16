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
        # Example algorithm which open a buy position if there is no opened position and close it otherwise
        if len(self.fxcm.getPositions()) == 0:
            self.positionId = self.fxcm.buy(1)
            print("Buy position %s" % self.positionId)

            # Try to close the position right after opening it (might not work each time because FXCM API needs 1-2 seconds to transform an order into a real open position)
            self.closePosition(self.positionId)
        else:
            self.closePosition(self.positionId)

    def closePosition(self, positionId):
        if self.fxcm.closePosition(positionId):
            print("Close position %s" % positionId)
        else:
            print("Position %s couldn't be closed" % positionId)
