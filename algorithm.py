class Algorithm():
    fxcm = None
    config = None

    def __init__(self, fxcm, config):
        self.fxcm = fxcm
        self.config = config

    def runNextInstance(self, newCandle, allCandles):
        # print(newCandle)
        # print(allCandles)
        if len(self.fxcm.con.get_orders(kind="list")) == 0:
            order = self.fxcm.buy(1)
            print(order)
            self.fxcm.unsubscribeMarket()
