import time
import random
import robin_stocks.robinhood as r
import logging


class CatchUpHill:

    logging.basicConfig(level=logging.INFO, format='%(asctime)s :: %(levelname)s :: %(message)s')

    @staticmethod
    def check_and_trade(stock, ratio):
        stock.update()
        if not stock.hold:
            return

        if stock.consecutiveDeclines >= 2:
            logging.info(f"Price drop detected for {stock.ticker} for two consecutive checks. Preparing to sell...")
            CatchUpHill.prepare_to_sell(stock, ratio)

        sleep_time = 60 + random.randint(0, 60)

        logging.info(f"Next check for {stock.ticker} in {sleep_time} seconds.")
        time.sleep(sleep_time)

    @staticmethod
    def prepare_to_sell(stock, ratio):
        current_sell_price = stock.target_sell_price_with_input_ratio(ratio)
        best_sell_price = stock.maxSellPrice * ratio
        if best_sell_price < stock.currentPrice:
            stock.set_target_sell_price(best_sell_price)
        else:
            stock.set_target_sell_price(current_sell_price)

        while True:
            stock.update()
            if stock.consecutiveIncreases >= 2:
                logging.info(f"Price rise detected for {stock.ticker} for two consecutive checks. Canceling sell...")
                break

            logging.info(f"Monitoring {stock.ticker} for selling opportunity...")
            if stock.currentPrice <= stock.targetSellPrice:
                logging.info(f"Attempting to sell {stock.ticker} at price {stock.currentPrice}")
                # 这里加入卖出股票的逻辑
                sell_order = r.order_sell_market(stock.ticker, stock.shares)
                if sell_order and 'id' in sell_order:
                    # 如果卖出成功，记录成功信息并退出循环
                    logging.info(f"Successfully sold all shares of {stock.ticker}")
                    logging.info(f"Total Earning: {stock.shares * (stock.currentPrice-stock.averageCost)}")
                    break
                else:
                    # 如果卖出失败，记录失败信息但不退出循环，继续监控股价变动
                    logging.error(f"Failed to sell shares of {stock.ticker}. Response: {sell_order}")
                    # 可选: 在这里加入延迟或重试逻辑
                    time.sleep(60)  # 继续监控前等待一段时间
            else:
                sleep_time = 60 + random.randint(0, 60)
                time.sleep(sleep_time)

