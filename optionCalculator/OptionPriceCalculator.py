import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq
import pandas_datareader.data as web


class OptionPriceCalculator:
    @staticmethod
    # Black-Scholes公式计算期权价格
    def black_scholes(S, K, T, r, sigma, option_type='call'):
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        if option_type == 'call':
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        elif option_type == 'put':
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        else:
            raise ValueError("option_type must be either 'call' or 'put'")

        return price

    @staticmethod
    # 隐含波动率计算
    def implied_volatility(option_market_price, S, K, T, r, option_type='call'):
        objective_function = lambda sigma: OptionPriceCalculator.black_scholes(S, K, T, r, sigma,
                                                                               option_type) - option_market_price
        iv = brentq(objective_function, 1e-6, 5.0)
        return iv

    @staticmethod
    def get_risk_free_rate(expiration_days=None):
        """
        获取无风险利率，默认为最短时间的国债利率。

        参数:
        expiration_days (int): 期权的到期时间，以天为单位。如果为None，则默认为最短时间的国债利率。

        返回:
        float: 无风险利率（年化）。
        """
        # 获取不同期限的美国国债收益率
        three_month_rate = web.DataReader('TB3MS', 'fred')  # 3个月国债收益率
        six_month_rate = web.DataReader('TB6MS', 'fred')  # 6个月国债收益率
        one_year_rate = web.DataReader('GS1', 'fred')  # 1年期国债收益率
        five_year_rate = web.DataReader('GS5', 'fred')  # 5年期国债收益率
        ten_year_rate = web.DataReader('GS10', 'fred')  # 10年期国债收益率

        # 合并数据
        rates = pd.concat([three_month_rate, six_month_rate, one_year_rate, five_year_rate, ten_year_rate], axis=1)
        rates.columns = ['3-Month', '6-Month', '1-Year', '5-Year', '10-Year']

        # 获取最新的国债收益率
        latest_rates = rates.iloc[-1]

        # 如果未指定到期时间，则返回最短时间的国债利率
        if expiration_days is None:
            return latest_rates['3-Month'] / 100

        # 根据到期时间选择相应的无风险利率
        T = expiration_days / 365  # 将天数转换为年
        if T <= 0.25:
            risk_free_rate = latest_rates['3-Month'] / 100
        elif T <= 0.5:
            risk_free_rate = latest_rates['6-Month'] / 100
        elif T <= 1:
            risk_free_rate = latest_rates['1-Year'] / 100
        elif T <= 5:
            risk_free_rate = latest_rates['5-Year'] / 100
        else:
            risk_free_rate = latest_rates['10-Year'] / 100

        return risk_free_rate

    @staticmethod
    def get_delta(S, K, T, r, sigma, option_type='call'):
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        if option_type == 'call':
            delta = norm.cdf(d1)
        elif option_type == 'put':
            delta = norm.cdf(d1) - 1
        else:
            raise ValueError("option_type must be either 'call' or 'put'")
        return delta

    @staticmethod
    def get_gamma(S, K, T, r, sigma):
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        return gamma

    @staticmethod
    def integrate_delta(initial_stock_price, final_stock_price, K, T, r, sigma, option_type='call'):
        stock_prices = np.linspace(initial_stock_price, final_stock_price, 100)
        option_prices = [OptionPriceCalculator.black_scholes(S, K, T, r, sigma, option_type) for S in stock_prices]
        deltas = [OptionPriceCalculator.get_delta(S, K, T, r, sigma, option_type) for S in stock_prices]

        integrated_prices = [option_prices[0]]
        for i in range(1, len(stock_prices)):
            ds = stock_prices[i] - stock_prices[i - 1]
            integrated_price = integrated_prices[-1] + deltas[i - 1] * ds
            integrated_prices.append(integrated_price)

        return stock_prices, integrated_prices

    @staticmethod
    def integrate_delta_stress(initial_stock_price, final_stock_price, K, T, r, sigma, option_type='call', stress_val=0):
        stock_prices = np.linspace(initial_stock_price, final_stock_price, 100)
        option_prices = [OptionPriceCalculator.black_scholes(S, K, T, r, sigma, option_type) for S in stock_prices]
        deltas = [OptionPriceCalculator.get_delta(S, K, T, r, sigma, option_type) for S in stock_prices]

        integrated_prices = [option_prices[0]]
        for i in range(1, len(stock_prices)):
            ds = stock_prices[i] - stock_prices[i - 1]
            integrated_price = integrated_prices[-1] + (deltas[i - 1]-stress_val) * ds
            integrated_prices.append(integrated_price)

        return stock_prices, integrated_prices

    @staticmethod
    def integrate_gamma(initial_stock_price, final_stock_price, K, T, r, sigma, option_type='call'):
        stock_prices = np.linspace(initial_stock_price, final_stock_price, 100)
        deltas = [OptionPriceCalculator.get_delta(S, K, T, r, sigma, option_type) for S in stock_prices]
        gammas = [OptionPriceCalculator.get_gamma(S, K, T, r, sigma) for S in stock_prices]

        integrated_deltas = [deltas[0]]
        for i in range(1, len(stock_prices)):
            ds = stock_prices[i] - stock_prices[i - 1]
            integrated_delta = integrated_deltas[-1] + gammas[i - 1] * ds
            integrated_deltas.append(integrated_delta)

        integrated_prices = [OptionPriceCalculator.black_scholes(initial_stock_price, K, T, r, sigma, option_type)]
        for i in range(1, len(stock_prices)):
            ds = stock_prices[i] - stock_prices[i - 1]
            integrated_price = integrated_prices[-1] + integrated_deltas[i - 1] * ds
            integrated_prices.append(integrated_price)

        return stock_prices, integrated_prices

