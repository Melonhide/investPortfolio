import robin_stocks.robinhood as r


class Stock:
    def __init__(self, ticker):
        self.ticker = ticker
        self.hold = False
        self.shares = 0
        self.averageCost = 0
        self.cost = 0
        self.currentPrice = 0
        self.maxSellPrice = 0
        self.targetSellPrice = 0
        self.fetch_data()
        self.previousPrice = self.currentPrice
        self.consecutiveDeclines = 0  # 追踪连续下跌的次数
        self.consecutiveIncreases = 0

    def fetch_data(self):
        holdings = r.build_holdings()
        if self.ticker in holdings:
            self.hold = True
            holding_info = holdings[self.ticker]
            self.shares = float(holding_info['quantity'])
            self.averageCost = float(holding_info['average_buy_price'])
            self.cost = self.shares * self.averageCost
            current_prices = r.get_latest_price(self.ticker)
            if current_prices:
                self.currentPrice = current_prices[0]
                self.maxSellPrice = self.currentPrice
                self.targetSellPrice = self.maxSellPrice
            else:
                print("Failed to fetch current price. Please check if ticker is correct.")

    def update(self):
        holdings = r.build_holdings()
        if self.ticker in holdings:
            self.previousPrice = self.currentPrice
            self.hold = True
            holding_info = holdings[self.ticker]
            self.shares = float(holding_info['quantity'])
            self.averageCost = float(holding_info['average_buy_price'])
            self.cost = self.shares * self.averageCost
            current_prices = r.get_latest_price(self.ticker)
            if current_prices:
                new_price = float(current_prices[0])
                if new_price > self.currentPrice:
                    self.consecutiveIncreases += 1
                    self.consecutiveDeclines = 0
                    self.maxSellPrice = max(new_price, self.maxSellPrice)
                elif new_price < self.currentPrice:
                    self.consecutiveDeclines += 1
                    self.consecutiveIncreases = 0
                self.currentPrice = new_price
            else:
                print("Failed to fetch current price. Please check if ticker is correct.")
        else:
            self.hold = False
            self.shares = 0
            self.averageCost = 0
            self.cost = 0
            self.currentPrice = 0
            self.maxSellPrice = 0

    def set_target_sell_price(self, new_price):
        self.targetSellPrice = new_price

    def get_hold_status(self):
        return self.hold

    def print_hold_status(self):
        if not self.hold:
            print(f"I am NOT holding {self.ticker} stock")
        else:
            print(f"I am  holding {self.ticker} stock")

    def get_average_cost(self):
        return self.averageCost

    def print_average_cost(self):
        if not self.hold:
            print(f"I am not holding {self.ticker} stock")
        else:
            print(f"The average cost for {self.ticker} stock is {self.averageCost}")

    def get_shares(self):
        return self.shares

    def print_shares(self):
        if not self.hold:
            print(f"I am not holding {self.ticker} stock")
        else:
            print(f"I am holding {self.shares} shares of {self.ticker} stock.")
            print(f"Total cost for {self.ticker} stock is {self.cost}.")

    def get_total_cost(self):
        return self.cost

    def print_total_cost(self):
        if not self.hold:
            print(f"I am not holding {self.ticker} stock")
        else:
            print(f"Total cost for {self.ticker} stock is {self.cost}.")

    # update_current_price function should not be use; User should use update function instead
    def update_current_price(self):
        current_prices = r.get_latest_price(self.ticker)
        if current_prices:
            current_price = current_prices[0]
            self.currentPrice = current_price

    def get_current_price(self):
        return self.currentPrice

    def print_current_price(self):
        print(f"Current price of {self.ticker} is {self.currentPrice}")

    def calculate_earning_per_share(self):
        return self.currentPrice-self.averageCost

    def calculate_total_earning(self):
        return (self.currentPrice-self.averageCost)*self.shares

    def calculate_earning_percentage(self):
        return (self.currentPrice-self.averageCost)/self.averageCost

    def target_sell_price_with_input_ratio(self, ratio, stop_loss_ratio=0.9, hard_stop_loss_ratio=0.9):
        if self.currentPrice >= self.averageCost:
            return self.averageCost+(self.currentPrice-self.averageCost)*ratio
        else:
            if self.averageCost*stop_loss_ratio <= self.currentPrice:
                return self.averageCost*stop_loss_ratio
            else:
                return self.currentPrice*hard_stop_loss_ratio


if __name__ == "__main__":
    # import robin_stocks.robinhood as r
    # from config import RH_USERNAME, RH_PASSWORD
    #
    #
    # r.login(RH_USERNAME, RH_PASSWORD)
    # nvda = Stock('NVDA')
    # nvda.get_shares()
    # nvda.get_total_cost()
    # nvda.get_average_cost()
    # nvda.get_current_price()
    #
    # aapl = Stock('AAPL')
    # aapl.get_shares()
    # aapl.get_total_cost()
    # aapl.get_average_cost()
    # aapl.get_current_price()
    #
    # tsla = Stock('TSLA')
    # tsla.get_shares()
    # tsla.get_total_cost()
    # tsla.get_average_cost()
    # tsla.get_current_price()
    #
    # r.logout()

    print((141.4-133.89)*52.5)
