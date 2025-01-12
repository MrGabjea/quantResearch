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
n=0.0035
len_reset = 12
#%%
L_max =[]
L_portefeuille=[]
Portefeuille =0
N_order = []
delta=0
Sell = []
Sold = []
Buy = []
Bought = []


for i in range(len(df)):
    
    
    if Sold == [] and Bought ==[]:
        Sell=[]
        Buy=[]
        Sell.append((1+n)*df['openPrice'][i])
        Buy.append((1-n)*df['openPrice'][i])
        
    else:
        if Sold == []:
            Sell.append(df['openPrice'][i])
            Buy.append(df['openPrice'][i]*(1-n)**2)
            
        if Bought ==[]:
            Buy.append(df['openPrice'][i])
            Sell.append(df['openPrice'][i]*(1+n)**2)
    
    
    if np.mean(Sell)<df['high'][i]:
        Sold = Sold + Sell
        '''
        if len(Sold)!=0 and len(Bought)!=0:
            l=len(Buy)
            Buy = [np.mean(Sell)*(1-n)] * l
        '''
        Sell = []
    if np.mean(Buy)>df['low'][i]:
        Bought = Bought + Buy
        '''
        if len(Sold)!=0 and len(Bought)!=0:
            l=len(Sell)
            Sell = [np.mean(Buy)*(1+n)] * l
           '''
        Buy = []
    
    
    length = min(len(Sold),len(Bought))
    #print(len(Sold),len(Bought))
    if length !=0:
        Portefeuille += (np.mean(Sold[:length]) - np.mean(Bought[:length])-0.0004*np.mean(Sold[:length]))*length
        #print(len(Sold),len(Bought))
        N_order.append((len(Sold),len(Bought)))
        
           
    Sold = Sold[length:]
    Bought = Bought[length:]
    '''
    if len(Sold)>50:
        Portefeuille += -abs(np.mean(Sold)-df['openPrice'][i])*len(Sold)
        Sold = []
        Bought = []
        Sell=[]
        Buy = []
    if len(Bought)>50:
        Portefeuille += -abs(np.mean(Bought)-df['openPrice'][i])*len(Bought)
        Sold = []
        Bought = []
        Sell=[]
        Buy = []
    '''
    delta=0
    if len(Sold)!=0:
        delta = -abs(df['openPrice'][i]-np.mean(Sold))*len(Sold)
    if len(Bought)!=0:
        delta =-abs(df['openPrice'][i]-np.mean(Bought))*len(Bought)
    print(delta)
    if len(Bought)>len_reset or len(Sold)>len_reset :
        Li = Bought if (len(Bought)>len_reset)  else Sold
        Portefeuille += - df['openPrice'][i]*0.001*len(Li)
        
        Portefeuille = Portefeuille +delta
        delta=0
        Sell = []
        Sold = []
        Buy = []
        Bought = []
        
    L_portefeuille.append(Portefeuille + delta)


#%%
plt.plot(L_portefeuille)
plt.grid()
plt.show()

#%%
plt.plot(df['openPrice'])
