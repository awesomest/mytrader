"""
simulator.py
"""
import inspect
from logging import getLogger, basicConfig, DEBUG
from mylib import bitbank  # pylint: disable=import-error
from mylib import bitcoin  # pylint: disable=import-error

FORMATTER = "%(levelname)8s : %(asctime)s : %(message)s"
basicConfig(format=FORMATTER)
logger = getLogger(__name__)
logger.setLevel(DEBUG)


class BitcoinSimulator:
    """
    BitcoinSimulator
    """

    def __init__(self, yen):
        """
        Params:
            yen (int): initial yen the user have
        """
        self.user = BitcoinUser(yen)

    def simulate(self, data, model):
        """
        Params:
            data (dataframe): all dataset to simulate
            model (model): data for model
        Return:
            dataframe: transition of assets
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        data_simulation = data.copy()
        data_simulation["predict"] = model.predict(data[bitcoin.TRAIN_COLUMNS])
        assets = []

        for index, row in data_simulation.iterrows():
            if index % 10000 == 0:
                logger.info("  index: {:.2%}".format(index / len(data_simulation)))
            action = self.decide_action(row)
            if action == 1:
                amount = self.user.yen / row["close"]
                self.user.buy_btc(row["close"], amount)
            elif action == -1:
                amount = self.user.btc
                self.user.sell_btc(row["close"], amount)

            assets.append(self.user.total)

        return assets

    def decide_action(self, row):
        """
        Params:
            row: current data
        Returns:
            int: -1 for sell, 1 for buy, 0 otherwise
        """
        if row["predict"] > 1.005:  # upward trend # TODO: Decide the threshold
            if self.user.yen > 0:
                return 1
        if row["predict"] < 0.995:  # downward # TODO: Decide the threshold
            if self.user.btc > 0:
                return -1

        return 0


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
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        self.yen -= price * amount
        self.btc += amount * (1 - bitbank.TRADING_FEE)
        self.update_total_assets(price)

    def sell_btc(self, price, amount):
        """
        Params:
            price (int): current price of BTC
            amount (float): amount of BTC to sell
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        self.btc -= amount
        self.yen += price * amount * (1 - bitbank.TRADING_FEE)
        self.update_total_assets(price)

    def update_total_assets(self, price):
        """
        Update user's total assets
        Params:
            price (int): current price of BTC
        """
        self.total = self.yen + self.btc * price
