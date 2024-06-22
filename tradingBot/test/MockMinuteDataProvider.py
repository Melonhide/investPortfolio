import pandas as pd


class MockMinuteDataProvider:
    def __init__(self, ticker):
        self.data = pd.read_csv(f"{ticker}_minute_data.csv", index_col='Datetime', parse_dates=True)
        self.current_index = 0

    def get_latest_price(self):
        if self.current_index < len(self.data):
            current_price = self.data.iloc[self.current_index]['Close']
            self.current_index += 1
            return [current_price]
        return None