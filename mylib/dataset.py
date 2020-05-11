"""
dataset.py
"""
import inspect
from logging import getLogger, basicConfig, DEBUG
from datetime import datetime as dt
import pandas as pd  # pylint: disable=import-error
from scipy.stats import linregress  # pylint: disable=import-error

FORMATTER = "%(levelname)8s : %(asctime)s : %(message)s"
basicConfig(format=FORMATTER)
logger = getLogger(__name__)
logger.setLevel(DEBUG)

MINUTES_OF_HOURS = 60 * 1  # TODO: 最適な時間を要調査


class BitcoinDataset:
    """
    BitcoinDataset
    """

    def __init__(self, version):
        self.version = version
        self.data = None

    def set_dataset(self, csv):
        """
        データセットを作成
        Params:
            csv (dataframe): originalデータ
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        self.data = csv.sort_values(["unixtime"])
        self.add_column_trend()
        self.add_column_extreme_60_later()
        # self.add_column_trend_60_later()  # TODO: 不要になったら削除
        self.add_columns_close_ratio()
        self.add_columns_time()
        self.convert_hlc_to_ratio()
        self.remove_missing_rows()
        self.data.to_csv("datasets/" + str(self.version) + ".csv", index=False)
        logger.info("end: {:s}".format(inspect.currentframe().f_code.co_name))

    def add_column_extreme_60_later(self):
        """
        現在から60分後までの最大値or最小値を追加
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        if "extreme60" in self.data.columns:
            return

        for index, row in self.data.iterrows():
            if index % 10000 == 0:
                logger.info("  index: {:.2%}".format(index / len(self.data)))
            last_index = index + MINUTES_OF_HOURS
            if last_index > len(self.data):
                continue

            data_in_hours = self.data[["high", "low"]][index:last_index]
            highest = data_in_hours["high"].max()
            lowest = data_in_hours["low"].min()
            diff_highest = highest - row["open"]
            diff_lowest = row["open"] - lowest

            if diff_highest > diff_lowest:
                extreme60 = highest / row["open"]
            else:
                extreme60 = lowest / row["open"]

            self.data.at[index, "extreme60"] = extreme60

        self.data.to_csv("datasets/" + str(self.version) + ".csv", index=False)

    def add_columns_time(self):
        """
        現在日時に関する列を追加
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        if "second" in self.data.columns:
            return

        timestamp = pd.Series([dt.fromtimestamp(i) for i in self.data["unixtime"]])
        self.data["day"] = timestamp.dt.day
        self.data["weekday"] = timestamp.dt.dayofweek
        self.data["second"] = (timestamp.dt.hour * 60 + timestamp.dt.minute) * 60
        self.data.drop(columns=["unixtime"], inplace=True)
        self.data.to_csv("datasets/" + str(self.version) + ".csv", index=False)

    def remove_missing_rows(self):
        """
        欠損値を除外する
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        self.data.dropna(inplace=True)

    def add_column_trend(self):
        """
        60分前から現在までのトレンドを追加
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        if "trend" in self.data.columns:
            return

        for index, _ in self.data.iterrows():
            if index % 10000 == 0:
                logger.info("  index: {:.2%}".format(index / len(self.data)))
            first_index = index - MINUTES_OF_HOURS
            if first_index < 0:
                continue

            data_in_hours = self.data[["close"]][first_index:index]

            _x = list(range(len(data_in_hours)))
            trend_line = linregress(x=_x, y=data_in_hours["close"])
            self.data.at[index, "trend"] = trend_line[0] / data_in_hours["close"].iat[0]

        self.data.to_csv("datasets/" + str(self.version) + ".csv", index=False)

    def add_column_trend_60_later(self):
        """
        現在から60分後までのトレンドを追加
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        if "trend60" in self.data.columns:
            return

        self.data["trend60"] = self.data["trend"].shift(-1 * MINUTES_OF_HOURS)
        self.data.to_csv("datasets/" + str(self.version) + ".csv", index=False)

    def add_columns_close_ratio(self):
        """
        指定した時間前のclose_ratioを現在のopenに対する割合として追加
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        minute_list = [1, 2, 5, 10, 15, 30, 60, 120, 240, 480, 720, 1440, 2880, 10080]
        for i in minute_list:
            name = "close_ratio-" + str(i)
            if name in self.data.columns:
                continue

            self.data[name] = self.data["close"].shift(i)
            self.data[name] = self.data[name] / self.data["open"]
            self.data.to_csv("datasets/" + str(self.version) + ".csv", index=False)

    def convert_hlc_to_ratio(self):
        """
        価格データをopenに対する割合として追加
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        columns = ["high", "low", "close"]
        for column in columns:
            name = column + "_ratio"
            if name in self.data.columns:
                continue

            self.data[name] = self.data[column] / self.data["open"]
            self.data.to_csv("datasets/" + str(self.version) + ".csv", index=False)
