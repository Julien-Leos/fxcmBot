from algorithm import Algorithm
from tools.graph import Graph
from tools.indicator import Indicator


class DoubleEMA(Algorithm):
    """
    Exponential Moving Average Strategy
    Capture the trend, using two EMAs(Periods of 20 & 50)
    1. Detect EMAs crossover.
    2. Detect prices to be higher than both EMAs. (pricetest)
    3. Wait until the price is tested atleast twice (2st step).
    4. Buy at market price if price is tested for a third time (2st step).
    5. Place a stop loss on 20 pips bellow current EMA(50)
    6. Place a take profits limit at... TODO
    """

    # Ask
    lastEmaShort = 0
    lastEmaLong = 0
    # Bid
    lastBidEmaShort = 0
    lastBidEmaLong = 0

    def start(self, firstCandle, allCandles):
        print("First Tick")

    def tick(self, newCandle, allCandles):
        if (len(allCandles) < 50):
            return
        self.detectCrossOverWindows(newCandle, allCandles)

    def end(self, lastCandle, allCandles):
        print("Last tick")

        accountInfo = self.fxcm.getAccountInfo()
        Graph.setTitle(
            "Final Account Equity: {} / Strategy: DoubleEMA".format(accountInfo['equity']))

        Graph.addIndicator(
            x=allCandles.index.to_pydatetime(),
            y=Indicator.ema(allCandles['askclose'], 20),
            name='EMA 20',
            color="rgba(0, 255, 0, 0.6)"
        )

        Graph.addIndicator(
            x=allCandles.index.to_pydatetime(),
            y=Indicator.ema(allCandles['askclose'], 50),
            name='EMA 50',
            color="rgba(0, 0, 255, 0.6)"
        )

        Graph.addIndicator(
            x=allCandles.index.to_pydatetime(),
            y=Indicator.ema(allCandles['bidclose'], 20),
            name='EMA 20',
            color="rgba(0, 255, 0, 0.6)",
            plot=2
        )

        Graph.addIndicator(
            x=allCandles.index.to_pydatetime(),
            y=Indicator.ema(allCandles['bidclose'], 50),
            name='EMA 50',
            color="rgba(0, 0, 255, 0.6)",
            plot=2
        )

    def detectCrossOverWindows(self, lastCandle, allCandles):
        emaShort = Indicator.ema(allCandles['askclose'], 20)[-1]
        emaLong = Indicator.ema(allCandles['askclose'], 50)[-1]
        emaBidShort = Indicator.ema(allCandles['bidclose'], 20)[-1]
        emaBidLong = Indicator.ema(allCandles['bidclose'], 50)[-1]
        if (self.lastEmaLong == 0 or self.lastBidEmaLong == 0):
            self.lastEmaShort = emaShort
            self.lastEmaLong = emaLong
            self.lastBidEmaShort = emaBidShort
            self.lastBidEmaLong = emaBidLong
            return
        crossedUp = (self.lastEmaShort <
                     self.lastEmaLong and emaShort > emaLong)
        crossedDown = (self.lastBidEmaShort >
                       self.lastBidEmaLong and emaBidShort < emaBidLong)
        if (crossedUp):
            Graph.addAction(
                lastCandle.name,
                emaShort,
                0,
                'Crossed UP',
                None, 1)
        if (crossedDown):
            Graph.addAction(
                lastCandle.name,
                emaBidShort,
                0,
                'Crossed Down',
                None, 2)
        self.lastEmaShort = emaShort
        self.lastEmaLong = emaLong
        self.lastBidEmaShort = emaBidShort
        self.lastBidEmaLong = emaBidLong
