from ts2vg import NaturalVG
import networkx as nx
import numpy as np
from pybit.unified_trading import HTTP
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ta

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
    shift = 8
    df['ma']=df['price'].rolling(window = 200).mean()
    df['ema'] = ta.trend.EMAIndicator(close=df['price'], window=shift).ema_indicator()
    df['ema2'] = ta.trend.EMAIndicator(close=df['ema'], window=shift).ema_indicator()
    df['ema3'] = ta.trend.EMAIndicator(close=df['ema2'], window=shift).ema_indicator()
    df['ema4'] = ta.trend.EMAIndicator(close=df['ema3'], window=shift).ema_indicator()
    df['logR'] = np.log(df['ema4'] / df['ema4'].shift(1))
    return None
#%%
df = get_data(session,1000,'BTCUSDT',60)
traitement_data(df)
#%%
plt.plot(df['price'])
plt.plot(df['ema4'])

#plt.plot(df['logR'])
#plt.plot(df['ema4'])
#plt.plot(df['ma'])

#%%

ng = NaturalVG()
ng.build(df['ema4'].values[800:])
adj_matrix = ng.adjacency_matrix()

print(np.array(adj_matrix)[-1].sum())
#%%

position = 0
L_position = []
L_portefeuille=[]
Portefeuille =0



for i in range(100,len(df)):
    Portefeuille += position*(df['price'][i]-df['price'][i-1])
    pos_prec = position
    
    ng = NaturalVG()
    ng.build(df['ema4'].values[i-49:i+1])
    adj_matrix = ng.adjacency_matrix()
    count = np.array(adj_matrix)[-1].sum()
    if position ==0 :
        position = (count>10)*1 *(np.log(df['ema4'][i]/df['ema4'][i-1])>0)
    elif (np.log(df['ema4'][i]/df['ema4'][i-1])<0):
        position = 0
    #Portefeuille += -(7/10000)*abs(position-pos_prec)*df['price'][i]
    L_portefeuille.append(Portefeuille)
    L_position.append(position)
#%%
plt.plot(L_portefeuille) 
plt.grid() 
plt.show()

#%%


position = 0
L_position = []
L_portefeuille=[]
Portefeuille =0



for i in range(100,len(df)):
    Portefeuille += position*(df['price'][i]-df['price'][i-1])
    pos_prec = position
    
    if df['logR'][i]>0.0005 : 
        position = 1
    if df['logR'][i]<0:
        position =0
    #Portefeuille += -(7/10000)*abs(position-pos_prec)*df['price'][i]
    L_portefeuille.append(Portefeuille)
    L_position.append(position)
    
#%%
plt.plot(L_portefeuille) 
plt.grid() 
plt.show()