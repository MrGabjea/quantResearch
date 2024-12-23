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
    df['ewm_price'] = df['price'].ewm(span=100, adjust=False).mean()
    df['ma150']=df['price'].rolling(window = 4).mean()
    df['ma100']=df['price'].rolling(window =100).mean()
    df['ma20']= df['price'].rolling(window =80).mean()
    df['std'] = df['price'].rolling(window = 30).std()
    len_deriv = 5 # longueur de l'interpolation des dérivées premières
    x= np.array([i for i in range(len_deriv)])
    deriv_LT = []
    
    for i in range(len_deriv+200,len(df)):
        seq_LT = df['ma100'][i-len_deriv:i].values
        
        a_LT = np.polyfit(x,seq_LT,1)
       
        deriv_LT.append(a_LT[0])
        
        
    df['deriv_100'] = np.concatenate( (np.zeros(205)*np.nan, deriv_LT))
    
    df['logR'] = np.log(df['price']/df['price'].shift(1))
    df['vol'] = df['logR'].rolling(window =15).std()
    n = 15
    df['volkinj']= 0.5*(df['vol'].rolling(window=n).max() +  df['vol'].rolling(window=n).min())
    return None
#%%
df_1 = get_data(session,1000,'BTCUSDT',120)
df_2 = get_data(session,1000,'ETHUSDT',240)
df = df_1
#df['price']= df_1['price']/df_2['price']
#%%
traitement_data(df)
#%%
plt.plot(df['price'])
plt.plot(df['ewm_price'])
plt.plot( df['ma150'],label='ma150')
plt.plot( df['ma100'],label='ma100')
#plt.plot( df['ma20'],label='ma20')
#plt.plot( df['ma100']+1*df['std'], label='ma20')
#plt.plot( df['ma100']-1*df['std'], label='ma20')
plt.grid()
plt.legend()
plt.show()
    
#%%
plt.plot(df['volkinj'])
plt.plot(df['vol'])
plt.grid()
plt.show()
    


#%%

position = 0
L_position = []
L_portefeuille=[]
Portefeuille =0



for i in range(150,len(df)):
    Portefeuille += position*(df['price'][i]-df['price'][i-1])
    prix_100 =df['ma100'][i]
    prix_20 = df['ma20'][i]
    prix = df['ma150'][i]
    pos_prec = position
    if (prix_100>prix_20):
        if (prix_20>prix) :
            position = -3
        if prix>prix_100 :
            position = 3
        if ((prix>prix_20) and (prix<prix_100)) :
            position = -1
    else :
        if prix>prix_20 :
            position = 3
        if prix<prix_100:
            position = -3
        if ((prix<prix_20) and (prix>prix_100)):
            position = 1
    #position *=(df['deriv_100'][i]*position>0)
    Portefeuille += -(13/10000)*abs(position-pos_prec)*df['price'][i]
    L_portefeuille.append(Portefeuille)
    L_position.append(position)

#%%
plt.plot(L_portefeuille) 
plt.grid() 
plt.show()
#%%
L= L_portefeuille
#%%
plt.plot(np.array(L_portefeuille)-np.array(L))
#plt.plot(L)
plt.grid() 
plt.show()
#%%
correlation = df_1['price'].corr(df_2['price'])
print(f"La corrélation entre les crypto est de : {correlation}")
#%%
def compte(n,L):
    count = 0
    for i in L:
        if i<n :
            count +=1
    return count
#%% Test avec prise en compte du hedging
position = 0
L_position = []
L_portefeuille=[]
Portefeuille =0



for i in range(100,len(df)):
    Portefeuille += position*(df['price'][i]-df['price'][i-1])
    prix_100 =df['ma100'][i]
    prix_20 = df['ma20'][i]
    prix = df['ma150'][i]
    pos_prec = position
    if (prix_100>prix_20):
        if (prix_20>prix) :
            position = -1
        if prix>prix_100 :
            position = 1
        if ((prix>prix_20) and (prix<prix_100)) :
            position = -0
    else :
        if prix>prix_20 :
            position = 1
        if prix<prix_100:
            position = -1
        if ((prix<prix_20) and (prix>prix_100)):
            position = 0
    #position *=(df['deriv_100'][i]*position>0)
    p1 = position
    prix = df['price'][i]
    if (prix_100>prix_20):
        if (prix_20>prix) :
            position = -3
        if prix>prix_100 :
            position = 3
        if ((prix>prix_20) and (prix<prix_100)) :
            position = -1
    else :
        if prix>prix_20 :
            position = 3
        if prix<prix_100:
            position = -3
        if ((prix<prix_20) and (prix>prix_100)):
            position = 1
    
    test = compte(df['std'][i],df['std'][i-20:i])/20
    
    position = (test>0.5)*p1#- position
    
    Portefeuille += -(7/10000)*abs(position-pos_prec)*df['price'][i]
    L_portefeuille.append(Portefeuille)
    L_position.append(position)


#%%
plt.plot(L_portefeuille) 
plt.grid() 
plt.show()

#%%
def max_drawdown(L_portefeuille):
    if len(L_portefeuille) == 0:
        return 0  # Si la liste est vide, le max drawdown est 0

    # Initialiser les variables pour stocker le maximum et le drawdown maximum
    max_so_far = L_portefeuille[0]
    max_drawdown = 0
    
    # Parcourir la liste des valeurs du portefeuille
    for value in L_portefeuille:
        # Mettre à jour le sommet maximum atteint
        if value > max_so_far:
            max_so_far = value
        
        # Vérifier que max_so_far n'est pas zéro avant de calculer le drawdown
        if max_so_far != 0:
            drawdown = (max_so_far - value) 
        else:
            drawdown = 0  # Si max_so_far est zéro, le drawdown est nul
        
        # Mettre à jour le drawdown maximum si on trouve un plus grand drawdown
        if drawdown > max_drawdown:
            max_drawdown = drawdown
            
    return max_drawdown

#%%
max_drawdown(L_portefeuille)










