from fastapi import FastAPI
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import plotly.graph_objects as go
import csv

app = FastAPI()


@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Connection available",
        "data": []
    }


@app.get("/get_recommendation/{symbol}/{interval}")
async def root(symbol: str, interval: str):
    market = symbol
    tick_interval = interval
    url = 'https://api.binance.com/api/v3/klines?symbol=' + market + '&interval=' + tick_interval
    data = requests.get(url).json()
    # open the file in the write mode
    f = open('result.csv', 'w')
    # create the csv writer
    writer = csv.writer(f)
    title = [
        'OpenTime', 'Open', 'High', 'Low', 'Close', 'Volume', 'CloseTime', 'QuoteVolume', 'Trades', 'TakerBase',
        'TakerQuote', 'Ignore'
    ]
    # write a row to the csv file
    writer.writerow(title)
    for candle in data:
        single_data = [
            str(datetime.fromtimestamp(candle[0] / 1000).strftime('%d-%m-%y %H:%M')),
            str(candle[1]),
            str(candle[2]),
            str(candle[3]),
            str(candle[4]),
            str(candle[5]),
            str(datetime.fromtimestamp(candle[6] / 1000).strftime('%d-%m-%Y')) if tick_interval == '1d' else str(datetime.fromtimestamp(candle[6] / 1000).strftime('%d-%m-%Y %H:%M')),
            str(candle[7]),
            str(candle[8]),
            str(candle[9]),
            str(candle[10]),
            str(candle[11]),
        ]
        writer.writerow(single_data)

        # close = candle[4]
        # timestamp = candle[6]/1000
        # date_time = datetime.fromtimestamp(timestamp).strftime('%d-%m-%y %H:%M')
        # full_candle = [
        #     date_time,
        #     close,
        # ]
        # result.append(full_candle)

    # close the file
    f.close()
    #
    df = pd.read_csv('result.csv')
    # df['vwap'] = df['QuoteVolume'] / df['Volume']
    df['ma_20'] = df.rolling(window=20)['Close'].mean()
    df['ma_50'] = df.rolling(window=50)['Close'].mean()
    df['diff'] = df['ma_20'] - df['ma_50']
    df['mirror_ma_50'] = df['ma_20'] + df['diff']

    fig = go.Figure(data=[go.Candlestick(x=df['CloseTime'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'])])

    fig.add_trace(go.Scatter(
        x=df['CloseTime'],
        y=df['ma_20'],
        name='MA-20',  # Style name/legend entry with html tags
        connectgaps=True  # override default to connect the gaps
    ))

    fig.add_trace(go.Scatter(
        x=df['CloseTime'],
        y=df['ma_50'],
        name='MA-50',  # Style name/legend entry with html tags
        connectgaps=True  # override default to connect the gaps
    ))

    fig.add_trace(go.Scatter(
        x=df['CloseTime'],
        y=df['mirror_ma_50'],
        name='Mirror MA-50',  # Style name/legend entry with html tags
        connectgaps=True  # override default to connect the gaps
    ))

    fig.show()
    return {
        "success": True,
        "message": "Request Accepted",
        "data": data
    }
