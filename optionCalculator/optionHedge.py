class OptionStockStrategy:


    def f(self, stock_start_price, stock_end_price, stock_amount, option_start_price, option_end_price, option_amount):
        pass



if __name__ == "__main__":
    stock_start_price = 214.12
    stock_end_price = 211.62
    stock_amount = 50
    stock_loss = (stock_end_price-stock_start_price)*stock_amount
    print(stock_loss)

    option_start_price = 110
    option_end_price = 225
    need_option = -stock_loss/(option_end_price-option_start_price)
    print(need_option)
    print(need_option*option_start_price)


    ## 模拟盘
    print("假设我在2024 06 18 买入苹果 214每股，我的预期是涨到217每股，最大下跌为210")
    print("目前215 的put option，每个合约是240，假设我买1个")
    print("如果上涨，我需要cover我的put option, 也就是说，我需要买80股，成本价格是" + str(80*214))
    print("如果下跌，我每股损失4，总共损失"+str(4*80))
    print("也就是说，我的option必须涨到320以上")


