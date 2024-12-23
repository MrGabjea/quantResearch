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

df = get_data(session, 1000, 'DOGEUSDT',15)

#%%

count = 0


for i in range(len(df)):
    count += ((df['openPrice'][i]*(1+0.0004))<df['high'][i] ) and ((df['openPrice'][i]*(1-0.0004))>df['low'][i] ) 
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

List_wait =[]
Sell_order = []
Buy_order = []

for i in range(len(df)):
    if df['MM'][i] : Portefeuille +=(2*n-0.0004)*df['openPrice'][i]

    else : 
        if df['high'][i]<(df['openPrice'][i]*(1+n)) : Sell_order.append((df['openPrice'][i]*(1+n),1))
        if df['low'][i]>(df['openPrice'][i]*(1-n)) : Buy_order.append((df['openPrice'][i]*(1-n),1))
    
    L_bo = []
    for bo in Buy_order : 
        if df['low'][i]< bo[0] : 
            Portefeuille+=(2*n-0.0004)*bo[0]/(1-n)
            List_wait.append(bo[1])
        else: 
            
            
            L_bo.append((bo[0],bo[1]+1))
    Buy_order = L_bo
    
    L_so = []
    for so in Sell_order : 
        if df['high'][i]> so[0] : 
            Portefeuille+=(2*n-0.0004)*so[0]/(1-n)
            List_wait.append(so[1])
        else: L_so.append((so[0],so[1]+1))
    Sell_order = L_so
    
           
    L_portefeuille.append(Portefeuille)
#%%

plt.plot(L_portefeuille)
plt.show()
    

    
#%%
    
def compter_apparitions(liste):
    # Trouver la valeur maximale dans la liste
    max_val = max(liste) if liste else 0

    # Créer une liste de compteurs initialisée à zéro
    compteurs = [0] * (max_val + 1)

    # Compter les apparitions
    for val in liste:
        compteurs[val] += 1

    return compteurs

def tracer_histogramme(compteurs):
    valeurs = list(range(len(compteurs)))  # Les indices représentent les valeurs
    plt.bar(valeurs, compteurs, color='skyblue', edgecolor='black')  # Tracer un histogramme
    plt.xlabel("Valeurs")
    plt.ylabel("Nombre d'apparitions")
    plt.title("Histogramme des apparitions")
    plt.xticks(valeurs)  # Afficher tous les indices sur l'axe des x
    plt.grid(axis='y', linestyle='--', alpha=0.7)  # Ajouter une grille pour l'axe Y
    plt.show()
    
#%%
L= compter_apparitions(List_wait)
L= np.array(L)/len(L)
#%%
tracer_histogramme(L)
