import pandas as pd
import pandas_ta as ta
import numpy as np
import yfinance as yf
from multiprocessing import Pool
import requests as r
import requests_cache

requests_cache.install_cache('request_cache')

s = r.Session()


mega = 200000000000
large = 10000000000
mid = 2000000000
small = 300000000

class stock:
    def __init__(self, ticker):
        self.ticker = ticker.replace('.', '-')

        self.get_data()
        self.get_market_cap()
        self.get_ta()
        self.get_trades()

        self.trades = pd.DataFrame(self.trades, columns = ['Symbol', 'Start Date', 'End Date', 'Buy Price', 'Sell Price', 'Change'])

        self.trades['Market Cap'] = self.market_cap
        #print(self.trades)


    def get_data(self):
        self.df = yf.Ticker(self.ticker).history('5y')

        if self.df.empty:
            raise Exception("History df is empty")


    def get_market_cap(self):
        response = r.get('https://finance.yahoo.com/quote/'+self.ticker)
        cap_df = pd.read_html(response.text)
        self.market_cap = cap_df[1][1].loc[0]
        #print(self.market_cap)
        if 'T' in self.market_cap:
            self.market_cap = float(self.market_cap[:-1])*1000000000000
        elif 'B' in self.market_cap:
            self.market_cap = float(self.market_cap[:-1])*1000000000
        elif 'M' in self.market_cap:
            self.market_cap = float(self.market_cap[:-1])*1000000
        elif 'K' in self.market_cap:
            self.market_cap = float(self.market_cap[:-1])*1000

        if self.market_cap>mega:
            self.market_cap = 'Mega'
        elif self.market_cap>large and self.market_cap<mega:
            self.market_cap = 'Large'
        elif self.market_cap<large and self.market_cap>mid:
            self.market_cap = 'Mid'
        elif self.market_cap<mid and self.market_cap>small:
            self.market_cap = 'Small'
        else:
            self.market_cap = 'Micro'

        #print(self.market_cap)


    def get_ta(self):
        sqz_df = self.df.ta.squeeze(use_tr=True,mamode='ema', lazybear=True,detailed=True)

        self.df = pd.concat([self.df, sqz_df],axis=1)


    def get_trades(self):
        cur_pos = None
        self.trades = []
        start_trading = False
        for key, row in self.df.iterrows():
            if start_trading == False and row['SQZ_ON'] == 1:
                start_trading = True

            if start_trading == False:
                continue

            cur_price = row['close']
            if cur_pos is None and row['SQZ_ON'] == 0:
                # buy
                cur_pos = {'buy_date': key, 'buy_price': cur_price}

            if cur_pos is not None and row['SQZ_ON'] == 1:
                # sell
                cur_pos['sell_date'] = key
                cur_pos['sell_price'] = cur_price
                percent_change = (cur_pos['sell_price'] - cur_pos['buy_price']) / cur_pos['buy_price']
                self.trades.append([self.ticker, cur_pos['buy_date'], cur_pos['sell_date'], cur_pos['buy_price'], cur_pos['sell_price'], percent_change])
                cur_pos = None



def stock_wrapper(ticker):
    try:
        stock_class = stock(ticker)
    except Exception as e:
        print(ticker, '\t', e)
        return None
    #print(stock_class.trades)
    print(ticker)
    return stock_class.trades

if __name__ == '__main__':
    companies = pd.read_csv('companies.csv')
    tickers = list(companies['Symbol'].values)
    with Pool(16) as p:
        trades = p.map(stock_wrapper, tickers)

    all_trades = pd.concat(trades)
    all_trades.to_csv('all_trades.csv')
