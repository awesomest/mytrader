"""user.py"""

from bitbank.models import AssetHistory
from . import bitbank_app  # pylint: disable=relative-beyond-top-level


class BitcoinUser:
    """
    BitcoinUser
    """

    UPWARD_THRESHOLD = 0.00125  # TODO: Decide the best. this is 20th percentile now.
    DOWNWARD_THRESHOLD = -0.00119  # TODO: Decide the best. this is 80th percentile now.

    def __init__(self, yen=0, btc=0):
        """
        Params:
            yen (int): initial yen the user have
            btc (int): initial btc the user have
        """
        self.yen = yen  # 現在所持している円の量
        self.btc = btc  # 現在所持しているBTCの量
        self.total = 0  # 現在の総資産額
        self.update_total_assets(btc)
        self.target = 0  # 次の予定売買価格
        self.traded_btc = 0  # 前回の取引価格
        """
        TODO:
        diff_target = |target - btc|
        diff_current = |target - traded_btc|

        action_chance = diff_current / diff_target # 理想値との差のうち、どの程度近づいているか
        """

    def buy_btc(self, price, amount):
        """
        Params:
            price (int): current price of BTC
            amount (float): amount of BTC to buy
        """
        self.yen -= price * amount
        self.btc += amount * (1 - bitbank_app.TRADING_FEE)
        self.update_total_assets(price)

    def sell_btc(self, price, amount):
        """
        Params:
            price (int): current price of BTC
            amount (float): amount of BTC to sell
        """
        self.btc -= amount
        self.yen += price * amount * (1 - bitbank_app.TRADING_FEE)
        self.update_total_assets(price)

    def update_total_assets(self, price):
        """
        Update user's total assets
        Params:
            price (int): current price of BTC
        """
        self.total = self.yen + self.btc * price

    def load_asset(self):
        """
        Load user's asset
        Params:
            price (int): current price of BTC
        """
        asset = AssetHistory.objects.order_by("-unixtime")[0]  # TODO: error handling
        self.yen = asset.yen
        self.btc = asset.btc
        self.total = asset.asset

    def decide_action(self, row):
        """
        Params:
            row: current data
        Returns:
            int: -1 for sell, 1 for buy, 0 otherwise
        """
        if row["predict"] > self.UPWARD_THRESHOLD:
            if self.yen > 0:
                return 1
        if row["predict"] < self.DOWNWARD_THRESHOLD:
            if self.btc > 0:
                return -1

        return 0

    def transact(self, row):
        """
        Params:
            row: current data
        """
        action = self.decide_action(row)
        if action == 1:
            amount = self.yen / row["close"]
            self.buy_btc(row["close"], amount)
        elif action == -1:
            amount = self.btc
            self.sell_btc(row["close"], amount)
