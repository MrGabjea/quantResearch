import requests
import time
import numpy as np
import pandas as pd
import hmac
import hashlib
import json
import base64


# Clés API
api_key = 'bg_669bde1227d59de7a29045ddd94398c4'
secret_key = 'df592a14c15d7b48832731745ed4de25e608ef19ddc2d7c1a4ac1e1186c8fa10'
passphrase = 'KangouQuant07'

######################################################################################################################
#%%      DEF FONCTIONS : PARTIE OBTENTION DONNEES

def get_data(n_periode, nom_crypto): # n_periode max: 200, la longueur de l'intervalle est à changer dans le corps de la fonction
    # URL de l'API Bitget
    base_url = 'https://api.bitget.com/api/v2/mix/market/candles'
    # Paramètres de la requête
    params = {
    'symbol': nom_crypto,
    'productType': 'usdt-futures',
    'granularity': '5m',
    'limit': n_periode  # Limite de chandeliers à récupérer
    }
    # Faire la requête GET
    response = requests.get(base_url, params=params)
    # Vérifier le statut de la réponse
    if (response.status_code == 200):
        data = np.array( response.json()['data'])[:,:5]
        df = pd.DataFrame(data,columns=['time', 'openPrice','high','low','closePrice'])
        df = df.astype(float)
        return(df)
    else:
        print(f"Erreur: {response.status_code}")
        print(response.text)

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


######################################################################################################################
#%%     DEF FONCTIONS :  PARTIE GESTION COMPTE

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
#%%     DEF FONCTIONS :  PARTIE GESTION ORDRE

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
def limit_order(nom_crypto, qty, limit):    
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
        'price' : limit,
        'side': sens,
        'orderType': 'limit',
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
def set_sl(nom_crypto,qty,limit):
    # URL de l'API Bitget
    url = 'https://api.bitget.com/api/v2/mix/order/place-tpsl-order'
    
    # Détermination du sens du trade
    sens = 'buy' if qty > 0 else 'sell'
    
    # Paramètres de la requête
    timestamp = str(int(time.time() * 1000))
    method = 'POST'
    request_path = '/api/v2/mix/order/place-tpsl-order'
    body = json.dumps({
        'symbol': nom_crypto,
        'productType': 'USDT-FUTURES',
        'marginMode': 'crossed',
        'marginCoin': 'USDT',
        'planType': 'loss_plan',
        'triggerPrice': limit,
        'holdSide': sens,  
        'size': str(abs(qty)), 
        'clientOid': str(int(time.time() * 1000))  # ID unique
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
def set_tp(nom_crypto,qty,limit):
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
        'price' : limit,
        'side': sens,
        'orderType': 'limit',
        'reduceOnly': 'YES',
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
def pending_order():
    # URL de l'API Bitget
    base_url = 'https://api.bitget.com'
    endpoint = '/api/v2/mix/order/orders-pending'
    
    # Paramètres de la requête
    params = {
        'productType': 'usdt-futures'
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
        data = response.json()['data']['entrustedList']  # Si la réponse est en JSON 
        return (data if data is not None else [])
    else:
        print(f"Erreur: {response.status_code}")
        print(response.text)
    return None
 
   
#______________________________________________________________________________
def cancel_order(nom_crypto,clientOid): # clientOid correspond à l'ID de l'ordre à cancel
   # URL de l'API Bitget
   url = 'https://api.bitget.com/api/v2/mix/order/cancel-order'
   
   
   # Paramètres de la requête
   timestamp = str(int(time.time() * 1000))
   method = 'POST'
   request_path = '/api/v2/mix/order/cancel-order'
   body = json.dumps({
       'symbol': nom_crypto ,
       'productType': 'usdt-futures',
       'clientOid': str(clientOid)  # ID de commande unique   
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
   return None

#______________________________________________________________________________
def cancel_all_order():
    List_order = pending_order()
    
    for order in List_order:
        ID,name = int(order['clientOid']),order['symbol']
        cancel_order(name,ID) 
    return None