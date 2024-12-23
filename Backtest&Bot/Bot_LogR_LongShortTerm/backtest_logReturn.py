import numpy as np
from pybit.unified_trading import HTTP
import pandas as pd
import numpy as np

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
    df['std'] = df['price'].rolling(window =48).std()
    df['ma100'] = df['price'].rolling(window =6).mean()
    #df['normaPrice'] = (df['price'])/df['std']
    df['logR'] = np.log(df['price'] / df['price'].shift(1))
    df['maLog1'] = df['logR'].rolling(window =50).mean()
    df['test'] = df['maLog1'].rolling(window =1).mean()
    df['maLog2'] = df['logR'].rolling(window =60).mean()
    df['maLog3'] = df['logR'].rolling(window =40).mean()
    return None


#%%
df_1 = get_data(session,1000,'WIFUSDT',60)
df_2 = get_data(session,1000,'BTCUSDT',60)
df = df_1
df['price']= df_1['price']/df_2['price']
#%%
traitement_data(df_1)
traitement_data(df_2)
#%%
traitement_data(df)
#%%

#plt.plot(df['test'][100:])
plt.plot(df['maLog1'][100:])
plt.plot(df['maLog2'][100:])
plt.plot(df['maLog3'][100:])
#plt.plot((df['maLog1']+df['maLog1']+df['maLog1'])/3)
plt.grid()
#%%
plt.plot(df['price'][100:])
#%%

position = 0
L_position = []
L_portefeuille=[]
Portefeuille =0


for i in range(100,len(df)):
    Portefeuille += position*(df['price'][i]-df['price'][i-1])
    pos_prec = position
    position = 2*np.sign((df['maLog1'][i]))-np.sign((df['maLog3'][i]))-np.sign((df['maLog2'][i])) #* (abs((2*df['maLog1']+df['maLog2']+df['maLog3'])[i])>0.004)
    #position *=(df['deriv_100'][i]*position>0)
    Portefeuille += -(14/10000)*abs(position-pos_prec)*df['price'][i]
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


for i in range(150,len(df)):
    Portefeuille += position*(df['price'][i]-df['price'][i-1])
    pos_prec = position
    position =0
    for r in range(1,2):
        position += np.sign(df['maLog'+ str(r)][i]) # * (abs(df['maLog'][i])>0.000)
    #position *=(df['deriv_100'][i]*position>0)
    Portefeuille += -(14/10000)*abs(position-pos_prec)*df['price'][i]
    L_portefeuille.append(Portefeuille)
    L_position.append(position) 
    
#%%
plt.plot(L_portefeuille) 
plt.grid() 
plt.show()  

#%%
def deriv_poly(L,size,degre):
    x=np.array([-size+i+1 for i in range(size)])
    P = np.polyfit(x, L[-size:], degre)
    return(P[degre-1]) 

#%%
position = 0
L_position = []
L_portefeuille=[]
Portefeuille =0


for i in range(100,len(df)):
    Portefeuille += position*(df['price'][i]-df['price'][i-1])
    pos_prec = position
    
    
    
    position = -np.sign( deriv_poly(df['test'].values[:i+1],20,3))
    #position *=(df['deriv_100'][i]*position>0)
    #Portefeuille += -(14/10000)*abs(position-pos_prec)*df['price'][i]
    L_portefeuille.append(Portefeuille)
    L_position.append(position) 
    
#%%
plt.plot(L_portefeuille) 
plt.grid() 
plt.show()  

#%%