if __name__ == "__main__":
    import matplotlib.pyplot as plt

    # calc = OptionPriceCalculator()
    # risk_free_rate_default = calc.get_risk_free_rate()
    # risk_free_rate_6months = calc.get_risk_free_rate(180)
    # risk_free_rate_1year = calc.get_risk_free_rate(365)
    #
    # print(f"Default Risk-Free Rate: {risk_free_rate_default}")
    # print(f"Risk-Free Rate for 6 Months: {risk_free_rate_6months}")
    # print(f"Risk-Free Rate for 1 Year: {risk_free_rate_1year}")

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

    #--------------------------------------------------------------------------------------------------------------------
    # # 获取行权价为125的看跌期权市场价格
    # strike_price = 120
    # put_option_market_price = puts[puts['strike'] == strike_price]['lastPrice'].values[0]
    # print(f"Market Price of 125 Strike Put Option: {put_option_market_price}")
    #
    # # 计算隐含波动率
    # expiration_date = pd.to_datetime(expiration)
    # current_date = pd.Timestamp('now')
    # days_to_expiration = (expiration_date - current_date).days
    #
    # # 假设无风险利率为最近的3个月国债收益率
    # calc = OptionPriceCalculator()
    # risk_free_rate = calc.get_risk_free_rate(days_to_expiration)
    #
    # # 计算隐含波动率
    # implied_vol = calc.implied_volatility(put_option_market_price, current_stock_price, strike_price,
    #                                       days_to_expiration / 365, risk_free_rate, option_type='put')
    # print(f"Implied Volatility: {implied_vol:.2%}")

    #-------------------------------------------------------------------------------------------------------------------
    # 获取行权价格在100到130之间的看跌期权市场价格
    strike_prices = np.arange(100, 130, 1)
    put_prices = []
    implied_vols = []

    expiration_date = pd.to_datetime(expiration)
    current_date = pd.Timestamp('now')
    days_to_expiration = (expiration_date - current_date).days

    calc = OptionPriceCalculator()
    risk_free_rate = calc.get_risk_free_rate(days_to_expiration)

    for strike_price in strike_prices:
        try:
            put_option_market_price = puts[puts['strike'] == strike_price]['lastPrice'].values[0]
            put_prices.append(put_option_market_price)
            implied_vol = calc.implied_volatility(put_option_market_price, current_stock_price, strike_price,
                                                  days_to_expiration / 365, risk_free_rate, option_type='put')
            implied_vols.append(implied_vol)
            print(f"Strike Price: {strike_price}, Impl Vol: {implied_vol:.4f}")
        except IndexError:
            print(f"No market price available for strike price {strike_price}")
            put_prices.append(None)
            implied_vols.append(None)

    # 绘制隐含波动率图
    plt.figure(figsize=(10, 6))
    plt.plot(strike_prices, implied_vols, marker='o', linestyle='-', color='b')
    plt.xlabel('Strike Price')
    plt.ylabel('Implied Volatility')
    plt.title('Implied Volatility vs Strike Price for NVDA Put Options')
    plt.grid(True)
    plt.show()
    #-----------------------------------------------------------------------------------------------------------------


    #-----------------------------------------------------------------------------------------------------------------
    # # 获取行权价为125的看跌期权市场价格
    # strike_price = 125
    # put_option_market_price = puts[puts['strike'] == strike_price]['lastPrice'].values[0]
    # print(f"Market Price of 125 Strike Put Option: {put_option_market_price}")
    #
    # # 计算隐含波动率
    # expiration_date = pd.to_datetime(expiration)
    # current_date = pd.Timestamp('now')
    # days_to_expiration = (expiration_date - current_date).days
    #
    # calc = OptionPriceCalculator()
    # risk_free_rate = calc.get_risk_free_rate(days_to_expiration)
    # implied_vol = calc.implied_volatility(put_option_market_price, current_stock_price, strike_price,
    #                                       days_to_expiration / 365, risk_free_rate, option_type='put')
    # print(f"Implied Volatility: {implied_vol:.2%}")
    #
    # # 计算Delta和Gamma
    # delta_value = calc.get_delta(current_stock_price, strike_price, days_to_expiration / 365, risk_free_rate, implied_vol,
    #                          option_type='put')
    # gamma_value = calc.get_gamma(current_stock_price, strike_price, days_to_expiration / 365, risk_free_rate, implied_vol)
    #
    # print(f"Delta: {delta_value:.4f}")
    # print(f"Gamma: {gamma_value:.6f}")
    # -----------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------------
    # 获取行权价格在100到130之间的看跌期权市场价格
    # strike_prices = np.arange(100, 131, 1)
    # implied_vols = []
    #
    # expiration_date = pd.to_datetime(expiration)
    # current_date = pd.Timestamp('now')
    # days_to_expiration = (expiration_date - current_date).days
    #
    # calc = OptionPriceCalculator()
    # risk_free_rate = calc.get_risk_free_rate(days_to_expiration)
    #
    # for strike_price in strike_prices:
    #     try:
    #         put_option_market_price = puts[puts['strike'] == strike_price]['lastPrice'].values[0]
    #         implied_vol = calc.implied_volatility(put_option_market_price, current_stock_price, strike_price, days_to_expiration / 365, risk_free_rate, option_type='put')
    #         implied_vols.append(implied_vol)
    #     except IndexError:
    #         print(f"No market price available for strike price {strike_price}")
    #         implied_vols.append(None)
    #
    # # 计算Delta和Gamma
    # deltas = []
    # gammas = []
    #
    # for i, strike_price in enumerate(strike_prices):
    #     if implied_vols[i] is not None:
    #         delta = calc.get_delta(current_stock_price, strike_price, days_to_expiration / 365, risk_free_rate, implied_vols[i], option_type='put')
    #         gamma = calc.get_gamma(current_stock_price, strike_price, days_to_expiration / 365, risk_free_rate, implied_vols[i])
    #         deltas.append(delta)
    #         gammas.append(gamma)
    #     else:
    #         deltas.append(None)
    #         gammas.append(None)
    #
    # # 绘制Delta和Gamma图
    # fig, ax1 = plt.subplots()
    #
    # color = 'tab:blue'
    # ax1.set_xlabel('Strike Price')
    # ax1.set_ylabel('Delta', color=color)
    # ax1.plot(strike_prices, deltas, marker='o', linestyle='-', color=color, label='Delta')
    # ax1.tick_params(axis='y', labelcolor=color)
    # ax1.legend(loc='upper left')
    #
    # ax2 = ax1.twinx()
    # color = 'tab:red'
    # ax2.set_ylabel('Gamma', color=color)
    # ax2.plot(strike_prices, gammas, marker='o', linestyle='-', color=color, label='Gamma')
    # ax2.tick_params(axis='y', labelcolor=color)
    # ax2.legend(loc='upper right')
    #
    # fig.tight_layout()
    # plt.title('Delta and Gamma vs Strike Price for NVDA Put Options')
    # plt.grid(True)
    # plt.show()

    # -----------------------------------------------------------------------------------------------------------------

    # # 获取行权价为125的看跌期权市场价格
    # strike_price = 125
    # put_option_market_price = puts[puts['strike'] == strike_price]['lastPrice'].values[0]
    # print(f"Market Price of 125 Strike Put Option: {put_option_market_price}")
    #
    # # 计算隐含波动率
    # expiration_date = pd.to_datetime(expiration)
    # current_date = pd.Timestamp('now')
    # days_to_expiration = (expiration_date - current_date).days
    #
    # calc = OptionPriceCalculator()
    # risk_free_rate = calc.get_risk_free_rate(days_to_expiration)
    # implied_vol = calc.implied_volatility(put_option_market_price, current_stock_price, strike_price,
    #                                       days_to_expiration / 365, risk_free_rate, option_type='put')
    # print(f"Implied Volatility: {implied_vol:.2%}")
    #
    # # 使用积分Delta和Gamma计算期权价格变化
    # initial_stock_price = current_stock_price - 20
    # final_stock_price = current_stock_price + 20
    #
    # stock_prices_delta, integrated_prices_delta = calc.integrate_delta(initial_stock_price, final_stock_price,
    #                                                                    strike_price, days_to_expiration / 365,
    #                                                                    risk_free_rate, implied_vol, option_type='put')
    # stock_prices_gamma, integrated_prices_gamma = calc.integrate_gamma(initial_stock_price, final_stock_price,
    #                                                                    strike_price, days_to_expiration / 365,
    #                                                                    risk_free_rate, implied_vol, option_type='put')
    #
    # # 绘制期权价格图
    # plt.figure(figsize=(14, 7))
    #
    # # 通过积分Delta得到期权价格图
    # plt.subplot(1, 2, 1)
    # plt.plot(stock_prices_delta, integrated_prices_delta, marker='o', linestyle='-', color='b')
    # plt.xlabel('Stock Price')
    # plt.ylabel('Option Price')
    # plt.title('Option Price vs Stock Price (Integrated Delta)')
    # plt.grid(True)
    #
    # # 通过二次积分Gamma得到期权价格图
    # plt.subplot(1, 2, 2)
    # plt.plot(stock_prices_gamma, integrated_prices_gamma, marker='o', linestyle='-', color='r')
    # plt.xlabel('Stock Price')
    # plt.ylabel('Option Price')
    # plt.title('Option Price vs Stock Price (Integrated Gamma)')
    # plt.grid(True)
    #
    # plt.tight_layout()
    # plt.show()