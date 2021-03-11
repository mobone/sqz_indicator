import pandas as pd
import yfinance
from sklearn import linear_model
import talib as ta
import statistics as stat
import numpy as np

class stock():
    def __init__(self, symbol):
        self.symbol = symbol

        self.length = 20
        self.mult = 2.0
        self.lengthKC = 20
        self.multKC = 1.5

        self.get_data()
        self.get_BB()
        self.get_KC()
        self.get_SQZ()

    def get_data(self):
        self.df = yfinance.Ticker(self.symbol).history(period='2y')

    def get_BB(self):
        source = self.df['Close']
        basis = ta.SMA(source, self.length)
        dev = self.multKC * stat.stdev(source, self.length)
        self.df['upperBB'] = basis + dev
        self.df['lowerBB'] = basis - dev

    def get_KC(self):
        source = self.df['Close']
        self.ma = ta.SMA(source, self.lengthKC)
        trueRange = abs(self.df['High']-self.df['Low'])

        rangema = ta.SMA(trueRange, self.lengthKC)
        self.df['upperKC'] = self.ma + rangema * self.multKC
        self.df['lowerKC'] = self.ma - rangema * self.multKC


    def get_SQZ(self):
        cur_coef = None
        result_list = []
        coef_list = []

        df = self.df
        sqzOn = df[ (df['lowerBB']>df['lowerKC']) & (df['upperBB']<df['upperKC']) ]
        sqzOff = df[ (df['lowerBB']<df['lowerKC']) & (df['upperBB']>df['upperKC']) ]
        noSqz = (sqzOn == False) & (sqzOff == False)
        print(sqzOn)
        input()
        regr = linear_model.LinearRegression()

        self.df = self.df.reset_index()
        for index in self.df.index:
            if len(self.df.iloc[index:index+self.lengthKC])!=self.lengthKC:
                print('pass')
                continue

            highest_high = self.df.iloc[index:index+self.lengthKC]['High'].max()
            lowest_low = self.df.iloc[index:index+self.lengthKC]['Low'].min()
            inner_mean = stat.mean([highest_high, lowest_low])

            outter_mean = stat.mean([inner_mean] + list(ta.SMA(self.df['Close'], self.lengthKC).values)[index:index+self.lengthKC])


            x = np.arange(self.lengthKC, dtype=float).reshape((self.lengthKC, 1))
            y = self.df.iloc[index:index+self.lengthKC]['Close'] - outter_mean
            y = y.dropna()

            if len(y)<self.lengthKC:
                continue
            regr.fit(x,y)


            prev_coef = cur_coef

            cur_coef = regr.coef_[0]

            if prev_coef is None:
                continue

            coef_list.append(prev_coef)
            if (cur_coef>0):
                if cur_coef>prev_coef:
                    result_list.append('lime')
                else:
                    result_list.append('green')
            else:
                if cur_coef<prev_coef:
                    result_list.append('red')
                else:
                    result_list.append('maroon')


        self.df = self.df[self.lengthKC:]
        self.df = self.df.iloc[len(self.df)-len(coef_list):]
        print(self.df)
        print(len(coef_list))
        self.df['COEF'] = coef_list
        self.df['SQZ'] = result_list
        print(self.df)
        self.df = self.df[['Date','Open', 'Close','Volume', 'COEF', 'SQZ']]
        print(self.df)
        self.df.to_csv('test.csv')

        """

        highest_high = self.df.iloc[:self.lengthKC]['High'].max()
        lowest_low = self.df.iloc[:self.lengthKC]['Low'].min()

        x_mean = stat.mean([highest_high, lowest_low])

        y_mean_list = []
        for y in self.ma:
            y_mean_list.append(stat.mean([x_mean, y]))

        self.df['lazy_bear_mean'] = self.df['Close'] - y_mean_list

        self.df = self.df.dropna(subset=['upperBB'])

        result_list = []
        coef_list = []
        cur_coef = None
        self.df = self.df.reset_index()
        for index in self.df.index:


            cur_linreg_data = self.df.iloc[index:index+self.lengthKC]['lazy_bear_mean'].values

            if len(cur_linreg_data)!=self.lengthKC:
                print('pass')
                continue

            x = np.arange(self.lengthKC, dtype=float).reshape((self.lengthKC, 1))
            y = cur_linreg_data.reshape(self.lengthKC, 1)
            regr.fit(x,y)
            prev_coef = cur_coef
            cur_coef = regr.coef_[0][0]


            if prev_coef is None:
                continue
            coef_list.append(prev_coef)
            if (cur_coef>0):
                if cur_coef>prev_coef:
                    result_list.append('lime')
                else:
                    result_list.append('green')
            else:
                if cur_coef<prev_coef:
                    result_list.append('red')
                else:
                    result_list.append('maroon')


        self.df = self.df[self.lengthKC:]
        print(self.df)
        print(len(coef_list))
        self.df['COEF'] = coef_list
        self.df['SQZ'] = result_list
        print(self.df)
        self.df = self.df[['Date','Open', 'Close','Volume', 'COEF', 'SQZ']]
        print(self.df)
        self.df.to_csv('test.csv')
        """


stock('QQQ')
