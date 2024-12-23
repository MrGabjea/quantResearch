import numpy as np
from pybit.unified_trading import HTTP
import pandas as pd
import numpy as np
import requests
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
    df = (pd.DataFrame(res, columns=['time', 'openPrice', 'max', 'min','closePrice'])[['time', 'openPrice','max','min']]).iloc[::-1].reset_index(drop=True)
    df['openPrice'] = df['openPrice'].astype(float)
    df['max'] = df['max'].astype(float)
    df['min'] = df['min'].astype(float)
    df = df.rename(columns={'openPrice': 'price'})
    return(df)

session = HTTP(testnet=False)

#%%
def traitement_data(df):
    df['ma'] = df['price'].rolling(window =30).mean()
    df['vol'] = df['price'].rolling(window =48).std()
   #df['volmax'] = df['max'].rolling(window =96).std()
    #df['volmin'] = df['min'].rolling(window =96).std()
    return None
#%%
df = get_data(session,1000,'BTCUSDT',240)
#%%
traitement_data(df)
#%%
plt.plot(df['vol'])
#plt.plot(df['volkinj'])
plt.show()
#%%
startingp=10

x= np.array([-150+i for i in range(150)])
y = df['price'][startingp:startingp+150].values
P = np.polyfit(x,y,3)


#%%

poly_vals = np.polyval(P, x)
#%%
plt.plot(poly_vals)
plt.plot(df['price'][startingp:400].values)
plt.show()


#%%

def deriv_poly(L,size,degre):
    x=np.array([-size+i+1 for i in range(size)])
    P = np.polyfit(x, L[-size:], degre)
    return(P[degre-1])

def acc_poly(L,size,degre):
    x=np.array([-size+i+1 for i in range(size)])
    P = np.polyfit(x, L[-size:], degre)
    return(P[degre-2]/2)

#%%
df_1 = get_data(session,1000,'SOLUSDT',60)
df_2 = get_data(session,1000,'BTCUSDT',60)
df = df_1
#df['price']= df_1['price']/df_2['price']
#df['ma']= df['price'].rolling(window =2).mean()
df['ma'] = ta.trend.EMAIndicator(close=df['price'], window=1).ema_indicator()
"""
for i in range(4):
    df['ma']= df['ma'].rolling(window =2).mean()
    """
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

n_rebal = 1

for i in range(500,len(df)):
    Portefeuille += position*(df['price'][i]-df['price'][i-1])
    pos_prec = position
    if i%n_rebal==0:
        position1 = 0
        position2 = 0
        degre = 3
        for k in [150]:
            position1 += np.sign(deriv_poly(df['ma'].values[:i],k,degre ))
            #position2 += np.sign(deriv_poly((df['price'].values)[i-k:i],k,3 ))
        
        degre = 3
        count = 0
        '''
        for k in range(40,60):
            count += np.sign(deriv_poly(df['price'].values[:i],k,degre ))
        '''
        position = position1/2# + 1.5*np.sign(count)
       
    #position *=(df['deriv_100'][i]*position>0)
    Portefeuille += -(7/10000)*abs(position-pos_prec)*df['price'][i]
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

n_rebal=1

for i in range(1000,len(df)):
    Portefeuille += position*(df['price'][i]-df['price'][i-1])
    pos_prec = position
    if i%n_rebal==0:
        position1 = 0
        position2 = 0
        degre = 1
        count = 0
        for k in range(20,100,5):
            #test = (deriv_poly(df['ma'].values[:i],k,degre ) * acc_poly(df['ma'].values[:i],k,degre ))>0
            #count += np.sign(deriv_poly(df['ma'].values[:i],k,degre ))# *test
            count += deriv_poly(df['price'].values[:i],k,degre )
            #position2 += np.sign(deriv_poly((df['price'].values)[i-k:i],k,3 ))
        
        position = round(np.sign(count) * (abs(count)>0))#*1000/df['vol'][i],2) #*(df['vol'][i]>df['volkinj'][i])
        #position = count
    #position *=(df['deriv_100'][i]*position>0)
    #Portefeuille += -(7/10000)*abs(position-pos_prec)*df['price'][i]
    L_portefeuille.append(Portefeuille)
    L_position.append(position) 

#%%
plt.plot(L_portefeuille) 
#plt.plot(pd.DataFrame(L_portefeuille)[0].rolling(window =90).min().rolling(window =90).mean())
#plt.plot(pd.DataFrame(L_portefeuille)[0].rolling(window =90).max().rolling(window =60).mean())
plt.grid() 
plt.show()
