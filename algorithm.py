class Algorithm():
    fxcm = None
    config = None

    def __init__(self, fxcm, config):
        self.fxcm = fxcm
        self.config = config

    def runNextInstance(self, newCandle, allCandles):
        # print(newCandle)
        # print(allCandles)
        if len(self.fxcm.orders) == 0:
            self.fxcm.buy(1)
        print(self.fxcm.getLastCandle().name, self.fxcm.orders[0]['close'], round(self.fxcm.orders[0]['grossPL'], 3))
