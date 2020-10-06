class Algorithm():
    fxcm = None
    config = None

    def __init__(self, fxcm, config):
        self.fxcm = fxcm
        self.config = config

    def runNextInstance(self, newCandle, allCandles):
        print(newCandle)
        # print(allCandles)
        self.fxcm.buy(1)
