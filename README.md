<b>Smart Recommendation Feature</b>

Smart recommendation to generate setting when user create robot in Robot Trading Dollar Cost-Averaging (DCA) (such as AiGate or RoyalQ or Ninebot) or it call Compounding Strategy based on Machine Learning (Polynomial Regression), Moving Average, Mirror Moving Average and VWAP

Source Data : Binance (https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1h)

Build in Python with Libraries:
1. FastAPI
2. pandas
3. plotly
4. numpy

Input 
- Market Symbol (ex: BTCUSDT)
- Timeframe (ex: 1h)
- Price (ex: 65230)

Output
- Market Trend (Bearish or Bullish) from MA
- Entry Price from MA
- Take Profit from MA
- Earning Callback from MA
- Buy Back from MA
- Buy In Callback from MA
- Status (Recomended or Not Recomended) from ML
- Image Represent Data

Sample Output
<br>
<img src="https://raw.githubusercontent.com/ijlik/aigate-smart-recommendation/master/sample-data.png">
<br>
<img src="https://raw.githubusercontent.com/ijlik/aigate-smart-recommendation/master/sample-image.png">

Hope this code can implement in AiGate or RoyalQ or Ninebot ecosystem
