TRADING_FEE = 0.0012


class BitcoinSimulator:
    def __init__(self, yen):
        self.user = BitcoinUser(yen)

    def simulate(self, data, model):
        predict_data = model.predict(data)
        data['predict'] = predict_data
        assets = []

        for index, row in data.iterrows():
            d = self.decide_action(row)
            if d == 1:
                amount = self.user.yen / row['close']
                self.user.buy_btc(row['close'], amount)
            elif d == -1:
                amount = self.user.btc
                self.user.sell_btc(row['close'], amount)

            assets.append(self.user.total)

        return assets

    def decide_action(self, data):
        """
        Returns
        -------
        int
            -1 : Means sell
             0 : Means do nothing
             1 : Means buy
        """

        if self.user.yen > 0 and data['predict'] / data['close'] > 1 + TRADING_FEE:
            return 1
        elif self.user.btc > 0 and data['predict'] / data['close'] < 1 - TRADING_FEE:
            return -1

        return 0


class BitcoinUser:
    def __init__(self, yen):
        self.yen = yen
        self.btc = 0
        self.total = yen

    def buy_btc(self, price, amount):
        self.yen -= price * amount
        self.btc += amount * (1 - TRADING_FEE)
        self.update_total_assets(price)

    def sell_btc(self, price, amount):
        self.btc -= amount
        self.yen += price * amount * (1 - TRADING_FEE)
        self.update_total_assets(price)

    def update_total_assets(self, price):
        self.total = self.yen + self.btc * price
