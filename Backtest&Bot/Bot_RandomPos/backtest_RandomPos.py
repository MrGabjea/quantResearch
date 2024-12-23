import numpy as np
from pybit.unified_trading import HTTP
import pandas as pd
import numpy as np
import ta
import matplotlib.pyplot as plt
import random
#%%
def get_data(session, n, nom_crypto, intervale): 
    res = (session.get_mark_price_kline(
        category="linear",
        symbol=nom_crypto,
        interval=intervale,
        limit=n,
        ))['result']['list']
    df = (pd.DataFrame(res, columns=['time', 'openPrice', 'C', 'D','closePrice'])[['time', 'openPrice']]).iloc[::-1].reset_index(drop=True)
    df['openPrice'] = df['openPrice'].astype(float)
    df = df.rename(columns={'openPrice': 'price'})
    return(df)

session = HTTP(testnet=False)
#%%
def traitement_data(df):
    
    df['ma'] = ta.trend.EMAIndicator(close=df['price'], window=20).ema_indicator()
    df['logR'] = np.log(df['price']/df['price'].shift(1))
    df['maLog'] = ta.trend.EMAIndicator(close=df['logR'], window=100).ema_indicator()
    df['vol'] = df['logR'].rolling(window =50).std()
    n=40
    df['volkinj']= 0.5*(df['vol'].rolling(window=n).max() +  df['vol'].rolling(window=n).min())
    df['mavol'] = ta.trend.EMAIndicator(close=df['vol'], window=20).ema_indicator()
    
    df['maL'] = ta.trend.EMAIndicator(close=df['logR'], window=1).ema_indicator()
    return None

#%%
df_1 = get_data(session,1000,'BTCUSDT',30)
df_2 = get_data(session,1000,'POPCATUSDT',1)
#df = df_1
#df['price']= df_1['price']/df_2['price']

traitement_data(df_1)
traitement_data(df_2)
#traitement_data(df)
#%%

plt.plot((df_1['maL']-df_2['maL'])[800:])
plt.plot(ta.trend.EMAIndicator(close=(df_1['maL']-df_2['maL']), window=50).ema_indicator()[800:])
plt.grid()
plt.show()

#%%
plt.plot(df_1['vol'])
plt.plot(df_1['volkinj'])
plt.grid()
plt.show()

#%%

#plt.plot(df_1['price']/df_1['price'][0])
plt.plot(df_2['price']/df_2['vol'])
plt.grid()
plt.show()

#%% Backtest random

position = 0
L_position = []
L_portefeuille=[]
Portefeuille =0



for i in range(100,len(df_1)):
    Portefeuille += position*(df_1['price'][i]-df_1['price'][i-1])
    pos_prec = position
    
    if position ==0 : 
        position = random.choice([1,-1])
        tp = df_1['price'][i] *(1+position*0.01)
        sl = df_1['price'][i] * (1-position*0.01)
        
        
    else :
        if df_1['price'][i]>max(tp,sl) or df_1['price'][i]<min(tp,sl) :
            position = 0
    
    #Portefeuille += -(7/10000)*abs(position-pos_prec)*df_1['price'][i]
    L_portefeuille.append(Portefeuille)
    L_position.append(position)

#%%
plt.plot(L_portefeuille)
plt.show()

#%% backtest global

moy = 0
L= np.zeros(len(df_1)-100)
for k in range(1000):
    position = 0
    L_position = []
    L_portefeuille=[]
    Portefeuille =0



    for i in range(100,len(df_1)):
        Portefeuille += position*(df_1['price'][i]-df_1['price'][i-1])
        pos_prec = position
        
        if position ==0 and (df_1['vol'][i]>df_1['volkinj'][i]): 
            position = random.choice([1,-1])
            tp = df_1['price'][i] *(1+position*0.03)
            sl = df_1['price'][i] * (1-position*0.005)
        
       
            
            
        else :
            if df_1['price'][i]>max(tp,sl) or df_1['price'][i]<min(tp,sl) :
                position = random.choice([1,-1]) * (df_1['vol'][i]>df_1['volkinj'][i])
                tp = df_1['price'][i] *(1+position*0.03)
                sl = df_1['price'][i] * (1-position*0.005)
        
        Portefeuille += -(7/10000)*abs(position-pos_prec)*df_1['price'][i]
        L_portefeuille.append(Portefeuille)
        L_position.append(position)
    moy+=L_portefeuille[-1]
    L+= np.array(L_portefeuille)
    print(k)

print(moy/1000)
    



#%%
plt.plot(df_1['price'])

#%%
plt.plot(L)
plt.grid()
plt.show()


