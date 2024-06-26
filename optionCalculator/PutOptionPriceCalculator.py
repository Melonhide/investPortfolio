

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
    strike_price = 115
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
    zero_crossing_points = []
    for i in range(1, len(total_profits)):
        if total_profits[i - 1] >= 0 and total_profits[i] <= 0:
            zero_crossing_points.append((stock_prices[i-1], total_profits[i-1]))
        elif total_profits[i - 1] <= 0 and total_profits[i] >= 0:
            zero_crossing_points.append((stock_prices[i], total_profits[i]))
        if len(zero_crossing_points) >= 2:
            break

    zero_crossing_points = sorted(zero_crossing_points, key=lambda x: x[0])

    # 打印收益为正的区间
    if len(zero_crossing_points) == 2:
        lower_bound = zero_crossing_points[0][0]
        upper_bound = zero_crossing_points[1][0]
        print(f"When the stock price is less than {lower_bound:.2f}, the total profit is positive.")
        print(f"When the stock price is greater than {upper_bound:.2f}, the total profit is positive.")
    else:
        print("Unable to determine the profit positive range with the given data.")

    # 绘制总收益随股票价格变化的图
    plt.figure(figsize=(10, 6))
    plt.plot(stock_prices, total_profits, linestyle='-', color='g', label='Total Profit')
    plt.xlabel('Stock Price')
    plt.ylabel('Total Profit')
    plt.title(
        f'Total Profit vs Stock Price\n(Current Stock Price: {current_stock_price}, Strike Price: {strike_price}, '
        f'Put Option Price: {put_option_market_price}, Shares: {num_shares}, Option Contracts: {num_options})')
    plt.grid(True)

    # 标注总收益从负数变为正数的点
    for i, point in enumerate(zero_crossing_points):
        xytext = (-60, -10) if i == 0 else (10, -10)  # 确保第一个点在左边，第二个点在右边
        plt.plot(point[0], point[1], 'ro')  # 红色圆点标记
        plt.annotate(f'{point[0]:.2f}', xy=point, textcoords='offset points', xytext=xytext,
                     arrowprops=dict(arrowstyle='->', color='red'))

    plt.legend()
    plt.show()