import requests
import time
import numpy as np
import pandas as pd
import hmac
import hashlib
import json
import base64


# Clés API
api_key = ''
secret_key = ''
passphrase = ''

######################################################################################################################
#%%      DEF FONCTIONS : PARTIE DATA

def get_data(n_periode, nom_crypto): # n_periode max: 200, la longueur de l'intervalle est à changer dans le corps de la fonction
    # URL de l'API Bitget
    base_url = 'https://api.bitget.com/api/v2/mix/market/candles'
    # Paramètres de la requête
    params = {
    'symbol': nom_crypto,
    'productType': 'usdt-futures',
    'granularity': '1H',
    'limit': n_periode  # Limite de chandeliers à récupérer
    }
    # Faire la requête GET
    response = requests.get(base_url, params=params)
    # Vérifier le statut de la réponse
    if (response.status_code == 200):
        data = np.array( response.json()['data'])[:,:2]
        df = pd.DataFrame(data, columns=['time', 'price'])
        df['price'] = df['price'].astype(float)
        return(df)
    else:
        print(f"Erreur: {response.status_code}")
        print(response.text)

def get_data2(n_periode, nom_crypto): # n_periode max: 200, la longueur de l'intervalle est à changer dans le corps de la fonction
    # URL de l'API Bitget
    base_url = 'https://api.bitget.com/api/v2/mix/market/candles'
    # Paramètres de la requête
    params = {
    'symbol': nom_crypto,
    'productType': 'usdt-futures',
    'granularity': '2H',
    'limit': n_periode  # Limite de chandeliers à récupérer
    }
    # Faire la requête GET
    response = requests.get(base_url, params=params)
    # Vérifier le statut de la réponse
    if (response.status_code == 200):
        data = np.array( response.json()['data'])[:,:2]
        df = pd.DataFrame(data, columns=['time', 'price'])
        df['price'] = df['price'].astype(float)
        return(df)
    else:
        print(f"Erreur: {response.status_code}")
        print(response.text)

def get_data30m(n_periode, nom_crypto): # n_periode max: 200, la longueur de l'intervalle est à changer dans le corps de la fonction
    # URL de l'API Bitget
    base_url = 'https://api.bitget.com/api/v2/mix/market/candles'
    # Paramètres de la requête
    params = {
    'symbol': nom_crypto,
    'productType': 'usdt-futures',
    'granularity': '30m',
    'limit': n_periode  # Limite de chandeliers à récupérer
    }
    # Faire la requête GET
    response = requests.get(base_url, params=params)
    # Vérifier le statut de la réponse
    if (response.status_code == 200):
        data = np.array( response.json()['data'])[:,:2]
        df = pd.DataFrame(data, columns=['time', 'price'])
        df['price'] = df['price'].astype(float)
        return(df)
    else:
        print(f"Erreur: {response.status_code}")
        print(response.text)

def deriv_poly(L,size):
    x=np.array([-size+i+1 for i in range(size)])
    P = np.polyfit(x, L[-size:], 3)
    return(P[2])
######################################################################################################################
#%%     DEF FONCTIONS :  PARTIE TRADING

#fonction pour créer les signatures pour l'envoi de requête
def create_signature(secret_key, timestamp, method, request_path, query_string='', body=''):
    # Construit le message à signer
    if query_string:
        message = f'{timestamp}{method}{request_path}?{query_string}{body}'
    else:
        message = f'{timestamp}{method}{request_path}{body}'

    # Calcule la signature HMAC SHA256
    signature = hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).digest()

    # Encode la signature en base64
    signature_base64 = base64.b64encode(signature).decode()

    return signature_base64

#______________________________________________________________________________

def get_last_Price(nom_crypto):
    base_url = 'https://api.bitget.com/api/v2/mix/market/candles'

    # Paramètres de la requête
    params = {
    'symbol': nom_crypto,
    'productType': 'usdt-futures',
    'granularity': '1m',
    'limit': 1  
    }
    response = requests.get(base_url, params=params)
    # Vérifier le statut de la réponse
    if (response.status_code == 200):
        data = response.json()['data'][0][1]
        return(float(data))
 
