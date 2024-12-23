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

def traitement_data(df,size_vol,size_backward):
    
    #df['vol'] = df['price'].rolling(window =96).std()
    n = size_backward
    df['max'] = df['price'].rolling(window=n).max()
    df['min'] = df['price'].rolling(window=n).min()
    
    nvol = size_vol
    df['volmax'] = df['max'].rolling(window =nvol).std()
    df['volmin'] = df['min'].rolling(window =nvol).std()
    
    return None


#%%
df_1 = get_data(session,1000,'BTCUSDT',5)
df_2 = get_data(session,1000,'BTCUSDT',5)
df = df_1
#df['price']= df_1['price']/df_2['price']



#%%

maxPerf = 0

for i in range(12,120,4):
    for k in range(12,120,4):
        traitement_data(df, i, k)
        
        position = 0
        L_position = []
        L_portefeuille=[]
        Portefeuille =0


        for j in range(len(df)-700,len(df)-350):
            Portefeuille += position*(df['price'][j]-df['price'][j-1])
            pos_prec = position

            position = -np.sign(df['volmax'][j]-df['volmin'][j]) 
            
            Portefeuille += -(7/10000)*abs(position-pos_prec)*df['price'][i]
        if Portefeuille>maxPerf :
            maxPerf = Portefeuille
            max_indice = (i,k)
            pos_final_max = position

#%%

traitement_data(df, max_indice[0], max_indice[1])
position = 0
L_position = []
L_portefeuille=[]
Portefeuille =0


for i in range(len(df)-700,len(df)-200):
    Portefeuille += position*(df['price'][i]-df['price'][i-1])
    pos_prec = position

    position = -np.sign(df['volmax'][i]-df['volmin'][i]) 
    
    Portefeuille += -(7/10000)*abs(position-pos_prec)*df['price'][i]
    L_portefeuille.append(Portefeuille)
    L_position.append(position)            


#%%
plt.plot(L_portefeuille) 
plt.grid() 
plt.show()   


#%%
traitement_data(df, 60, 24)
p = 0
LP = []
LPos = []
P = 0

pos_max_final = 0

for a in range(400,len(df)):
    
    P += p*(df['price'][a]-df['price'][a-3])
    pp = p
    
    
    if a%12 == 0 :
        
        dff = df.iloc[:a]
        maxPerf = 0
        
        for i in range(12, 120, 4):
            for k in range(12, 120, 4):
                traitement_data(dff, i, k)
                
                position = 0
                L_position = []
                L_portefeuille = []
                Portefeuille = 0
                
                for j in range(len(dff) - 48, len(dff)):
                    Portefeuille += position * (dff['price'][j] - dff['price'][j - 1])
                    pos_prec = position
                    
                    position = -np.sign(dff['volmax'][j] - dff['volmin'][j])
                    
                    Portefeuille += -(7 / 10000) * abs(position - pos_prec) * dff['price'][i]
                    if Portefeuille > maxPerf:
                        maxPerf = Portefeuille
                        max_indice = (i, k)
                        pos_final_max = position
        traitement_data(df, max_indice[0], max_indice[1])
        print(max_indice)
    p = -np.sign(df['volmax'][a]-df['volmin'][a])
    P +=-(7 / 10000) * abs(p - pp) * df['price'][a]
    LP.append(P)
    LPos.append(p)
    
    
    
#%%
plt.plot(LP)

plt.show()    
    
    
    
    
    
    
    
    
    
    
    
    





