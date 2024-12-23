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
    #df['ma'] = df['price'].rolling(window =5).mean()
    df['ma'] = ta.trend.EMAIndicator(close=df['price'], window=4).ema_indicator()
    return None


#%%
df_1 = get_data(session,1000,'TAOUSDT',120)
df_2 = get_data(session,1000,'ETHUSDT',120)
df = df_1
df['price']= df_1['price']/df_2['price']
#%%
traitement_data(df)
#%%
plt.plot(df['price'])
plt.plot(df['ma'])
plt.grid()
plt.show()
#%%

position = 0
L_position = []
L_portefeuille=[]
Portefeuille =0


for i in range(50,len(df)):
    Portefeuille += position*(df['price'][i]-df['price'][i-1])
    pos_prec = position
    count = 0
    for k in range(10,34,1):
        count += np.sign(np.log(df['ma'][i]/df['ma'][i-k]))
    position = np.sign(count) * (abs(count)>0)
    Portefeuille += -(13/10000)*abs(position-pos_prec)*df['price'][i]
    L_portefeuille.append(Portefeuille)#/df['price'][50])
    L_position.append(position) 
    
#%%
plt.plot(L_portefeuille) 
plt.grid() 
plt.show()    
