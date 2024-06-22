import yfinance as yf
import pandas as pd

class DownloadFromYfinance:

    @staticmethod
    def download_stock_data(ticker, start_date, end_date):
        # 下载股票数据
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        return stock_data


    @staticmethod
    def download_option_data(ticker, option_type, min_strike, max_strike, maturity_date):
        # 初始化Ticker对象
        stock = yf.Ticker(ticker)
        # 获取期权数据
        opts = stock.option_chain(maturity_date)
        # 根据期权类型选择数据
        if option_type == 'put':
            options = opts.puts
        elif option_type == 'call':
            options = opts.calls
        else:
            return pd.DataFrame()  # 返回空DataFrame

        # 筛选strike价格在给定范围内的期权
        return options[(options['strike'] >= min_strike) & (options['strike'] <= max_strike)]

    @staticmethod
    def download_stock_data_save_to_local(ticker, start_date, end_date):
        # 下载并保存股票数据到CSV
        stock_data = DownloadFromYfinance.download_stock_data(ticker, start_date, end_date)
        stock_data.to_csv(f'{ticker}_stock_data_from_{start_date}_to_{end_date}.csv')
        print(f'Saved stock data to {ticker}_stock_data_from_{start_date}_to_{end_date}.csv')

    @staticmethod
    def download_option_data_save_to_local(ticker, option_type, min_strike, max_strike, maturity_date):
        # 下载并保存期权数据到CSV
        option_data = DownloadFromYfinance.download_option_data(ticker, option_type, min_strike, max_strike,
                                                                maturity_date)
        if not option_data.empty:
            filename = f'{ticker}_{option_type}_option_data_strike_{min_strike}_to_{max_strike}_for_{maturity_date}.csv'
            option_data.to_csv(filename)
            print(f'Saved option data to {filename}')
        else:
            print("No data found for the specified range and type.")

if __name__ == "__main__":
    #DownloadFromYfinance.download_stock_data_save_to_local('AAPL', '2024-06-18', '2024-06-21')
    #DownloadFromYfinance.download_option_data_save_to_local('AAPL', 'put', 200, 225, '2024-06-28')

    import pandas as pd
    import matplotlib.pyplot as plt

    # # 加载CSV文件
    # data = pd.read_csv('AAPL_put_option_data_strike_200_to_225_for_2024-06-28.csv')
    # #data = pd.read_csv('AAPL_put_option_data_strike_200_to_225_for_2024-06-21.csv')
    #
    # # 确保strike列为数值型，以便排序
    # data['strike'] = pd.to_numeric(data['strike'], errors='coerce')
    # data = data.dropna(subset=['strike'])
    #
    # # 对数据按strike价格排序
    # data = data.sort_values('strike')
    #
    # # 绘制图表
    # plt.figure(figsize=(10, 5))
    # plt.plot(data['strike'], data['bid'], label='Bid Price', marker='o')
    # plt.plot(data['strike'], data['ask'], label='Ask Price', marker='o')
    # plt.title('AAPL Put Option Bid and Ask Prices for Strikes 200 to 225')
    # plt.xlabel('Strike Price')
    # plt.ylabel('Price ($)')
    # plt.legend()
    # plt.grid(True)
    # plt.show()

    def download_option_data(ticker, option_type, min_strike, max_strike, maturity_date):
        stock = yf.Ticker(ticker)
        opts = stock.option_chain(maturity_date)
        options = opts.puts if option_type == 'put' else opts.calls
        return options[(options['strike'] >= min_strike) & (options['strike'] <= max_strike)]


    def plot_option_data(ticker, min_strike, max_strike, maturity_date):
        puts = download_option_data(ticker, 'put', min_strike, max_strike, maturity_date)
        calls = download_option_data(ticker, 'call', min_strike, max_strike, maturity_date)

        # 确保数据是按strike排序的
        puts = puts.sort_values('strike')
        calls = calls.sort_values('strike')

        # 绘图
        plt.figure(figsize=(12, 6))
        plt.plot(puts['strike'], puts['bid'], label='Put Bid Price', marker='o')
        plt.plot(puts['strike'], puts['ask'], label='Put Ask Price', marker='o')
        plt.plot(calls['strike'], calls['bid'], label='Call Bid Price', marker='o')
        plt.plot(calls['strike'], calls['ask'], label='Call Ask Price', marker='o')
        plt.title(f'Apple Options Bid and Ask Prices for {maturity_date}')
        plt.xlabel('Strike Price')
        plt.ylabel('Price ($)')
        plt.legend()
        plt.grid(True)
        plt.show()


    # 调用函数
    plot_option_data('AAPL', 200, 225, '2024-06-28')


