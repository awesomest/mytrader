"""
dataset.py
"""
import inspect
from logging import getLogger, basicConfig, DEBUG
from datetime import datetime as dt
import pandas as pd  # pylint: disable=import-error
import numpy as np  # pylint: disable=import-error
from scipy.stats import linregress  # pylint: disable=import-error
from scipy import signal  # pylint: disable=import-error

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
        self.data = csv
        self.convert_hlc_to_log()
        # self.add_column_trend()  # TODO: 不要になったら削除
        # self.add_column_extreme_60_later()  # TODO: 不要になったら削除
        # self.add_column_trend_60_later()  # TODO: 不要になったら削除
        self.add_column_next_extreme()
        self.add_columns_close_log()
        self.add_columns_time()
        self.remove_missing_rows()
        self.data.to_csv("datasets/" + str(self.version) + ".csv", index=False)
        logger.info("end: {:s}".format(inspect.currentframe().f_code.co_name))

    def add_column_extreme_60_later(self):
        """
        現在から60分後までの最大値or最小値を追加
        TODO: dataframe.rolling を使用する
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

            # TODO: closeの最大・最小でも要確認
            data_in_hours = self.data[["high", "low"]][index:last_index]
            highest_index = data_in_hours["high"].idxmax()
            highest = data_in_hours["high"][highest_index]
            lowest_index = data_in_hours["low"].idxmin()
            lowest = data_in_hours["low"][lowest_index]

            if highest_index < lowest_index:
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
        # self.data.drop(columns=["unixtime"], inplace=True)
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

    def add_columns_close_log(self):
        """
        指定した時間前のclose_logの差を追加
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        minute_list = [1, 2, 5, 10, 15, 30, 60, 120, 240, 480, 720, 1440, 2880, 10080]
        for i in minute_list:
            name = "close_log-" + str(i)
            if name in self.data.columns:
                continue

            self.data[name] = self.data["close_log"].diff(periods=i)
            self.data.to_csv("datasets/" + str(self.version) + ".csv", index=False)

    def convert_hlc_to_log(self):
        """
        価格データをopenに対する割合として追加
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        columns = ["open", "high", "low", "close"]
        for column in columns:
            name = column + "_log"
            if name in self.data.columns:
                continue

            self.data[name] = np.log(self.data[column])
            self.data.to_csv("datasets/" + str(self.version) + ".csv", index=False)

    def add_column_next_extreme(self):
        """
        期間n分の極大値・極小値
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        column_name = "next_extreme_log"
        if column_name in self.data.columns:
            return

        _y = self.data["close_log"].values
        max_ids = signal.argrelmax(_y, order=1)
        min_ids = signal.argrelmin(_y, order=1)
        max_min_ids = np.concatenate([max_ids[0], min_ids[0]])
        max_min_ids = np.sort(max_min_ids)
        next_idx = 0
        for index, row in self.data.iterrows():
            if index % 10000 == 0:
                logger.info("  index: {:.2%}".format(index / len(self.data)))

            if next_idx >= len(max_min_ids):
                break

            _ni = max_min_ids[next_idx]
            if index >= _ni:
                next_idx += 1
            self.data.at[index, column_name] = (
                self.data.at[_ni, "close_log"] - row["open_log"]
            )
