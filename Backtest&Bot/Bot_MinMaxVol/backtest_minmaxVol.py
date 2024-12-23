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
        endTime = '1731393000000',
        limit=n,
        ))['result']['list']
    df = (pd.DataFrame(res, columns=['time', 'openPrice', 'C', 'D','closePrice'])[['time', 'openPrice']]).iloc[::-1].reset_index(drop=True)
    df['openPrice'] = df['openPrice'].astype(float)
    df = df.rename(columns={'openPrice': 'price'})
    return(df)

session = HTTP(testnet=False)

#%%
def traitement_data(df):
    
    df['vol'] = df['price'].rolling(window =48).std()
    n = 24
    df['max'] = df['price'].rolling(window=n).max()
    df['min'] = df['price'].rolling(window=n).min()
    
    nvol = 84
    df['volmax'] = df['max'].rolling(window =nvol).std()
    df['volmin'] = df['min'].rolling(window =nvol).std()
    
    return None

#%%
df_1 = get_data(session,1000,'BTCUSDT',15)
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
    
    #Portefeuille += -(7/10000)*abs(position-pos_prec)*df['price'][i]
    L_portefeuille.append(Portefeuille)
    L_position.append(position)
    

#%%
plt.plot(L_portefeuille) 
#plt.plot(pd.DataFrame((L_portefeuille)).rolling(window =160).mean())
#plt.plot(pd.DataFrame((L_portefeuille)).rolling(window =288).mean())
#plt.plot(ta.trend.EMAIndicator(close=pd.DataFrame((L_portefeuille)).iloc[:, 0], window=288).ema_indicator())
plt.plot(pd.DataFrame((L_portefeuille)).rolling(window =6).mean())
plt.grid() 
plt.show()   
#%%
res = pd.DataFrame((L_portefeuille))
res.columns = ['valeur']
#%%
n = 1000
res['min'] = res['valeur'].rolling(window=n).min()
res['max'] = res['valeur'].rolling(window=n).max()
res['maxmin'] = res['min'].rolling(window=1000).max()
res['LT'] = res['valeur'].rolling(window=500).mean()
res['ST'] = res['valeur'].rolling(window=24).mean()

res['test'] = (res['maxmin']<res['valeur'])*1

res['a']= res['valeur']-  res['valeur'].shift(1)
res['b'] = (res['a']*res['test'])
res['fin'] = res['b'].cumsum()
#%%
plt.plot(res['valeur'])
#plt.plot(res['min'])
plt.plot(res['maxmin'])
plt.plot(res['fin'])# - 25*(7/10000)*90000)
#plt.plot(0.9*res['min']+0.1*res['max'])
plt.grid()
plt.show()


#%%


position = 0
L_position = []
L_portefeuille=[]
Portefeuille =0
MM =[]
MM2 = []
MM3 = []
p=0
P=0
LP =[]
Lpos=[]

for i in range(200,len(df)):
    Portefeuille += position*(df['price'][i]-df['price'][i-1])
    pos_prec = position

    position = -np.sign(df['volmax'][i]-df['volmin'][i]) 
    
    #Portefeuille += -(7/10000)*abs(position-pos_prec)*df['price'][i]
    L_portefeuille.append(Portefeuille)
    L_position.append(position)
    
    if len(L_portefeuille)>150 :
        d = pd.DataFrame(L_portefeuille)
        d.columns = ['valeur']
        d['vol'] =d['valeur'].rolling(window=60).std()
        d['minvol'] = d['vol'].rolling(window=10).min()
        d['maxminvol'] = d['minvol'].rolling(window=40).max()
        
        
        d['valeur'] =d['valeur'].rolling(window=4).mean()
        d['min'] = d['valeur'].rolling(window=60).min()
        #d['maxmin'] = d['min'].rolling(window=15).mean()
        d['maxmin'] =  d['min'].rolling(window=60).max()
        
        d['max'] = d['valeur'].rolling(window=30).max()
        d['minmax'] = d['max'].rolling(window=120).min()
        
        P += p*(df['price'][i]-df['price'][i-1])
        pprec = p
        p = position * ((d['maxmin'][len(d)-1]<d['valeur'][len(d)-1]))#*(d['vol'][len(d)-1]>d['mavol'][len(d)-1])#*(d['minmax'][len(d)-1]<d['valeur'][len(d)-1])
        P += -(7/10000)*abs(p-pprec)*df['price'][i]
        LP.append(P)
        Lpos.append(p)
        MM.append(d['maxmin'][len(d)-1])
        MM2.append(d['vol'][len(d)-1])
        MM3.append(d['maxminvol'][len(d)-1])
        
#%%
plt.plot(L_portefeuille[150:])
#plt.plot(d['valeur'][100:].values)
#plt.plot(MM)
#plt.plot(MM2)
plt.plot(LP)
plt.grid()
plt.show()

#%%
plt.plot(MM2)
plt.plot(MM3)



        