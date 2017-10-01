import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.finance import candlestick_ohlc

import talib as ta

LIGHT_COLOR = '#00A3E0'
DARK_COLOR = '#183A54'

def plot_trade_strategy(df):    
    
    df['MPLDate'] = df['Datestamp'].apply(lambda date: mdates.date2num(date.to_pydatetime()))
    
    plt.figure(figsize=(15,8))
    last_price = round(float(df['Close'].as_matrix()[-1]),2)
    last_time_stamp = list(df['Datestamp'])[-1]
    # Add buys and Sells to the plot
    buys = df[df['Buy_Sell']==1][['Datestamp','Close']]
    sells = df[df['Buy_Sell']==-1][['Datestamp','Close']]
    Trade_num =  buys['Close'].shape[0] + sells['Close'].shape[0]
    last_value = round(float(df['Account_Value'].as_matrix()[-1]),2)
    
    a = plt.subplot2grid((16,10), (0,0), rowspan=8, colspan=10)
    a2 = plt.subplot2grid((16,10), (8,0), rowspan=3, colspan=10, sharex=a)
    a3 = plt.subplot2grid((16,10), (12,0), rowspan=4, colspan=10, sharex=a)
    
    a.plot_date(df['Datestamp'], df['Close'], LIGHT_COLOR, label='BTC Price')
    a.plot_date(buys['Datestamp'],buys['Close'], color='green', fmt='X', markersize=4, label='Buys')
    a.plot_date(sells['Datestamp'],sells['Close'], color='red', fmt='X' , markersize=4, label='Sells')    
    a.xaxis.set_major_locator(mticker.MaxNLocator(5))
    a.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    plt.setp(a.get_xticklabels(), visible=False)    
    title = "BTC/USD Prices\nLast Price: $"+str(last_price)+" ("+str(last_time_stamp)+")"
    a.set_title(title)
    a.set_ylabel('USD/BTC')    
    a.legend(loc=4, ncol=3)
    
    a2.fill_between(df['MPLDate'], 0, df['Volume_(BTC)'], facecolor=DARK_COLOR)
    a2.set_ylabel('Volume(BTC)')
        
    min_value = min(df['Close'].min(), df['Account_Value'].min())
    a3.fill_between(df['MPLDate'], min_value*0.9, df['Account_Value'], facecolor='blue', label='Active Account', alpha=0.5) 
    a3.fill_between(df['MPLDate'], min_value*0.9, df['Close'], facecolor='red', label='Passive Account', alpha=0.5)  
    a3.legend(loc=4, ncol=2)           
    a3.set_ylabel('Accout Value[$]')
    title = 'Number of trades: '+str(Trade_num)+', Account value: $'+str(last_value)
    a3.set_title(title, position=(0.5,0.7))    
    

#%%
def buy_sell_overlay(a, df, resample_size='1Min'):
    buys = df[df['Buy_Sell']==1][['Datestamp','Close']]
    sells = df[df['Buy_Sell']==-1][['Datestamp','Close']]
    buys = buys.resample(resample_size).apply({'Close':'mean'}).dropna()
    sells = sells.resample(resample_size).apply({'Close':'mean'}).dropna()
    a.plot_date(buys.index,buys['Close'], color='green', fmt='X', markersize=6.5, label='Buys')
    a.plot_date(sells.index,sells['Close'], color='red', fmt='X' , markersize=6.5, label='Sells')    
    return

def SMA_overlay(a, df, resample_size='1Min', timeperiod=14):
    SMA = ta.SMA(np.asarray(df['Close']), timeperiod=timeperiod)
    SMA = pd.DataFrame(SMA)
    SMA.index = df.index
    SMA.columns=['SMA']
    SMA = SMA.resample(resample_size).apply('mean').dropna()
    label = 'SMA'+str(timeperiod)
    a.plot_date(SMA.index, SMA['SMA'],fmt='-', label=label)

def EMA_overlay(a, df, resample_size='1Min', timeperiod=14):
    EMA = ta.EMA(np.asarray(df['Close']), timeperiod=timeperiod)
    EMA = pd.DataFrame(EMA)
    EMA.index = df.index
    EMA.columns=['EMA']
    EMA = EMA.resample(resample_size).apply('mean').dropna()
    label = 'EMA'+str(timeperiod)
    a.plot_date(EMA.index, EMA['EMA'],fmt='-', label=label)

