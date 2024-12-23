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
    df = (pd.DataFrame(res, columns=['time', 'openPrice', 'C', 'D','closePrice'])[['time', 'openPrice']]).iloc[::-1].reset_index(drop=True)
    df['openPrice'] = df['openPrice'].astype(float)
    df = df.rename(columns={'openPrice': 'price'})
    return(df)

#%%
def traitement_data(df):
    df['logR'] = np.log(df['price']/df['price'].shift(1))
#%%

df1 = get_data(session,1000,'ETHUSDT',15)
df2 = get_data(session,1000,'BTCUSDT',15)
traitement_data(df1)
traitement_data(df2)
#%%
df = pd.DataFrame(df1['price']/df2['price'])
df.columns = ['price']

n=1*1
df['min'] = df['price'].rolling(window = n).min()
df['max'] = df['price'].rolling(window = n).max()

df_sampled = df.iloc[::n].reset_index(drop=True)
#%%

plt.plot(df_sampled['price'])
plt.plot(df_sampled['min'])
plt.plot(df_sampled['max'])
plt.grid()
plt.show()

#%%

correlation_matrix = np.corrcoef(df1['logR'][1:],df2['logR'][1:])[0,1]

#%%
plt.plot(df1['price']/df1['price'][0])
plt.plot(df2['price']/df2['price'][0])
plt.grid()
plt.show()
#%%
plt.plot(df['price'])
plt.grid()
plt.show()

#%%
pos1 = 1/df1['price'][0]
pos2 = 1/df2['price'][0]

plt.plot(df1['price']*pos1 - df2['price']*pos2)
plt.grid()
plt.show()