#______________________________________________________________________________

def get_time():
    url = "https://api.bitget.com/api/spot/v1/public/time"
    # Effectuer une requête GET à l'API
    response = requests.get(url)
    # Vérifier si la requête a été effectuée avec succès
    if response.status_code == 200:
        # Extraire les données JSON de la réponse
        data = response.json()
        # Obtenir l'heure du serveur en millisecondes
        time_ms = data['data']
        return(int(time_ms))
    else:
        print(f"Échec de la requête, code d'erreur : {response.status_code}")
        
#______________________________________________________________________________
        
def market_order(nom_crypto, qty):
    # URL de l'API Bitget
    url = 'https://api.bitget.com/api/v2/mix/order/place-order'
    
    # Détermination du sens du trade
    sens = 'buy' if qty > 0 else 'sell'
    
    # Paramètres de la requête
    timestamp = str(int(time.time() * 1000))
    method = 'POST'
    request_path = '/api/v2/mix/order/place-order'
    body = json.dumps({
        'symbol': nom_crypto,
        'productType': 'usdt-futures',
        'marginMode': 'crossed',
        'marginCoin': 'USDT',
        'size': str(abs(qty)),
        'side': sens,
        'orderType': 'market',
        'clientOid': str(int(time.time() * 1000))  # ID de commande unique
    })
    
    # En-têtes de la requête
    headers = {
        'Content-Type': 'application/json',
        'ACCESS-KEY': api_key,
        'ACCESS-SIGN': create_signature(secret_key, timestamp, method, request_path, body=body),
        'ACCESS-TIMESTAMP': timestamp,
        'ACCESS-PASSPHRASE': passphrase,
        'locale': 'en-US'
    }
    
    # Envoi de la requête
    response = requests.post(url, headers=headers, data=body)
    
    # Gestion de la réponse
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur: {response.status_code}")
        print(response.text)
        return None

#______________________________________________________________________________

def get_Position_Info(nom_crypto):
    # URL de l'API Bitget
    base_url = 'https://api.bitget.com'
    endpoint = '/api/v2/mix/position/single-position'
    
    # Paramètres de la requête
    params = {
        'symbol': nom_crypto,
        'productType': 'usdt-futures',
        'marginCoin': 'USDT'
        }
    
    # Convertir les paramètres en query string
    query_string = '&'.join([f'{key}={value}' for key, value in params.items()])
    
    # Construire l'URL complète avec les paramètres
    url = f'{base_url}{endpoint}?{query_string}'
    
    # Informations pour l'authentification
    timestamp = str(int(time.time() * 1000))
    method = 'GET'
    request_path = f'{endpoint}'
    body = ''  # Le corps de la requête est vide pour une requête GET
    
    # En-têtes de la requête
    headers = {
        'Content-Type': 'application/json',
        'ACCESS-KEY': api_key,
        'ACCESS-SIGN': create_signature(secret_key, timestamp, method, request_path, query_string, body),
        'ACCESS-TIMESTAMP': timestamp,
        'ACCESS-PASSPHRASE': passphrase,
        'locale': 'en-US'
        } 
    # Envoyer la requête GET
    response = requests.get(url, headers=headers)      
    
    if response.status_code == 200:
        data = response.json()['data']  # Si la réponse est en JSON
        if (data ==[]):
            return(0) #pas de position
        else:
            sens = 2*(data[0]['holdSide'] == 'long')-1
            return (sens*float(data[0]['total']))
    else:
        print(f"Erreur: {response.status_code}")
        print(response.text)
        return None

