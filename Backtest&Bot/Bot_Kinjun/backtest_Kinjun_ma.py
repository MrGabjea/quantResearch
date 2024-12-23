import numpy as np
from pybit.unified_trading import HTTP
import pandas as pd
import numpy as np
import ta
import matplotlib.pyplot as plt
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
    df['ma1'] = df['price'].rolling(window =6).mean()
    df['volP'] = df['price'].rolling(window =48).std()
    df['logR'] = (np.log(df['price']))#/df['price'].shift(1)))
    df['ma'] = ta.trend.EMAIndicator(close=df['price'], window=6).ema_indicator()
    df['LT'] = df['price'].rolling(window =96).mean()
    #df['LT'] = ta.trend.EMAIndicator(close=df['price'], window=84).ema_indicator()
    df['vol'] = df['logR'].rolling(window =84).std()
    n=84
    df['volkinj']= 0.5*df['vol'].rolling(window=n).max() + 0.5*df['vol'].rolling(window=n).min()
    df['mavol'] = ta.trend.EMAIndicator(close=df['vol'], window=60).ema_indicator()
    
    df['expPrice'] = np.exp(np.log(df['LT'])+df['vol'])
    return None


#%%
df_1 = get_data(session,1000,'ETHUSDT',15)
df_2 = get_data(session,1000,'BTCUSDT',15)
df = df_1
df['price']= df_1['price']/df_2['price']

#%%
traitement_data(df)


#%%
plt.plot(df['vol'])
plt.plot(df['volkinj'])
plt.plot(df['mavol'])
plt.grid()
plt.show()
#%%
plt.plot(df['price'])
#plt.plot(np.exp(np.log(df['LT'])+df['vol']))
#plt.plot(df['ma'])
#plt.plot(df['LT'])
plt.grid()
plt.show()


#%%
position = 0
L_position = []
L_portefeuille=[]
Portefeuille =0


for i in range(120,len(df)):
    Portefeuille += position*(df['price'][i]-df['price'][i-1])
    pos_prec = position
    
    position = (2*(df['ma1'][i]>df['LT'][i])-1) * ((df['vol'][i]>df['volkinj'][i]))#*500/df['volP'][i]# or (df['vol'][i]>df['mavol'][i]))
    
    Portefeuille += -(7/10000)*abs(position-pos_prec)*df['price'][i]
    L_portefeuille.append(Portefeuille)
    L_position.append(position)
    
#%%
plt.plot(L_portefeuille) 
plt.grid() 
plt.show()   

    