import numpy as np
from pybit.unified_trading import HTTP
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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

df = get_data(session, 1000, 'BTCUSDT',5)

#%%

count = 0


for i in range(len(df)):
    count += ((df['openPrice'][i]*(1+0.0005))<df['high'][i] ) and ((df['openPrice'][i]*(1-0.0005))>df['low'][i] ) 
print(count/len(df))

#%%
n=0.0005

df['MM']= np.array( [ ((df['openPrice'][i]*(1+n))<df['high'][i] ) and ((df['openPrice'][i]*(1-n))>df['low'][i] ) for i in range(len(df))] )

#%%

plt.plot(df['closePrice'])
#plt.plot(df['high'])
#plt.plot(df['low'])
plt.grid()
plt.show()


#%%

position = 0

L_portefeuille=[]
Portefeuille =0

Sell_order = []
Buy_order = []

for i in range(len(df)):
    if df['MM'][i] : Portefeuille +=(2*n-0.0004)*df['openPrice'][i]

    else : 
        if df['high'][i]<(df['openPrice'][i]*(1+n)) : Sell_order.append((df['openPrice'][i]*(1+n)))
        if df['low'][i]>(df['openPrice'][i]*(1-n)) : Buy_order.append((df['openPrice'][i]*(1-n)))
    
    L_bo = []
    for bo in Buy_order : 
        if df['low'][i]< bo : Portefeuille+=(2*n-0.0004)*bo/(1-n)
        else: 
            
            
            L_bo.append(bo)
    Buy_order = L_bo
    
    L_so = []
    for so in Sell_order : 
        if df['high'][i]> so : Portefeuille+=(2*n-0.0004)*bo/(1-n)
        else: L_so.append(so)
    Sell_order = L_so
    
           
    L_portefeuille.append(Portefeuille)
#%%

plt.plot(L_portefeuille)
plt.show()
    
    
#%%
dette =Portefeuille + (Buy_order - df['closePrice'].iloc[-1]).sum() + (df['closePrice'].iloc[-1] - Sell_order).sum()
  
