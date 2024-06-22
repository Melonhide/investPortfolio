import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd


# 设置股票和期权
ticker = 'AAPL'
strike_price = 215
option_type = 'put'

# 下载股票数据
stock_data = yf.download(ticker, start="2024-06-18", end="2024-06-21")

# 转换股票数据索引到纽约时区
stock_data.index = stock_data.index.tz_localize('UTC').tz_convert('America/New_York')

# 获取期权数据
stock = yf.Ticker(ticker)
opt = stock.option_chain(date='2024-06-21')  # 指定日期
puts = opt.puts
specific_put = puts[puts['strike'] == strike_price]

# 转换期权数据时间到纽约时区
specific_put['lastTradeDate'] = pd.to_datetime(specific_put['lastTradeDate']).dt.tz_convert('America/New_York')

# 确保数据对齐
merged_data = pd.merge(stock_data['Close'], specific_put.set_index('lastTradeDate')[['bid', 'ask']], left_index=True, right_index=True, how='inner')
merged_data.to_csv('merged_data.csv')
# 绘图
plt.figure(figsize=(10, 6))
#plt.plot(merged_data['Close'], label='Stock Price')
plt.plot(merged_data['bid'], label='Option Bid Price')
plt.plot(merged_data['ask'], label='Option Ask Price')
plt.title('AAPL Stock and Option Price Over Time (ET)')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.grid(True)
plt.show()
