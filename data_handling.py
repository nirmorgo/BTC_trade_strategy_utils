import pandas as pd
import numpy as np
import urllib
import json

#%%

def get_OHLC_data_from_file(directory_path, file_name):
    data = pd.read_csv(directory_path+'/'+file_name)    
    data.dropna(inplace=True)
    data.reset_index(inplace=True)
    data=data.drop('index', axis=1)
    data['Datestamp'] = np.array(data['Timestamp'].apply(int)).astype('datetime64[s]')
    data['Buy_Sell'] = 0
    data['Account_Value'] = data['Close']
    
    print ('Data loaded from file.', data.shape[0],'sampels.')
    return data

#%%

def get_latest_Bitstamp_ticks():
    datalink = 'https://www.bitstamp.net/api/transactions/'
    data = urllib.request.urlopen(datalink)
    data = data.read().decode("utf-8")
    data = json.loads(data)
    data = pd.DataFrame(data)
    data['price'] = data['price'].apply(float)
    data['amount'] = data['amount'].apply(float)
    data['Datestamp'] = np.array(data['date'].apply(int)).astype('datetime64[s]') 
    
    return data
    
#%%

def get_tick_data_from_file(directory_path, file_name):
    data = pd.read_csv(directory_path+'/'+file_name)
    data['price'] = data['price'].apply(float)
    data['amount'] = data['amount'].apply(float)
    data['Datestamp'] = np.array(data['date'].apply(int)).astype('datetime64[s]') 
    
    return data

#%%
def convert_tick_to_OHLC(df, resample_size='1Min'):
    df.dropna(inplace=True)
    df = df.set_index('Datestamp')
    ohlc_dict = {'Open':'first', 'High':'max', 'Low':'min', 'Close': 'last'}
    OHLC = df['price'].resample(resample_size).apply(ohlc_dict).dropna()
    volumeData = df['amount'].resample(resample_size).apply({'Volume':'sum'}).dropna()
    OHLC['Volume_(BTC)'] = volumeData
    OHLC['Buy_Sell'] = 0
    OHLC['Account_Value'] = OHLC['Close']    
    OHLC.reset_index(inplace=True)
    
    return OHLC
    
    
#%%
def save_OHLC_to_file(df,directory_path, file_name):    

    path=directory_path+'/'+file_name
    df['Timestamp'] = df['Datestamp'].values.astype(np.int64) // 10 ** 9
    df = df.set_index('Timestamp')
    df.to_csv(path)
      
