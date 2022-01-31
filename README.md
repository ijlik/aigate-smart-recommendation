<b>AiGate Smart Recommendation</b>

Smart recommendation to generate setting when user create robot in AiGate Dollar Cost-Averaging (DCA) or it call Compounding Strategy based on Machine Learning, Moving Average, Mirror Moving Average and VWAP (soon)

Source Data : Binance (https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h)

Build in Python with Libraries:
1. FastAPI
2. pandas
3. plotly

Input 
- Market Symbol (ex: BTCUSDT)
- Timeframe (ex: 1h)
- Price (ex: 65230)

Output
- Market Trend (Bearish or Bullish)
- Entry Price
- Take Profit
- Earning Callback
- Buy Back
- Buy In Callback
- Status (Recomended or Not Recomended)
- Image Represent Data

Sample Output
<br>
<img src="https://raw.githubusercontent.com/ijlik/aigate-smart-recommendation/master/sample-data.png">
<br>
<img src="https://raw.githubusercontent.com/ijlik/aigate-smart-recommendation/master/sampel-image.png">

Hope this code can implement in AiGate ecosystem
