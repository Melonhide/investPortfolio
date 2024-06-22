import yfinance as yf

ticker = 'AAPL'
stock = yf.Ticker(ticker)
# 获取最近 7 天的每分钟数据
data = stock.history(interval='1m', period='5d')
# 保存数据为 CSV
data.to_csv(f"{ticker}_minute_data.csv")