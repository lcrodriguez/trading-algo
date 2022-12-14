import backtrader.feeds as btfeeds
import yfinance as yf
import backtrader as bt
import datetime

class BuyAndHold_Buy(bt.Strategy):
    
    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.data.datetime[0]
        if isinstance(dt, float):
            dt = bt.num2date(dt)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            self.log('ORDER ACCEPTED/SUBMITTED', dt=order.created.dt)
            self.order = order
            return

        if order.status in [order.Expired]:
            self.log('BUY EXPIRED')

        elif order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

        # Sentinel to None: new orders allowed
        self.order = None

    def start(self):
        # set the starting cash
        self.val_start = self.broker.get_cash() 

    def nextstart(self):
        # Buy stocks with all the available cash
        size = int(self.val_start / self.data.close[0])
        print('Size: %s' % (size))

        self.buy(size=size)

    def stop(self):
        # calculate the actual returns
        self.roi = (self.broker.get_value() / self.val_start) - 1.0
        print("ROI: %.2f, Market Value: %.2f, Cash: %.2f" % (100.0 * self.roi, self.broker.get_value(), self.broker.get_cash()))

# Se compra cuando la 21D hace CROSSOVER con la 100D por encima de la 200W
# Se vende cuando la 21 hace crossover con la 200 W
# Every month we will add u$s 1000 to the account
ticker_name = "SPY"
print('Ticker Name: %s' % (ticker_name))

cerebro = bt.Cerebro()
data = bt.feeds.PandasData(dataname=yf.download(ticker_name, '2015-07-06', '2021-07-01', auto_adjust=True))
cerebro.addstrategy(BuyAndHold_Buy, "HODL")
cerebro.broker.set_cash(10000)
cerebro.adddata(data)
cerebro.run()

cerebro.plot()
