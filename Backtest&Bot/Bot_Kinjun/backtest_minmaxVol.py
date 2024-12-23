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
    
    df['vol'] = df['price'].rolling(window =96).std()
    n = 48
    df['max'] = df['price'].rolling(window=n).max()
    df['min'] = df['price'].rolling(window=n).min()
    
    nvol = 72
    df['volmax'] = df['max'].rolling(window =nvol).std()
    df['volmin'] = df['min'].rolling(window =nvol).std()
    
    return None

#%%
df_1 = get_data(session,1000,'BTCUSDT',5)
df_2 = get_data(session,1000,'BTCUSDT',5)
df = df_1
#df['price']= df_1['price']/df_2['price']

#%%
traitement_data(df)


#%%
plt.plot(df['vol'])
plt.plot(df['volmax'])
plt.plot(df['volmin'])
plt.grid()
plt.show()

#%%
plt.plot(df['price'])
plt.plot(df['max'])
plt.plot(df['min'])
#plt.plot(L)
#plt.plot(df['LT']+ 0.5*df['vol'])
#plt.plot(df['LT']- 0.5*df['vol'])


plt.grid()
plt.show()

#%%
position = 0
L_position = []
L_portefeuille=[]
Portefeuille =0


for i in range(200,len(df)):
    Portefeuille += position*(df['price'][i]-df['price'][i-1])
    pos_prec = position

    position = -np.sign(df['volmax'][i]-df['volmin'][i]) 
    
    Portefeuille += -(7/10000)*abs(position-pos_prec)*df['price'][i]
    L_portefeuille.append(Portefeuille)
    L_position.append(position)
    

#%%
plt.plot(L_portefeuille) 
plt.plot(pd.DataFrame((L_portefeuille)).rolling(window =160).mean())
plt.plot(pd.DataFrame((L_portefeuille)).rolling(window =288).mean())
#plt.plot(ta.trend.EMAIndicator(close=pd.DataFrame((L_portefeuille)).iloc[:, 0], window=288).ema_indicator())
plt.plot(pd.DataFrame((L_portefeuille)).rolling(window =6).mean())
plt.grid() 
plt.show()   

    
#%%
pos = 0
Lp_portefeuille=[]
BPortefeuille =0

position = 0
L_portefeuille=[]
Portefeuille =0


for i in range(150,len(df)):
    Portefeuille += position*(df['price'][i]-df['price'][i-1])
    BPortefeuille += pos*(df['price'][i]-df['price'][i-1])
    po_prec = pos
    pos_prec = position

    position = -np.sign(df['volmax'][i]-df['volmin'][i]) 
    
    Portefeuille += -(7/10000)*abs(position-pos_prec)*df['price'][i]
    L_portefeuille.append(Portefeuille)
    
    if len(L_portefeuille)>=160 : 
        test = np.sign(np.mean(np.array(L_portefeuille)[-8:])-np.mean(np.array(L_portefeuille)[-288:]))
        pos = test*position
        Lp_portefeuille.append(BPortefeuille)
        BPortefeuille += -(7/10000)*abs(pos-po_prec)*df['price'][i]
    else : 
        Lp_portefeuille.append(0)
        




#%%
    

plt.plot(Lp_portefeuille) 
plt.plot(np.array(L_portefeuille)-L_portefeuille[95])
plt.grid() 
plt.show()   

#%%
position = 0
L_portefeuille=[]
Portefeuille =0

for i in range(500,len(df)):
    Portefeuille += position*(df['price'][i]-df['price'][i-1])
    pos_prec = position
    
    position = -np.sign(df['volmax'][i]-df['volmin'][i])
    
    P = 0
    L = []
    pos = 0
    for k in range(i-288,i):
        P+=pos*(df['price'][k]-df['price'][k-1])
        pos = np.sign(df['volmax'][k]-df['volmin'][k])
        L.append(P)
    position *= -np.sign(np.mean(np.array(L)[-8:])-np.mean(np.array(L)))
    Portefeuille += -(7/10000)*abs(position-pos_prec)*df['price'][i]
    L_portefeuille.append(Portefeuille)
    
#%%
plt.plot(L_portefeuille) 
plt.grid() 
plt.show()   















        