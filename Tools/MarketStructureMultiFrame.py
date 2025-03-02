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

def traitement_data(df):
    df['diff'] = df['high']-df['low']
    df['ATR']= df['diff'].rolling(window=30).mean()
    return None


#%%
df = get_data(session, 1000, 'DOGEUSDT', 5)
#%%
traitement_data(df)

#%%
k=8
sens = 1
optimum = 0
indice = 0
seuil = 0

L = []

for i in range(20,len(df)):
    if sens ==1:
        if df['high'][i]>optimum:
            optimum =df['high'][i]
            indice = i
            seuil = df['high'][i]-k*df['ATR'][i]
            #print(i)
            
        if seuil>df['low'][i]:
            L.append((indice,sens))
            optimum = df['low'][i]
            seuil =df['low'][i]+k*df['ATR'][i]
            indice = i
            sens *= -1
            
    elif sens == -1:
        if df['low'][i]<optimum:
            optimum = df['low'][i]
            indice = i
            seuil = df['low'][i]+k*df['ATR'][i]
        if seuil<df['high'][i]:
            L.append((indice,sens))
            optimum = df['high'][i]
            seuil = df['high'][i]-k*df['ATR'][i]
            indice = i
            sens *=-1
            
            
#%%
index = [0 for i in range(len(df))]
for i in L:
    index[i[0]]=i[1]

df['trend'] = [
    df.loc[i, 'high'] if index[i] == 1 else
    df.loc[i, 'low'] if index[i] == -1 else
    np.nan
    for i in range(len(df))
]

#%%

ind=[i[0] for i in L]
val = df.loc[ind]['trend']
plt.plot(df['openPrice'])
plt.plot(ind,val)
plt.show()


#%%
Top =[]
Bot = []
for i in L:
    if i[1]==1:
        Top.append(i[0])
    else: 
        Bot.append(i[0])

Top2=[]
Bot2=[]
for i in range(1,len(Top)-1):
    if df['trend'][Top[i]]>df['trend'][Top[i-1]] and df['trend'][Top[i]]>df['trend'][Top[i+1]]:
        Top2.append(Top[i])
for i in range(1,len(Bot)-1):
    if df['trend'][Bot[i]]<df['trend'][Bot[i-1]] and df['trend'][Bot[i]]<df['trend'][Bot[i+1]]:
        Bot2.append(Bot[i])

#%%
ind=[i[0] for i in L]
L2= sorted(Top2+Bot2)
val = df.loc[ind]['trend']
plt.plot(df['openPrice'])
plt.plot(ind,val)
plt.plot(L2,df.loc[L2]['trend'])
plt.show()



#%% Backtest avec schema epaule tete epaule




k=8
sens = 1
optimum = 0
indice = 0
seuil = 0
InTrade =False
Config=False
raté=0
gagné=0

Top = []
for i in range(20,len(df)):
    if sens ==1:
        if df['high'][i]>optimum:
            optimum =df['high'][i]
            indice = i
            seuil = df['high'][i]-k*df['ATR'][i]
        if len(Top)>=2:
            if Top[-2]>Top[-1]>optimum :
                Config =True
            else: 
                Config = False
        if seuil>df['low'][i]:
            if Config and not(InTrade):
                print(i)
                print(Top[-1],Top[-2],optimum)
                InTrade = True
                entry = seuil
                sl = optimum
                tp = entry -5*(optimum -seuil)
                
            Top.append(df['high'][indice])
            optimum = df['low'][i]
            seuil =df['low'][i]+k*df['ATR'][i]
            indice = i
            sens *= -1
            
            
    elif sens == -1:
        if df['low'][i]<optimum:
            optimum = df['low'][i]
            indice = i
            seuil = df['low'][i]+k*df['ATR'][i]
        if seuil<df['high'][i]:
            
            optimum = df['high'][i]
            seuil = df['high'][i]-k*df['ATR'][i]
            indice = i
            sens *=-1
    if InTrade:
        if sl<df['high'][i]:
            raté +=1
            InTrade = False
        elif tp>df['low'][i]:
            gagné +=1
            InTrade=False
        

#%%
diff=[]
for i in range(len(L)-1):
    if L[i][1]==1:
        k=(df['high'][L[i][0]]-df['low'][L[i+1][0]])/df['ATR'][L[i][0]]
    else:
        k=-(df['low'][L[i][0]]-df['high'][L[i+1][0]])/df['ATR'][L[i][0]]
    diff.append(k)
