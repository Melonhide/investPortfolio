

if __name__ == "__main__":
    import yfinance as yf
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from OptionPriceCalculator import OptionPriceCalculator

    # 示例用法
    ticker = 'NVDA'
    stock = yf.Ticker(ticker)

    # 获取当前股价
    current_stock_price = stock.history(period='1d')['Close'].iloc[-1]
    print(f"Current Stock Price: {current_stock_price}")

    # 获取期权链
    expiration = '2024-06-28'
    options = stock.option_chain(expiration)
    puts = options.puts

    # 获取行权价为125的看跌期权市场价格
    strike_price = 122
    put_option_market_price = puts[puts['strike'] == strike_price]['lastPrice'].values[0]
    print(f"Market Price of 125 Strike Put Option: {put_option_market_price}")

    # 计算隐含波动率
    expiration_date = pd.to_datetime(expiration)
    current_date = pd.Timestamp('now')
    days_to_expiration = (expiration_date - current_date).days

    calc = OptionPriceCalculator()
    risk_free_rate = calc.get_risk_free_rate(days_to_expiration)
    implied_vol = calc.implied_volatility(put_option_market_price, current_stock_price, strike_price,
                                          days_to_expiration / 365, risk_free_rate, option_type='put')
    print(f"Implied Volatility: {implied_vol:.2%}")

    # 模拟股票价格变化
    stock_prices = np.arange(current_stock_price - 15, current_stock_price + 15, 0.01)
    put_option_prices = []

    for stock_price in stock_prices:
        delta = calc.get_delta(stock_price, strike_price, days_to_expiration / 365, risk_free_rate, implied_vol,
                               option_type='put')
        put_option_price = put_option_market_price + delta * (stock_price - current_stock_price)
        put_option_prices.append(put_option_price)

    # 计算总收益
    num_shares = 20
    num_options = 1  # 一个期权合约代表100股

    total_profits = []

    for stock_price, option_price in zip(stock_prices, put_option_prices):
        stock_profit = (stock_price - current_stock_price) * num_shares
        option_profit = (option_price - put_option_market_price) * num_options * 100
        total_profit = stock_profit + option_profit
        total_profits.append(total_profit)

    # --------------------------------------------------------------------------------------------------------------
    # # 绘制总收益随股票价格变化的图
    # plt.figure(figsize=(10, 6))
    # plt.plot(stock_prices, total_profits, marker='o', linestyle='-', color='g')
    # plt.xlabel('Stock Price')
    # plt.ylabel('Total Profit')
    # plt.title('Total Profit vs Stock Price')
    # plt.grid(True)
    # plt.show()

    # --------------------------------------------------------------------------------------------------------------

    # 查找总收益为0的点
    zero_profit_points = [(stock_price, profit) for stock_price, profit in zip(stock_prices, total_profits) if
                          abs(profit) < 0.035]

    # 绘制总收益随股票价格变化的图
    plt.figure(figsize=(10, 6))
    plt.plot(stock_prices, total_profits, linestyle='-', color='g', label='Total Profit')
    plt.xlabel('Stock Price')
    plt.ylabel('Total Profit')
    #plt.title('Total Profit vs Stock Price')
    plt.title(
        f'Total Profit vs Stock Price\n(Current Stock Price: {current_stock_price}, Strike Price: {strike_price}, '
        f'Put Option Price: {put_option_market_price}, Shares: {num_shares}, Option Contracts: {num_options})')
    plt.grid(True)

    # 标注总收益为0的点
    for point in zero_profit_points:
        plt.plot(point[0], point[1], 'ro')  # 红色圆点标记
        plt.annotate(f'{point[0]:.2f}', xy=point, textcoords='offset points', xytext=(10, -10),
                     arrowprops=dict(arrowstyle='->', color='red'))

    plt.legend()
    plt.show()