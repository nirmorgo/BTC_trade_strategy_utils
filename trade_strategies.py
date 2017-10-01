import numpy as np
import talib as ta

def generic_strategy_template(df, start=1, commision=0.0025, *args):
    '''
    can use this as a template to create a strategy.
    Inputs:
        df - a Pandas dataframe that contains trade history. with a 'Close' 
             columns that contains the closing price of each sample bar at each sample.             
        start - the number of bitcoins in account at the begining of strategy simulation (double)
        commision - the price paid for each Buy/Sell transaction (double)
        *args - other parameters needed for the current strategy
    
    Outputs:
        df will be updated with following columns:
            Buys_Sells: -1 for BTC sell, 1 for BTC purchase, 0 for no action.
            Account_value: keep track of current account value, starting with the
                           starting with the number of BTCs set with 'start' parameter.
    '''
    buys_sells = [0]*df.shape[0]
    account_value = [0]*df.shape[0]
    currency = 'BTC'
    prices = df['Close'].values
    current_BTC = start
    current_USD = 0
    
    ### Additional code for df preprocess can go here ###
    
    for idx, row in df.iterrows():
        if currency == 'BTC':
            # Should add additional code for sell condition
            if sell_condition:
                # Sell Bitcoins action
                buys_sells[idx] = -1
                currency = 'USD'
                current_USD = current_BTC * (1 - commision) * prices[idx]
                current_BTC = 0
        
        elif currency == 'USD':
            # Should add additional code for buy condition
            if buy_condition:
            # Buy Bitcoins action
                buys_sells[idx] = 1
                currency = 'BTC'
                current_BTC = current_USD * (1 - commision) / prices[idx]
                current_USD = 0
        
        # update account value in USD
        account_value[idx] = current_BTC * prices[idx] + current_USD           
    # Update last value of the list 
    account_value[-1] = current_BTC * prices[-1] + current_USD
            
    df['Buy_Sell'] = buys_sells
    df['Account_Value'] = account_value
    print('Current holdings: ',account_value[-1],'USDs')
    return df


def hindsight_trade_strategy(df, start=1, commision=0.0025, sensitivity=0.8):
    '''
    A trade strategy that makes decisions based on previously known future outcomes.
    This is obviously not a real trade stragtegy, but a tool that can create the
    "Perfect Baseline", so other trades strategies can be compared to.
    Inputs:
        df - a dataframe that contains trade history. with a 'Close' columns that 
             contains the closing price of each sample
             at each sample.             
        start - the number of bitcoins in account at the begining of strategy simulation (double)
        commision - the price paid for each Buy/Sell transaction (double)
        sensitivity - [0:1] will determines the sensitivity to small price changes
    Outputs:
        df will be updated with following columns:
            Buys_Sells: -1 for BTC sell, 1 for BTC purchase, 0 for no action.
            Account_value: keep track of current account value, starting with the
                           starting with the number of BTCs set with 'start' parameter.
    '''
    
    buys_sells = [0]*df.shape[0]
    account_value = [0]*df.shape[0]
    currency = 'BTC'
    prices = df['Close'].values
    current_BTC = start
    current_USD = 0
    
    for current_idx, current_price in enumerate(prices[:-1]):        
        if currency == 'BTC':
        # If the currency is now in BTC, we want to keep as long as the rate goes up 
        # and sell the moment it starts to fall
            for future_price in prices[current_idx+1:]:
                if future_price >= current_price:
                    break
                # Calculate BTC sell commision and potential buyback commision
                sell_comm = current_BTC * current_price * commision
                new_value = current_BTC * current_price - sell_comm    
                # if BTCs are sold, this would be the value in USD after commision
                buy_back_comm = new_value * commision
                
                if current_BTC * (current_price - future_price) > (sell_comm + buy_back_comm) / sensitivity:
                    buys_sells[current_idx] = -1
                    currency = 'USD'
                    current_USD = current_BTC * (1 - commision) * current_price
                    current_BTC = 0
                    break
                else:
                    # if the price dropped, but not enough to cover commision
                    # we continue to see next future price
                    continue
        elif currency == 'USD':
        # If the currency is now in BTC, we want to keep as long as the rate goes down 
        # and sell the moment it starts to rise
             for future_idx, future_price in enumerate(prices[current_idx+1:]):
                if future_price <= current_price:
                    break
                # Calculate BTC buy commision and potential sellback commision
                buy_comm = current_USD * commision
                # if BTCs are bought, this would be the value in BTC after commision
                new_value = (1 - commision) * current_USD / current_price 
                sell_back_comm = new_value * commision * future_price
                
                if new_value * (future_price - current_price) > (buy_comm + sell_back_comm) / sensitivity:
                    buys_sells[current_idx] = 1
                    currency = 'BTC'
                    current_BTC = current_USD * (1 - commision) / current_price
                    current_USD = 0
                    break
                else:
                    # if the price dropped, but not enough to cover commision
                    # we continue to see next future price
                    continue
                 # Keep track of current acount_value
        
        account_value[current_idx] = current_BTC * current_price + current_USD           
    # Update last value of the list
    account_value[-1] = current_BTC * current_price + current_USD
            
    df['Buy_Sell'] = buys_sells
    df['Account_Value'] = account_value
    print('Current holdings: ',account_value[-1],'USDs')
    return df
#%%
def RSI_strategy(df, start=1, commision=0.0025, timeperiod=14, low_TH=30, high_TH=70):
    '''
    decide on buying/selling according to RSI score
    '''
    buys_sells = [0]*df.shape[0]
    account_value = [0]*df.shape[0]
    currency = 'BTC'
    prices = df['Close'].values
    current_BTC = start
    current_USD = 0
    df['RSI'] = ta.RSI(np.asarray(df['Close']), timeperiod=timeperiod)
    # We buy if RSI index is bellow low_TH and sell if it is above high_TH
    for idx, row in df.iterrows():
        if currency == 'BTC' and row['RSI'] > high_TH:
            buys_sells[idx] = -1
            currency = 'USD'
            current_USD = current_BTC * (1 - commision) * prices[idx]
            current_BTC = 0
        
        elif currency == 'USD' and row['RSI'] < low_TH:
            buys_sells[idx] = 1
            currency = 'BTC'
            current_BTC = current_USD * (1 - commision) / prices[idx]
            current_USD = 0
        
        account_value[idx] = current_BTC * prices[idx] + current_USD           
    # Update last value of the list
    account_value[-1] = current_BTC * prices[-1] + current_USD
            
    df['Buy_Sell'] = buys_sells
    df['Account_Value'] = account_value
    print('Current holdings: ',account_value[-1],'USDs')
    return df
#%%
    
    
    
