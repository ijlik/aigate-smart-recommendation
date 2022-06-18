from fastapi import FastAPI
import pandas as pd
from datetime import datetime
import numpy as np
import csv
from binance import Client

app = FastAPI()

api_key = "bc03el1MRfSQLVLCdBTRgHF8cgZmmAxiknz1siG0FM2YfEYbbzcLuppcCgIyLN0m"
api_secret = "5TCdDESBry2Fe6LEAdU2du4vrW9wwv48H06diB3y04W4fhHbGkinxepcBMBV00YP"


@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Connection available for Index",
        "data": [

        ]
    }


@app.get("/get_data_test/{symbol}/{interval}/{entry}/{start}/{end}/{orde}")
async def srf_calculates(symbol: str, interval: str, entry: float, start: str, end: str, orde: int):
    price = entry
    plain_df = getDataPrice(symbol, interval, start, end)
    df_ma = calculateMAIndicator(plain_df)
    df_rule = calculateMARule(df_ma, price)
    df_result = calculateResult(df_rule)
    df_polynomial = calculatePolyPrediction(df_result, interval, orde)

    # send response
    prediction = predictCurrentPrice(df_polynomial, interval, 'vwap', orde)
    return {
        "success": True,
        "message": "Request Accepted",
        "data": {
            "last_candle": {
                "date": df_polynomial['OpenTime'].iloc[-2],
                "open": df_polynomial['Open'].iloc[-2],
                "high": df_polynomial['High'].iloc[-2],
                "low": df_polynomial['Low'].iloc[-2],
                "close": df_polynomial['Close'].iloc[-2],
                "vwap": df_polynomial['vwap'].iloc[-2],
            },
            "prediction_candle": {
                "vwap": prediction,
            },
            "confirm_candle": {
                "date": df_polynomial['OpenTime'].iloc[-1],
                "open": df_polynomial['Open'].iloc[-1],
                "high": df_polynomial['High'].iloc[-1],
                "low": df_polynomial['Low'].iloc[-1],
                "close": df_polynomial['Close'].iloc[-1],
                "vwap": df_polynomial['vwap'].iloc[-1],
            },
            "prediction_value": {
                "vwap": True if prediction > df_polynomial['vwap'].iloc[-2] else False,
            },
            "actual_value": {
                "vwap": True if df_polynomial['vwap'].iloc[-1] > df_polynomial['vwap'].iloc[-2] else False,
            },

            # "kline": kline_data(start, end, symbol, interval)
        },

    }


def getDataPrice(symbol: str, interval: str, start: str, end: str):
    client = Client(api_key, api_secret)
    kline = client.get_historical_klines(symbol, interval, start, end)

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

    return df


def calculateMAIndicator(df):
    # calculate vwap price
    df['vwap'] = df['QuoteVolume'] / df['Volume']

    # calculate ma30 based on vwap price
    df['ma_30'] = df.rolling(window=30)['vwap'].mean()

    # calculate ma90 based on vwap price
    df['ma_90'] = df.rolling(window=90)['vwap'].mean()

    # calculate mirror ma90 based on ma_30 and ma_90
    df['diff'] = df['ma_30'] - df['ma_90']
    df['mirror_ma_90'] = df['ma_30'] + df['diff']

    return df


def calculateMARule(df, price):
    # calculate take profit
    df['take_profit'] = df[['mirror_ma_90', 'ma_90']].max(axis=1)
    df['take_profit_percent'] = abs((df['take_profit'] - price) / price * 100)

    # calculate buy back
    df['buy_back'] = df[['mirror_ma_90', 'ma_90']].min(axis=1)
    df['buy_back_percent'] = abs((df['buy_back'] - price) / price * 100)

    # calculate entry price
    df['entry_price'] = df['ma_30']

    return df


def calculateResult(df):
    # calculate earning callback
    df['earning_callback'] = df['take_profit'] - (0.1 * (df['take_profit'] - df['entry_price']))
    df['earning_callback_percent'] = abs((df['earning_callback'] - df['take_profit']) / df['take_profit'] * 100)

    # calculate buy in callback
    df['buy_in_callback'] = df['buy_back'] + (0.1 * ((df['entry_price']) - df['buy_back']))
    df['buy_in_callback_percent'] = abs((df['buy_in_callback'] - df['buy_back']) / df['buy_back'] * 100)

    return df


def getPolyExponent(tick_interval: str):
    poly_exponent = 0
    if tick_interval == '1d':
        poly_exponent = 20
    elif tick_interval == '4h':
        poly_exponent = 9
    else:
        poly_exponent = 11

    return poly_exponent


def createPolyModel(df, tick_interval: str, df_index_target: str, poly_exponent: int):
    # poly_exponent = getPolyExponent(tick_interval)
    model = np.poly1d(np.polyfit(df['index'], df[df_index_target], poly_exponent))

    return model


def calculatePolyPrediction(df, tick_interval, orde):
    # predict vwap value for each candle
    vwap_model = createPolyModel(df, tick_interval, 'vwap', orde)
    df['vwap_prediction'] = vwap_model(df['index'])

    return df


def predictNextPrice(df, tick_interval, column, orde):
    last_index = df['index'].iloc[-1]
    prediction_index = last_index + 1
    print(last_index)
    print(prediction_index)
    # predict vwap value for next candle
    model = createPolyModel(df, tick_interval, column, orde)
    prediction = model(prediction_index)

    return prediction


def predictCurrentPrice(df, tick_interval, column, orde):
    last_index = df['index'].iloc[-2]
    prediction_index = last_index + 1
    print(last_index)
    print(prediction_index)
    # predict vwap value for next candle
    model = createPolyModel(df, tick_interval, column, orde)
    prediction = model(prediction_index)

    return prediction


def kline_data(start: str, end: str, symbol: str, interval: str):
    client = Client(api_key, api_secret)
    kline = client.get_historical_klines(symbol, interval, start, end)
    raw_data = []
    for candle in kline:
        str_date = str(datetime.fromtimestamp(candle[0] / 1000).strftime('%d-%m-%y %H:%M:00'))
        open_price = float(candle[1])
        high_price = float(candle[2])
        low_price = float(candle[3])
        close_price = float(candle[4])
        coin_volume = float(candle[5])
        usd_volume = float(candle[7])

        single_data = [
            str_date,
            open_price,
            high_price,
            low_price,
            close_price,
            coin_volume,
            usd_volume,
        ]
        raw_data.append(single_data)

    return raw_data
