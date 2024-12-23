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

inter =60
df_1 = get_data(session,1000,'SANDUSDT',inter)
df_2 = get_data(session,1000,'MANAUSDT',inter)
df_3 = get_data(session,1000,'CAKEUSDT',inter)
#df_4 = get_data(session,1000,'GMTUSDT',inter)


#%%
plt.plot(df_1['price']/df_1['price'][0])
plt.plot(df_2['price']/df_2['price'][0], label ="Mana")
plt.plot(df_3['price']/df_3['price'][0], label = "Sand")
#plt.plot(df_4['price']/df_4['price'][0], label ="Axs")
plt.legend()
plt.grid()
plt.show()


#%% Test de regression linéaire
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
#%%
data = {
    'Prix_1': df_2['price'].values,
    'Prix_2': df_3['price'].values,
    #'Prix_3': df_4['price'].values,
    'Prix_4': df_1['price'].values,
    #'Prix_Cible': [1 for i in range(len(df_2))] # Variable cible
}

df = pd.DataFrame(data)
#%%
# 3. Définir les variables explicatives (X) et la variable à prédire (y)
X = df[[ 'Prix_2','Prix_4']]  # Les prix des 3 actifs
y = df['Prix_1']  # La variable cible (prix à prédire)

# 4. Créer le modèle de régression linéaire
model = LinearRegression()

# 5. Ajuster le modèle aux données (entraîner le modèle)
model.fit(X, y)
#%%
# 6. Faire des prédictions
y_pred = model.predict(X)

# 7. Afficher les coefficients du modèle
print("Coefficients du modèle : ", model.coef_)
print("Intercept : ", model.intercept_)
#%%
# 8. Évaluer le modèle
mse = mean_squared_error(y, y_pred)
r2 = r2_score(y, y_pred)
print(f"Erreur quadratique moyenne (MSE) : {mse}")
print(f"Coefficient de détermination (R^2) : {r2}")
#%%
# 9. Optionnel : Visualiser les résultats
plt.scatter(y, y_pred)
plt.plot([min(y), max(y)], [min(y_pred), max(y_pred)], color='red')  # Ligne de régression
plt.xlabel('Prix Cible Réel')
plt.ylabel('Prix Cible Prédit')
plt.title('Régression linéaire : Prix Réel vs Prédit')
plt.show()

#%%
res = model.coef_[0]*df_3['price'].values + model.coef_[1]*df_1['price'].values -df_2['price'].values
#res = model.coef_[0]*df_4['price'].values + model.coef_[1]*df_3['price'].values + model.coef_[2]*df_1['price'].values -df_2['price'].values
#res1 = 0.01*df_4['price'].values -0.7*df_3['price'].values -df_2['price'].values
plt.plot(res)
#plt.plot(res1)
#plt.plot(df_2['price'].values)
plt.grid()
plt.show()


###############################################################################
#%% Strategie de trading

def traitement_data(df):
    df['ma']=df['price'].rolling(window = 5).mean()
    df['std'] = df['price'].rolling(window = 80).std()
    
    
    len_deriv = 25 # longueur de l'interpolation des dérivées premières
    x= np.array([i for i in range(len_deriv)])
    deriv_LT = []
    
    for i in range(len_deriv+100,len(df)):
        seq_LT = df['price'][i-len_deriv:i].values
        
        a_LT = np.polyfit(x,seq_LT,1)
       
        deriv_LT.append(a_LT[0])
        
        
    df['deriv'] = np.concatenate((np.zeros(125)*np.nan, deriv_LT))
    
    deriv_LT = []
    for i in range(len_deriv+100,len(df)):
        seq_LT = df['ma'][i-len_deriv:i].values
        
        a_LT = np.polyfit(x,seq_LT,1)
       
        deriv_LT.append(a_LT[0])
        
        
    df['deriv_ma'] = np.concatenate((np.zeros(125)*np.nan, deriv_LT))
    return None



#%%

trading = pd.DataFrame(res, columns=['price'])
traitement_data(trading)

plt.plot(trading['price'])
plt.plot(trading['ma'])
#plt.plot(trading['ma']+2*trading['std'])
plt.grid()
plt.show()

#%%

position = 0
L_position = []
L_portefeuille=[]
Portefeuille =0



for i in range(200,len(df)):
    Portefeuille += position*(trading['price'][i]-trading['price'][i-1])
    prix =trading['deriv'][i]
    
    pos_prec = position
    position1 = - np.sign(prix) #* (abs(prix)>(10**(-4)))
    
    prix =trading['deriv_ma'][i]
    
    pos_prec = position
    position2 = - np.sign(prix)
    
    position = position2
    #position *=(df['deriv_100'][i]*position>0)
    Portefeuille += -(20/10000)*abs(position-pos_prec)*abs(trading['price'][i])
    L_portefeuille.append(Portefeuille)
    L_position.append(position)


#%%
plt.plot(L_portefeuille) 
plt.grid() 
plt.show()
