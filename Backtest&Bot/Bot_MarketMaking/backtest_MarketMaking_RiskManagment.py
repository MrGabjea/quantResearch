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

df = get_data(session, 1000, 'DOGEUSDT',5)
#%%
n=0.0014

df['MM']= np.array( [ ((df['openPrice'][i]*(1+n))<df['high'][i] ) and ((df['openPrice'][i]*(1-n))>df['low'][i] ) for i in range(len(df))] )
df['vol'] = df['openPrice'].rolling(window =48).std()/df['openPrice']

#%%

position = 0

L_portefeuille=[]
Portefeuille =0

Taille_pos =[]
N_order = []
Sell_order = []
Buy_order = []

for i in range(len(df)):
    if np.mean(Sell_order)<df['high'][i]:
        N_order.append(len(Sell_order))
        Portefeuille += len(Sell_order)*(2*n-0.0004)*np.mean(Sell_order)/(1+n)
        Sell_order = []
    if np.mean(Buy_order)>df['low'][i]:
        N_order.append(-len(Buy_order))
        Portefeuille += len(Buy_order)*(2*n-0.0004)*np.mean(Buy_order)/(1-n)
        Buy_order = []
        
    if df['MM'][i] : Portefeuille += (2*n-0.0004)*df['openPrice'][i]

    else : 
        if df['high'][i]<(df['openPrice'][i]*(1+n)) and df['low'][i]<(df['openPrice'][i]*(1-n)):
            Sell_order.append(df['openPrice'][i]*(1+n))
        if df['low'][i]>(df['openPrice'][i]*(1-n)) and df['high'][i]>(df['openPrice'][i]*(1+n)):
            Buy_order.append(df['openPrice'][i]*(1-n))
    
    Taille_pos.append(abs(len(Sell_order)-len(Buy_order)))
     
    L_portefeuille.append(Portefeuille)
    
#%%
plt.plot(L_portefeuille)
plt.grid()
plt.show()

#%% backtest avec suivi de portefeuille

position = 0

L_portefeuille=[]
Portefeuille =0

N_order = []
Sell_order = []
Buy_order = []

for i in range(len(df)):
    if np.mean(Sell_order)<df['high'][i]:
        N_order.append(len(Sell_order))
        Portefeuille += len(Sell_order)*(2*n-0.0004)*np.mean(Sell_order)/(1+n)
        Sell_order = []
    if np.mean(Buy_order)>df['low'][i]:
        N_order.append(-len(Buy_order))
        Portefeuille += len(Buy_order)*(2*n-0.0004)*np.mean(Buy_order)/(1-n)
        Buy_order = []
        
    if df['vol'][i]<0.01:
        if df['MM'][i] : Portefeuille += (2*n-0.0004)*df['openPrice'][i]

        else : 
            if df['high'][i]<(df['openPrice'][i]*(1+n)) and df['low'][i]<(df['openPrice'][i]*(1-n)):
                Sell_order.append(df['openPrice'][i]*(1+n))
            if df['low'][i]>(df['openPrice'][i]*(1-n)) and df['high'][i]>(df['openPrice'][i]*(1+n)):
                Buy_order.append(df['openPrice'][i]*(1-n))
        
    delta=0
    for so in Sell_order: delta += -(so/((1+n)**2) - df['openPrice'][i])
    for bo in Buy_order: delta += (bo/((1-n)**2) - df['openPrice'][i])
        
     
    L_portefeuille.append(Portefeuille+delta)


#%% backtest sans prime au premier

position = 0

L_portefeuille=[]
Portefeuille =0

N_order = []
Sell_order = []
Buy_order = []

for i in range(len(df)):
    
    if df['vol'][i]<0.1:
        Sell_order.append((1+n)*df['openPrice'][i])
        if len(Sell_order)>50:
            L_discard = Sell_order[:2]
            Sell_order = Sell_order[2:]
            for so in L_discard:
                Portefeuille += -(so/((1+n)**2) - df['openPrice'][i])
        Buy_order.append(df['openPrice'][i]*(1-n))
        if len(Buy_order)>50:
            L_discard = Buy_order[:2]
            Buy_order = Buy_order[2:]
            for bo in L_discard:
                Portefeuille += (bo/((1-n)**2) - df['openPrice'][i])
        
    
   
    if np.mean(Sell_order)<df['high'][i]:
        N_order.append(len(Sell_order))
        Portefeuille += min(len(Sell_order),100)*(2*n-0.0004)*np.mean(Sell_order)/(1+n)
        Sell_order = []
    if np.mean(Buy_order)>df['low'][i]:
        N_order.append(-len(Buy_order))
        Portefeuille += min(len(Buy_order),100)*(2*n-0.0004)*np.mean(Buy_order)/(1-n)
        Buy_order = []
        
    
    delta=0
    for so in Sell_order: delta += -(so/((1+n)**2) - df['openPrice'][i])
    for bo in Buy_order: delta += (bo/((1-n)**2) - df['openPrice'][i])
        
     
    L_portefeuille.append(Portefeuille+delta)
    

#%%
plt.plot(df['vol'])

plt.grid()
plt.show()
