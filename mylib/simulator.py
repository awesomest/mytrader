from mylib import bitbank  # pylint: disable=import-error


class BitcoinSimulator:
    def __init__(self, yen):
        self.user = BitcoinUser(yen)

    def simulate(self, data, model):
        predict_data = model.predict(data)
        data["predict"] = predict_data
        assets = []

        for _, row in data.iterrows():
            action = self.decide_action(row)
            if action == 1:
                amount = self.user.yen / row["close"]
                self.user.buy_btc(row["close"], amount)
            elif action == -1:
                amount = self.user.btc
                self.user.sell_btc(row["close"], amount)

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

        if data["predict"] > 0:  # 上昇トレンド
            if self.user.yen > 0:
                return 1
        if data["predict"] < 0:  # 下降トレンド
            if self.user.btc > 0:
                return -1

        return 0


class BitcoinUser:
    def __init__(self, yen):
        self.yen = yen  # 現在の円価格
        self.btc = 0  # 現在のBitCoin価格
        self.total = yen  # 現在の総資産額
        self.target = 0  # 次の予定売買価格
        self.traded_btc = 0  # 前回の取引価格
        """
        TODO:
        diff_target = |target - btc|
        diff_current = |target - traded_btc|

        action_chance = diff_current / diff_target # 理想値との差のうち、どの程度近づいているか
        """

    def buy_btc(self, price, amount):
        self.yen -= price * amount
        self.btc += amount * (1 - bitbank.TRADING_FEE)
        self.update_total_assets(price)

    def sell_btc(self, price, amount):
        self.btc -= amount
        self.yen += price * amount * (1 - bitbank.TRADING_FEE)
        self.update_total_assets(price)

    def update_total_assets(self, price):
        self.total = self.yen + self.btc * price
