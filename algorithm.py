class Algorithm():

    MIN_CANDLES = 10
    STREAM_PERIOD = 3000  # In milliseconds

    candles = []

    def runNextInstance(self, newCandle, allCandles):
        print(newCandle) # nouvelle bougie
        print(allCandles) # historique des bougies depuis le subscribe

