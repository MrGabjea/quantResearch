import numpy as np
from pybit.unified_trading import HTTP
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

session = HTTP(testnet=False)
######################################################################################################################
#%%

def get_data(session, n, nom_crypto, intervale): 
    res = (session.get_mark_price_kline(
        category="linear",
        symbol=nom_crypto,
        interval=intervale,
        limit=n,
        ))['result']['list']
    df = (pd.DataFrame(res, columns=['time', 'openPrice', 'high', 'low','closePrice'])).iloc[::-1].reset_index(drop=True)
    price_columns = ['openPrice', 'high', 'low', 'closePrice']
    df[price_columns] = df[price_columns].astype(float)
    #df = df.rename(columns={'openPrice': 'price'})
    return(df)

#%%

df = get_data(session, 1000, 'DOGEUSDT',5)
#%%
df['ma1'] = df['openPrice'].rolling(window=60).mean()
df['ma2'] = df['openPrice'].rolling(window=90).mean()

#%%
plt.plot(df['openPrice'])
plt.plot(df['ma1'])
plt.plot(df['ma2'])
plt.show()
#%%
n= 0.01
L_Portefeuille =[]
Portefeuille = 0

Sell = 0
Buy = 0
Bought = False
Sold = False
Intrade = False
start_trade = 0
for i in range(200,len(df)):
    m = min(df['ma1'][i],df['ma2'][i])
    M= max(df['ma1'][i],df['ma2'][i])
    
    if df['openPrice'][i]<M and df['openPrice'][i]>m and not(Intrade):
    
        Buy = (1-n)*df['openPrice'][i]
        Sell = (1+n)*df['openPrice'][i]
        Intrade = True
        start_trade = i
        print(i)
    if Intrade:
        if (df['low'][i]<Buy) and not(Bought) : 
            Bought = True
        if df['high'][i]>Sell and not(Sold):
            Sold =True
    if Bought and Sold :
        Intrade = False
        Bought = False
        Sold = False
        print("success")
        Portefeuille += Sell-Buy - 0.0004*Sell
    if Intrade and i-start_trade>12 :
        Portefeuille += Bought*(df['openPrice'][i]-Buy) + Sold*(Sell - df['openPrice'][i]) -df['openPrice'][i]*0.001 
        Intrade =False
    if Intrade :
        if Bought and not(Sold):
            L_Portefeuille.append(Portefeuille + df['openPrice'][i]-Buy)
        if Sold and not(Bought) :
            L_Portefeuille.append(Portefeuille +Sell - df['openPrice'][i])
    else :
        L_Portefeuille.append(Portefeuille)        
    
#%%
plt.plot(L_Portefeuille)
plt.show()    
