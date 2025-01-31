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

df = get_data(session, 1000, 'DOGEUSDT',30)

#%%


def traitement_data(df):
    df['diff'] = df['high']-df['low']
    df['ATR']= df['diff'].rolling(window=14).mean()
    df['vol']= (df['closePrice']-df['openPrice'])/2
    return None
    
#%%
traitement_data(df)
#%%

plt.plot(df['ATR'])
plt.plot(abs(df['vol']))
plt.grid()
plt.show()

#%%
plt.plot(df['openPrice'])
plt.show()

#%%

tp = 0
sl = 0
entry =0
inter = 0
InterDone = False
N=0
Intrade = False
Long =True
k = 0
Liste= []
Raté = 0
Gagné = 0
Outime=0
Beven =0
for i in range(20,len(df)):
    
    if Intrade:
        Liste.append(df['openPrice'][i])
        if sl>df['low'][i] and sl<df['high'][i]:
            #print(Liste)
            Intrade = False
            if not(InterDone):   
                Raté +=1
            else: Beven+=1
            #print(i-k)
            
        else:
            if tp>df['low'][i] and tp<df['high'][i]:
                Intrade = False
                Gagné +=1
                #print(i-k)
                #print(Liste)
            
            elif inter>df['low'][i] and inter<df['high'][i] and not(InterDone):
                sl =entry
                InterDone =True
            
       
            elif i-k >24:
                Intrade = False
                Outime +=1
                print(Liste)
    
    if not(Intrade):
        if abs(df['vol'][i])>df['ATR'][i]:
            k = i
            Intrade = True
            N+=1
            InterDone = False
            entry = df['closePrice'][i]+1.5*np.sign(df['vol'][i])*df['ATR'][i]
            inter =df['closePrice'][i] +3*np.sign(df['vol'][i])*df['ATR'][i]
            tp = df['closePrice'][i] +4.5*np.sign(df['vol'][i])*df['ATR'][i]
            sl = df['closePrice'][i] -1.5*np.sign(df['vol'][i])*df['ATR'][i]
            Liste = [np.sign(df['vol'][i])]
    
