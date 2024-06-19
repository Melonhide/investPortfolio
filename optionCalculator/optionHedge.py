class OptionStockStrategy:
    def f(self, stock_start_price, stock_end_price, stock_amount, option_start_price, option_end_price, option_amount):
        pass



if __name__ == "__main__":
    stock_start_price = 214.15
    stock_end_price = 211.62
    stock_amount = 100
    stock_loss = (stock_end_price-stock_start_price)*stock_amount
    print(stock_loss)

    option_start_price = 1.10
    option_end_price = 2.25
    need_option = -stock_loss/(option_end_price-option_start_price)
    print(need_option)
    print(need_option*option_start_price)

