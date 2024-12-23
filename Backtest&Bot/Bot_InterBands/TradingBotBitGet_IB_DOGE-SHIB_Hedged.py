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


def traitement_data(df):
    df['ma_LT']=df['price'].rolling(window = 160).mean()
    df['ma_ST']= df['price'].rolling(window = 100).mean()
    df['ma_denoise']=df['price'].rolling(window = 20).mean()
    return None

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

crypto1 = 'DOGEUSDT'
crypto2 = 'SHIBUSDT'

size_batch = 400  #taille de la position de base pour les trades 

#%% Procédure de trading

# renvoie la nouvelle position à prendre
def Trading_Step():
    df_1 = get_data(200, crypto1)
    df_2 = get_data(200,crypto2)
    
    df = df_1
    df['price'] =df_1['price']/df_2['price']
    
    
    traitement_data(df)
    time.sleep(1)
    prix_LT =df['ma_LT'][199]
    prix_ST = df['ma_ST'][199]
    # Position de la première stratégie
    prix = df['ma_denoise'][199]
    if (prix_LT>prix_ST):
        if (prix_ST>prix) :
            position = -3
        if prix>prix_LT :
            position = 3
        if ((prix>prix_ST) and (prix<prix_LT)) :
            position = -1
    else :
        if prix>prix_ST :
            position = 3
        if prix<prix_LT:
            position = -3
        if ((prix<prix_ST) and (prix>prix_LT)):
            position = 1
    
    position1 = position
    
    # Position de la deuxème stratégie
    prix = df['price'][199]
    if (prix_LT>prix_ST):
        if (prix_ST>prix) :
            position = -3
        if prix>prix_LT :
            position = 3
        if ((prix>prix_ST) and (prix<prix_LT)) :
            position = -1
    else :
        if prix>prix_ST :
            position = 3
        if prix<prix_LT:
            position = -3
        if ((prix<prix_ST) and (prix>prix_LT)):
            position = 1
    return (position1-position)

#%%
# Initialisation du portefeuille
L_Portefeuille=[get_total_equity()] 
L_position = [get_Position_Info(crypto1)/size_batch]

#%%

last_hour = int(get_data(1,crypto1)["time"][0])
chrono = (get_time() - last_hour)/60000 # nombre de minute depuis la derniere bougie
time.sleep(1)


while True :
    try :
        chrono =(get_time() - last_hour)/60000 # nombre de minute depuis la derniere bougie
        print(round(100*(chrono/60),2), '%')
        time.sleep(1)
        if (chrono> 60): # attend 60min
            try :
                pos = Trading_Step()
                time.sleep(1)
                
                prix1 = get_last_Price(crypto1)
                prix2 = get_last_Price(crypto2)
                time.sleep(1)
                
                Doge_pos = get_Position_Info(crypto1)
                Shib_pos = get_Position_Info(crypto2)
                print('Current Position : ', Doge_pos/size_batch)
                time.sleep(1)
                
                if (Doge_pos!=(pos*size_batch)):
                    try:
                        market_order(crypto1, round((pos*size_batch)-Doge_pos))
                        time.sleep(1)
                        newShib_pos = -pos*size_batch*prix1/prix2
                        market_order(crypto2, round(newShib_pos-Shib_pos)) 
                        print("WIF Position Changed from ", Doge_pos,"to", (pos*size_batch))
                        print("SHIB Position Changed from ", Shib_pos,"to", round(newShib_pos))
                    except:
                        print("Problem with market orders")
                else : 
                    print("Position Unchanged")
            except : 
                print("Problem Happened with Trading Step")
            
            time.sleep(1)
            last_hour = int(get_data(1,crypto1)["time"][0])
            time.sleep(1)
            L_Portefeuille.append(get_total_equity())
            time.sleep(1)
            L_position.append(pos)
    except:
        print("Problem  with the Trading procedure")
    time.sleep(25.2)