#______________________________________________________________________________
    
    
def get_total_equity():
    # URL de l'API Bitget
    base_url = 'https://api.bitget.com'
    endpoint = '/api/v2/mix/account/account'
    
    # Paramètres de la requête
    params = {
        'symbol': 'btcusdt',
        'productType': 'USDT-FUTURES',
        'marginCoin': 'usdt'
    }
    
    # Convertir les paramètres en query string
    query_string = '&'.join([f'{key}={value}' for key, value in params.items()])
    
    # Construire l'URL complète avec les paramètres
    url = f'{base_url}{endpoint}?{query_string}'
    
    # Informations pour l'authentification
    timestamp = str(int(time.time() * 1000))
    method = 'GET'
    request_path = endpoint
    body = ''  # Le corps de la requête est vide pour une requête GET
    
    # En-têtes de la requête
    headers = {
        'Content-Type': 'application/json',
        'ACCESS-KEY': api_key,
        'ACCESS-SIGN': create_signature(secret_key, timestamp, method, request_path, query_string, body),
        'ACCESS-TIMESTAMP': timestamp,
        'ACCESS-PASSPHRASE': passphrase,
        'locale': 'en-US'
    }
    
    # Envoyer la requête GET
    response = requests.get(url, headers=headers)
    
    # Gestion de la réponse
    if response.status_code == 200:
        return(float(response.json()['data']['usdtEquity']))
    else:
        print(f"Erreur: {response.status_code}")
        print(response.text)
        return None

    
######################################################################################################################
######################################################################################################################
######################################################################################################################
#%%                   IMPLEMENTATION STRATEGIE DE TRADING


# Initialisation des parametres du bot 

crypto = 'BTCUSDT'
size_batch = 0.02  #taille de la position de base pour les trades 


#%% Procédure de trading

# renvoie la nouvelle position à prendre

# Procédure de trading pour BTC
def Trading_Step():
    df = get_data(200, crypto)
    time.sleep(1)
    df2 = get_data2(200, crypto)
    time.sleep(1)
    df30m = get_data30m(200, crypto)
    
    count30m = 0
    for k in range(80,120):
        count30m += np.sign(deriv_poly(df30m['price'].values[-k:],k))
    
    count2 = 0
    for k in range(20,30):
        count2 += np.sign(deriv_poly(df2['price'].values[-k:],k))
    
    count = 0
    for k in range(40,60):
        count += np.sign(deriv_poly(df['price'].values[-k:],k))
     
    position = np.sign(count) + np.sign(count2) + np.sign(count30m)
    return (position)


#%%
# Initialisation du portefeuille
L_Portefeuille=[get_total_equity()] 
L_position = [get_Position_Info(crypto)/size_batch]


#%%

last_hour = int(get_data(1,crypto)["time"][0])
chrono = (get_time() - last_hour)/60000 # nombre de minute depuis la derniere bougie
time.sleep(1)


while True :
    try:
        chrono =(get_time() - last_hour)/60000 # nombre de minute depuis la derniere bougie
        print(round(100*(chrono/60),2), '%')
        time.sleep(1)
        if (chrono> 60): # attend 60min
            
            #partie BTC
            pos_prev = get_Position_Info(crypto)
            try : 
                pos = round(Trading_Step()*size_batch,3)
                time.sleep(1)
                print('Current Position BTC: ', round(pos_prev/size_batch,3))
            except:
                print("Problem Happened with position update")
            if (pos_prev!=pos):
                try:
                    market_order(crypto, round((pos-pos_prev),3))
                except :
                    print("Problem Happened with market order")
                print("Position Updated :", pos_prev, "to", pos)
            else : 
                print("Position Unchanged")
            
            time.sleep(1)
            
            
            time.sleep(1)
            last_hour = int(get_data(1,crypto)["time"][0])
            time.sleep(1)
            L_Portefeuille.append(get_total_equity())
            time.sleep(1)
            L_position.append(pos/size_batch)
            time.sleep(1)
    except:
        print("Problem with the trading procedure")
    time.sleep(32.8)



#%%
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
#%% Enregistrement données

Historique_Portefeuille = pd.DataFrame(L_Portefeuille,columns = ['AUM'])
Historique_Portefeuille.to_csv('P:/TradingBot/TradingBot_Polynome/Performance_Poly.csv', mode='a', header=False, index=False)

