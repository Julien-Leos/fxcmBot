class Algorithm():

    MIN_CANDLES = 10
    STREAM_PERIOD = 2000 #In milliseconds

    candles = []

    def runNextInstance(self, newCandle):
        candles.append(newCandle)
        print(candles)

    def displayCandles(data, dataframe):
        print('%3d | %s | %s, %s, %s, %s, %s'
              % (len(dataframe), data['Symbol'],
                 pd.to_datetime(int(data['Updated']), unit='ms'),
                 data['Rates'][0], data['Rates'][1], data['Rates'][2],
                 data['Rates'][3]))
