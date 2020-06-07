"""user.py"""

from . import bitbank_app  # pylint: disable=relative-beyond-top-level


class BitcoinUser:
    """
    BitcoinUser
    """

    def __init__(self, yen):
        """
        Params:
            yen (int): initial yen the user have
        """
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
