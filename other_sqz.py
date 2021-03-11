import pandas as pd
import yfinance as yf
import pandas_ta as ta
import numpy as np
mega = 200000000000
large = 10000000000
mid = 2000000000
small = 300000000
companies = pd.read_csv("companies.csv")
all_trades = []
all_trades_summary = []

for ticker, row in companies.iterrows():

    ticker = row['Symbol']
    cap = row['Market Cap']

    if cap>mega:
        cap = 'mega'
    elif cap>large and cap<mega:
        cap = 'large'
    elif cap<large and cap>mid:
        cap = 'mid'
    elif cap<mid and cap>small:
        cap = 'small'
    else:
        cap = 'micro'

    df = yf.Ticker(ticker).history(period='5y')
    if df.empty:
        continue

    #df.ta.squeeze(use_tr=True,lazybear=True)
    try:
        sqz_df = df.ta.squeeze(use_tr=True,mamode='ema', lazybear=True,detailed=True)
    except:
        continue

    df = pd.concat([df, sqz_df],axis=1)


    cur_pos = None
    trades = []
    buy_trigger = True
    for key, row in df.iterrows():
        #if cur_pos is None and buy_trigger == False and row['SQZ_ON'] == 1:
        #    buy_trigger = True
        if cur_pos is None and row['SQZ_ON'] == 0: # and buy_trigger == True:
            # buy
            cur_pos = [key, row['close']]

        if cur_pos is not None and row['SQZ_ON'] == 1:
            # sell
            percent_change = (row['close'] - cur_pos[1]) / cur_pos[1]
            trades.append([ticker, cur_pos[0], key, percent_change])
            cur_pos = None
        '''
        if cur_pos is not None and row['SQZ_PDEC']>0:
            sqz_on_found = False
            # sell
            percent_change = (row['close'] - cur_pos[1]) / cur_pos[1]
            trades.append([cur_pos[0], key, percent_change])
            cur_pos = None
            buy_trigger = False
        '''


    output_df = pd.DataFrame(trades, columns = ['Symbol', 'Start Date', 'End Date', 'Change'])
    if output_df.empty:
        continue

    all_trades.append(output_df)
    num_trades = len(output_df)
    mean = output_df['Change'].mean()
    success = len(output_df[output_df['Change']>0])/len(output_df)
    all_trades_summary.append([ticker, cap, num_trades, success, mean])

    output_df = pd.DataFrame(all_trades_summary, columns = ['Ticker', 'Market Cap', 'Num Trades', 'Success Rate', 'Avg Return'])
    print(output_df)
    print('Success Rate: {0:.2f}%\t Average Return: {1:.2f}%'.format(output_df['Success Rate'].mean()*100, output_df['Avg Return'].mean()*100))
output_df.to_csv('lazybear_results.csv')
all_trades = pd.concat(all_trades)
all_trades.to_csv('trades.csv')
