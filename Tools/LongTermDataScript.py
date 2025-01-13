import numpy as np
from pybit.unified_trading import HTTP
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt

#%%
def get_data(session, n, nom_crypto, intervale, time): 
    res = (session.get_mark_price_kline(
        category="linear",
        symbol=nom_crypto,
        interval=intervale,
        endTime=time,
        limit=n,
    ))['result']['list']
    
    # Création du DataFrame avec les colonnes renommées
    df = (
        pd.DataFrame(res, columns=['time', 'openPrice', 'high', 'low', 'closePrice'])
        .iloc[::-1]
        .reset_index(drop=True)
    )
    
    # Conversion des colonnes en types appropriés
    df['openPrice'] = df['openPrice'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['closePrice'] = df['closePrice'].astype(float)
    #df['time'] = df['time'].astype(float)

    return df

session = HTTP(testnet=False)


#%%
def get_historical_data(session, n, nom_crypto, intervale, start_time, num_batches):
    
    all_data = []  # Liste pour stocker tous les DataFrames
    end_time = start_time  # Initialiser endTime au point de départ donné

    for i in range(num_batches):
        # Récupérer les données pour ce lot
        print(f"Fetching batch {i+1}/{num_batches} ending at {end_time}")
        batch_data = get_data(session, n, nom_crypto, intervale, end_time)
        
        # Ajouter les données à la liste
        all_data.append(batch_data)
        
        # Mettre à jour endTime pour remonter dans le passé
        end_time = batch_data['time'].iloc[0]   # Prend le dernier timestamp et le diminue de 1

    # Concaténer tous les DataFrames dans un seul DataFrame
    result = pd.concat(all_data, axis=0).reset_index(drop=True)
    res = result.sort_values(by='time').drop_duplicates(subset='time').reset_index(drop=True)
    return res

#%%

df = get_historical_data(session, 1000, 'DOGEUSDT', 5, 1736425800000 , 10)
