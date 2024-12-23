import numpy as np
from pybit.unified_trading import HTTP
import pandas as pd
import numpy as np
import time

######################################################################################################################
#%%      DEF FONCTIONS : PARTIE DATA

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


def traitement_data(df): # exemple de traitement de données 
    df['ma100']=df['price'].rolling(window = 100).mean()
    df['ma150']=df['price'].rolling(window = 150).mean()
    df['ma50']= df['price'].rolling(window = 50).mean()
    len_deriv = 5 # longueur de l'interpolation
    x= np.array([i for i in range(len_deriv)])
    deriv200 =[]
    deriv20 = []
    for i in range(len_deriv+200,len(df)):
        seq200 = df['ma150'][i-len_deriv:i].values
        seq20 =df['ma100'][i-len_deriv:i].values
        a200 = np.polyfit(x,seq200,1)
        a20 = np.polyfit(x,seq20,1)
        deriv200.append(a200[0])
        deriv20.append(a20[0])
    df['deriv150'] = np.concatenate( (np.zeros(205)*np.nan, deriv200))
    df['deriv100'] = np.concatenate( (np.zeros(205)*np.nan, deriv20))
    return

######################################################################################################################
#%%     DEF FONCTIONS :  PARTIE TRADING


def get_last_Price(session,  nom_crypto):
    t = (session.get_server_time())["time"]
    prix = session.get_kline(
    category="linear",
    symbol=nom_crypto,
    interval=1,
    start=t - 1000*100,
    end=t,
    limit= 1
    )["result"]["list"][0][4]
    return(float(prix))

def get_Position_Info(session, nom_crypto):
    res = session.get_positions(
    category="linear",
    symbol=nom_crypto,
    )["result"]["list"][0]
    size = res["size"]
    side = 2* (res["side"]=='Buy') -1
    return(float(size)*side)


def market_order(session,nom_crypto,qty):
    sens="Buy"
    if qty<0 : 
        sens = "Sell"
    session.place_order(
    category="linear",
    symbol=nom_crypto,
    side=sens,
    orderType="Market",
    qty=str(abs(qty)),
    timeInForce="PostOnly",
    isLeverage=0,
    orderFilter="Order",
    )
    return()


def get_total_equity(session):
    res = session.get_wallet_balance(
    accountType="UNIFIED",
    coin="USDT",
    )["result"]["list"][0]
    total = res["totalEquity"]    
    return(float(total))


def get_time(session):
    res=session.get_server_time()["time"]
    return(int(res))




######################################################################################################################
######################################################################################################################
######################################################################################################################
#%%                   IMPLEMENTATION STRATEGIE DE TRADING

# Initialisation des parametres du bot 

session = HTTP(testnet=False)
sessionp = HTTP(
    testnet=False,
    api_key="",
    api_secret="",
)

crypto1 = 'BTCUSDT'
crypto2 =  'ETHUSDT'

######################################################################################################################
#%%

# Procédure de trading
def Trading_Step():
    #traitement des données
    df_1 = get_data(session,500,crypto1,15)
    df_2 = get_data(session,500,crypto2,15)
    df = df_1.copy()
    df['price']= df_1['price']/df_2['price']
    traitement_data(df)
    
    time.sleep(1)
    
    #chargement des dernières données de marché
    prix1 = get_last_Price(session, crypto1)
    prix2 = get_last_Price(session, crypto2)
    Portefeuille = get_total_equity(sessionp)
    
    time.sleep(1)
    
    position = np.sign(get_Position_Info(sessionp, crypto1))

  # exemple de procédure de trading
    if (position ==0):
        if ((df['ma100'][499]>df['ma150'][499]) and (df['deriv100'][499]>df['deriv150'][499]) ):
            
            #prise de position long
            market_order(sessionp, crypto1, round(Portefeuille/prix1,3))
            market_order(sessionp, crypto2, round(-Portefeuille/prix2,2))
            time.sleep(1)
        if ((df['ma100'][499]<df['ma150'][499]) and (df['deriv100'][499]<df['deriv150'][499]) ):
            
            #prise de position short
            market_order(sessionp, crypto1, round(-Portefeuille/prix1,3))
            market_order(sessionp, crypto2, round(Portefeuille/prix2,2))
            time.sleep(1)
        else:
            if ((position==1) and (df['ma50'][499]<df['ma100'][499])):
                #liquidation des position
                pos1 = get_Position_Info(sessionp, crypto1)
                market_order(sessionp, crypto1, -pos1)
                time.sleep(1)
                pos2 = get_Position_Info(sessionp, crypto2)
                market_order(sessionp, crypto2,-pos2 )
            if ((position==-1) and (df['ma50'][499]>df['ma100'][499])):
                #liquidation des position
                pos1 = get_Position_Info(sessionp, crypto1)
                market_order(sessionp, crypto1, -pos1)
                time.sleep(1)
                pos2 = get_Position_Info(sessionp, crypto2)
                market_order(sessionp, crypto2,-pos2 )

#%%
# Initialisation du portefeuille
L_Portefeuille=[get_total_equity(sessionp)] 
L_position = [np.sign(get_Position_Info(sessionp, crypto1))]


#%%

last_hour = int(get_data(session,1,crypto1,15)["time"][0])
chrono = (get_time(session) - last_hour)/60000 # nombre de minute depuis la derniere bougie

while True :
    chrono =(get_time(session) - last_hour)/60000 # nombre de minute depuis la derniere bougie
    print(round(100*(chrono/15),2), '%')
    if (chrono> 15): # attend 15min
        try : 
            Trading_Step()
            print("Update Position")
            time.sleep(1)
        except:
            print("Problem Happened")
        last_hour = int(get_data(session,1,crypto1,15)["time"][0])
        L_Portefeuille.append(get_total_equity(sessionp))
        L_position.append(np.sign(get_Position_Info(sessionp, crypto1)))
    time.sleep(21)
    
