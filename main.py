from fastapi import FastAPI
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import csv
from dateutil.relativedelta import relativedelta
from binance import Client

app = FastAPI()

api_key = "bc03el1MRfSQLVLCdBTRgHF8cgZmmAxiknz1siG0FM2YfEYbbzcLuppcCgIyLN0m"
api_secret = "5TCdDESBry2Fe6LEAdU2du4vrW9wwv48H06diB3y04W4fhHbGkinxepcBMBV00YP"

@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Connection available for Main",
        "data": []
    }


@app.get("/get_recommendation/poly/{symbol}/{interval}/{entry}")
async def poly_calculate(symbol: str, interval: str, entry: float):
    # get input data
    market = symbol
    tick_interval = interval
    price = entry
    start = (datetime.now() - relativedelta(years=1)).strftime('%d %b, %Y 07:00:00')
    end = datetime.now().strftime('%d %b, %Y 07:00:00')

    poly_exponent = 20

    client = Client(api_key, api_secret)
    kline = client.get_historical_klines(market, tick_interval, start, end)

    f = open('result.csv', 'w')
    writer = csv.writer(f)
    title = [
        'OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'QuoteVolume',
    ]
    writer.writerow(title)
    for candle in kline:
        single_data = [
            str(datetime.fromtimestamp(candle[0] / 1000).strftime('%d-%m-%y %H:%M')),
            str(candle[1]),
            str(candle[2]),
            str(candle[3]),
            str(candle[4]),
            str(candle[5]),
            str(candle[7]),
        ]
        writer.writerow(single_data)

    f.close()

    # read csv file as Data Frame
    df = pd.read_csv('result.csv')

    df['index'] = np.arange(len(df))
    # calculate VWAP
    df['vwap'] = df['QuoteVolume'] / df['Volume']

    # calculate ma30 based on Close candle
    df['ma_30'] = df.rolling(window=30)['vwap'].mean()

    # calculate ma90 based on Close candle
    df['ma_90'] = df.rolling(window=90)['vwap'].mean()

    # calculate entry price
    df['entry_price'] = df['ma_30']

    # calculate mirror ma90 based on vwap candle
    df['diff'] = df['ma_30'] - df['ma_90']
    df['mirror_ma_90'] = df['ma_30'] + df['diff']

    # calculate take profit
    df['take_profit'] = df[['mirror_ma_90', 'ma_90']].max(axis=1)
    df['take_profit_percent'] = abs((df['take_profit'] - price) / price * 100)

    # calculate buy back
    df['buy_back'] = df[['mirror_ma_90', 'ma_90']].min(axis=1)
    df['buy_back_percent'] = abs((df['buy_back'] - price) / price * 100)

    # calculate earning callback
    df['earning_callback'] = df['take_profit'] - (0.1 * (df['take_profit'] - df['entry_price']))
    df['earning_callback_percent'] = abs((df['earning_callback'] - df['take_profit']) / df['take_profit'] * 100)

    # calculate buy in callback
    df['buy_in_callback'] = df['buy_back'] + (0.1 * ((df['entry_price']) - df['buy_back']))
    df['buy_in_callback_percent'] = abs((df['buy_in_callback'] - df['buy_back']) / df['buy_back'] * 100)

    mymodel = np.poly1d(np.polyfit(df['index'], df['vwap'], poly_exponent))

    prediction = str(round(mymodel(365),2))

    df['poly'] = mymodel(df['index'])

    fig = px.scatter(x=df['index'], y=df['vwap'])
    # add ma30 chart line
    fig.add_trace(go.Scatter(
        x=df['index'],
        y=df['poly'],
        name='Poly prediction : '+prediction,
        connectgaps=True
    ))

    fig.add_trace(go.Scatter(
        x=df['index'],
        y=df['ma_30'],
        name='MA-30',
        connectgaps=True
    ))

    fig.add_trace(go.Scatter(
        x=df['index'],
        y=df['ma_90'],
        name='MA-90',
        connectgaps=True
    ))

    fig.add_trace(go.Scatter(
        x=df['index'],
        y=df['mirror_ma_90'],
        name='Mirror MA-90',
        connectgaps=True
    ))

    fig.show()

    # send response
    return {
        "success": True,
        "message": "Request Accepted",
        "data": {
            "market_trend": "Bullish" if df['ma_30'].iloc[-1] > df['ma_90'].iloc[-1] else "Bearish",
            "entry_price": df['entry_price'].iloc[-1],
            "take_profit": df['take_profit_percent'].iloc[-1],
            "earning_callback": df['earning_callback_percent'].iloc[-1],
            "buy_back": df['buy_back_percent'].iloc[-1],
            "buy_in_callback": df['buy_in_callback_percent'].iloc[-1],
            "status": "Recommended" if price < df['entry_price'].iloc[-1] and df['ma_30'].iloc[-1] > df['ma_90'].iloc[-1] else "Not Recommended",
        },
        "additional_data": {
            "ma_30": df['ma_30'].iloc[-1],
            "ma_90": df['ma_90'].iloc[-1],
            "mirror_ma_90": df['mirror_ma_90'].iloc[-1],
        },
    }