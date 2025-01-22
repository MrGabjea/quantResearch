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
n=0.014

#%%

L_portefeuille=[]
Portefeuille =0

N_order = []

L=[]

Sell = []
Sold = []
Buy = []
Bought = []

Active = False
N_active=0
P=0
L_p=[]

for i in range(len(df)):
    
    # update des liste Sold et Bought
    length = min(len(Sold),len(Bought))
    if length !=0:
        print(length)
        Portefeuille += (np.mean(Sold[:length]) - np.mean(Bought[:length])-0.0004*np.mean(Sold[:length]))*length
        #print(len(Sold),len(Bought))
        N_order.append((i,len(Sold),len(Bought)))
        if Active : 
            if N_active<1 :
                #print(length)
                P += (np.mean(Sold[:length]) - np.mean(Bought[:length])-0.0004*np.mean(Sold[:length]))*length
                N_active +=1
            if N_active>=1:
                Active = False
    Sold = Sold[length:]
    Bought = Bought[length:]
    
    delta=0
    if len(Sold)!=0:
        delta = -(df['openPrice'][i]-np.mean(Sold))*len(Sold)
    if len(Bought)!=0:
        delta =(df['openPrice'][i]-np.mean(Bought))*len(Bought)
        
        
        
    # update si les postions sont trop grosses
    if len(Sold)>36:
        
        if Active:
            P += ((np.mean(Sold)-df['openPrice'][i])*len(Sold) - 0.0004*df['openPrice'][i]*len(Sold))
            #print("fail",P)
        Portefeuille += (np.mean(Sold)-df['openPrice'][i])*len(Sold) - 0.0004*df['openPrice'][i]*len(Sold)
        print("fail",len(Sold),Portefeuille)
        Sold = []
        Bought = []
        Sell=[]
        Buy = []
        L.append(i)
        
        Active = True
        N_active = 0
        
    if len(Bought)>36:
        
       
        if Active:
            P += (-(np.mean(Bought)-df['openPrice'][i])*len(Bought) - 0.0004*df['openPrice'][i]*len(Bought))
            #print("fail",P)
            
        Portefeuille += -(np.mean(Bought)-df['openPrice'][i])*len(Bought) - 0.0004*df['openPrice'][i]*len(Bought)
        print("fail",len(Bought),Portefeuille)
        Sold = []
        Bought = []
        Sell=[]
        Buy = []
        L.append(i)
        
        Active = True
        N_active = 0
    
    # placement des futurs positions
    if Sold == [] and Bought ==[]:
        #if True:# Active:
            #Sell=[]
            #Buy=[]
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
        Sell = []
    if np.mean(Buy)>df['low'][i]:
        Bought = Bought + Buy
        Buy = []
    L_portefeuille.append(Portefeuille+delta)
    L_p.append(P+Active*delta)
    
#%%
plt.plot(L_p)
plt.grid()
plt.show()

#%% Seconde verison pour retest
ls=0
lb=0
L=[]

Sell = []
Sold = []
Buy = []
Bought = []

Active = False

P=0
L_p=[]


for i in range(len(df)):
   
    
    # update des listes Sold et Bought
    length = min(len(Sold),len(Bought))
    if length !=0:
        
        
        if Active :
            print(length)
            P += (np.mean(Sold[:length]) - np.mean(Bought[:length])-0.0005*np.mean(Sold[:length]))*length
            Active = False
            
    Sold = Sold[length:]
    Bought = Bought[length:]
    
    delta=0
    if len(Sold)!=0:
        delta = -(df['openPrice'][i]-np.mean(Sold))*len(Sold)
    if len(Bought)!=0:
        delta =(df['openPrice'][i]-np.mean(Bought))*len(Bought)
    
    
    # check si les positions sont trop grosses
    if len(Sold)>36:
        if Active:
            
            #P+= (np.mean(Sold)-df['openPrice'][i])*len(Sold) - 0.001*df['openPrice'][i]*len(Sold)
            P+= ((np.mean(Sold)-df['openPrice'][i])*36 - 0.001*df['openPrice'][i]*36)*((len(Sold)-ls)<36)
        Sold = []
        Bought = []
        Sell=[]
        Buy = []
        
        Active = True
        
    if len(Bought)>36:
        if Active:
            
            #P+= -(np.mean(Bought)-df['openPrice'][i])*len(Bought) - 0.001*df['openPrice'][i]*len(Bought)
            P+= (-(np.mean(Bought)-df['openPrice'][i])*36 - 0.001*df['openPrice'][i]*36)*((len(Bought)-lb)<36)
        Sold = []
        Bought = []
        Sell=[]
        Buy = []
        
        Active = True
       
        
       
    # placement des futurs positions
    if Sold == [] and Bought ==[]:
        Sell.append((1+n)*df['openPrice'][i])
        Buy.append((1-n)*df['openPrice'][i])
        
    else:
        if Sold == []:
            Sell.append(df['openPrice'][i])
            Buy.append(df['openPrice'][i]*(1-n)**2)
            
        if Bought ==[]:
            Buy.append(df['openPrice'][i])
            Sell.append(df['openPrice'][i]*(1+n)**2)
    ls=len(Sold)
    lb=len(Bought)
    print(len(Sold),len(Bought))
    if np.mean(Sell)<df['high'][i]:
        Sold = Sold + Sell
        Sell = []
    if np.mean(Buy)>df['low'][i]:
        Bought = Bought + Buy
        Buy = []
      
    L_p.append(P+Active*delta)