def BBands_overlay(a, df, resample_size='1Min', timeperiod=20, nbdev=2):
    upper, middle, lower = ta.BBANDS(np.asarray(df['Close']),
                                     timeperiod=timeperiod, nbdevup=nbdev, nbdevdn=nbdev, matype=0)
    BBands = pd.DataFrame()
    BBands['Upper'] = upper
    BBands['Middle'] = middle
    BBands['Lower'] = lower
    BBands.index = df.index
    BBands = BBands.resample(resample_size).apply('mean').dropna()
    label = 'Bollinger Bands ('+str(timeperiod)+','+str(nbdev) +') High'
    a.plot_date(BBands.index, BBands['Upper'],fmt='--', label=label, linewidth=0.7)
    label = 'Bollinger Bands ('+str(timeperiod)+','+str(nbdev) +') Low'
    a.plot_date(BBands.index, BBands['Lower'],fmt='--', label=label, linewidth=0.7)    

def plot_OHLC(df, resample_size='10Min', overlays=[buy_sell_overlay,(SMA_overlay,14)]):
    '''
    Inputs:
        df - Pandas Dataframe that contains OHLC data with the following columns:
            'Open', 'High', 'Low', 'Close' and 'Volume_(BTC)'. 
            additional 'DateStamp' column in datetime64[s] is needed as well.
        resample_size - the OHLC can be resampled to different candle bar resolution.
                        minimum is '1Min'.
        Overlays - a list that contains either single item tupple with a supported overlay function
                    or a tupple with 2 items: function name and needed params.
    
    Output:
        plots a figure that contains
    '''
    plt.figure(figsize=(14,8))
    a = plt.subplot2grid((14,8), (0,0), rowspan=12, colspan=8)
    a2 = plt.subplot2grid((14,8), (12,0), rowspan=2, colspan=8, sharex=a)
    width_dict = {'1Min':0.0005, '3Min':0.0015, '5Min':0.003, '10Min':0.006, 
                  '15Min':0.008, '30Min':0.016, '1Hr':0.032}
    candle_width = width_dict.get(resample_size,0.005)
    df = df.set_index('Datestamp')
    df['Datestamp'] = df.index
    ohlc_dict = {'Open':'first', 'High':'max', 'Low':'min', 'Close': 'last'}
    OHLC = df.resample(resample_size).apply(ohlc_dict).dropna()
    OHLC['dateCopy'] = OHLC.index
    OHLC['MPLDates'] = OHLC['dateCopy'].apply(lambda date: mdates.date2num(date.to_pydatetime()))
    del OHLC['dateCopy']
    volume_data = df['Volume_(BTC)'].resample(resample_size).apply({'volume':'sum'}).dropna()
    # plot function imported from matplotlib.finance
    candlestick_ohlc(a,OHLC[['MPLDates', 'Open', 'High', 'Low', 'Close']].values,width=candle_width, 
                     colorup=LIGHT_COLOR, colordown=DARK_COLOR)
    
    # Plot the overlay functions
    for overlay in overlays:
        if len(overlay) == 1:
            overlay[0](a, df, resample_size)
        elif len(overlay) == 2:
            overlay[0](a, df, resample_size, overlay[1])
        elif len(overlay) == 3:
            overlay[0](a, df, resample_size, overlay[1], overlay[2])
        # TODO: this tripple 'if' statement is nasty, need to create a cleaner method
    
    a.set_ylabel('price')
    a.xaxis.set_major_locator(mticker.MaxNLocator(3))
    a.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
    a.legend(loc=4)
    last_price = round(float(df['Close'].as_matrix()[-1]),2)
    last_time_stamp = list(df['Datestamp'])[-1]
    title = "BTC/USD Prices (OHLC) "+resample_size+" bars\nLast Price: $"+str(last_price)+" ("+str(last_time_stamp)+")"
    a.set_title(title)
    a.set_ylabel('USD/BTC')
    plt.setp(a.get_xticklabels(), visible=False)
    
    a2.fill_between(OHLC.index, 0, volume_data['volume'], facecolor='blue')
    a2.set_ylabel('volume(BTC)')
        
