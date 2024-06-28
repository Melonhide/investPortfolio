
if __name__ == "__main__":
    import yfinance as yf
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from OptionPriceCalculator import OptionPriceCalculator

    # 获取NVIDIA的当前股价
    ticker = 'NVDA'
    stock = yf.Ticker(ticker)

    # 获取当前股价
    current_stock_price = stock.history(period='1d')['Close'].iloc[-1]
    print(f"Current Stock Price: {current_stock_price}")

    # 获取期权链
    expiration = '2024-07-19'
    options = stock.option_chain(expiration)
    puts = options.puts

    # 获取行权价格在100到130之间的看跌期权市场价格
    strike_prices = np.arange(100, 131, 1)
    implied_vols = []

    expiration_date = pd.to_datetime(expiration)
    current_date = pd.Timestamp('now')
    days_to_expiration = (expiration_date - current_date).days

    calc = OptionPriceCalculator()
    risk_free_rate = calc.get_risk_free_rate(days_to_expiration)

    for strike_price in strike_prices:
        try:
            put_option_market_price = puts[puts['strike'] == strike_price]['lastPrice'].values[0]
            implied_vol = calc.implied_volatility(put_option_market_price, current_stock_price, strike_price,
                                                  days_to_expiration / 365, risk_free_rate, option_type='put')
            implied_vols.append(implied_vol)
        except IndexError:
            print(f"No market price available for strike price {strike_price}")
            implied_vols.append(None)

    # 计算Delta和Gamma
    deltas = []
    gammas = []

    for i, strike_price in enumerate(strike_prices):
        if implied_vols[i] is not None:
            delta = calc.get_delta(current_stock_price, strike_price, days_to_expiration / 365, risk_free_rate,
                                   implied_vols[i], option_type='put')
            gamma = calc.get_gamma(current_stock_price, strike_price, days_to_expiration / 365, risk_free_rate,
                                   implied_vols[i])
            deltas.append(delta)
            gammas.append(gamma)
            # 打印每个行权价对应的Delta和Gamma
            print(f"Strike Price: {strike_price}, Delta: {delta:.4f}, Gamma: {gamma:.4f}")
        else:
            deltas.append(None)
            gammas.append(None)
            print(f"Strike Price: {strike_price}, Delta: N/A, Gamma: N/A")

    # 绘制Delta和Gamma图
    fig, ax1 = plt.subplots()

    color = 'tab:blue'
    ax1.set_xlabel('Strike Price')
    ax1.set_ylabel('Delta', color=color)
    ax1.plot(strike_prices, deltas, marker='o', linestyle='-', color=color, label='Delta')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.legend(loc='upper left')

    ax2 = ax1.twinx()
    color = 'tab:red'
    ax2.set_ylabel('Gamma', color=color)
    ax2.plot(strike_prices, gammas, marker='o', linestyle='-', color=color, label='Gamma')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.legend(loc='upper right')

    fig.tight_layout()
    plt.title(f'Delta and Gamma vs Strike Price for NVDA Put Options\nCurrent Stock Price: {current_stock_price} on {current_date}')
    plt.grid(True)
    plt.show()

