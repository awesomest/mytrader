"""
dataset.py
"""
from datetime import datetime as dt
import pandas as pd  # pylint: disable=import-error
from scipy.stats import linregress  # pylint: disable=import-error

MINUTES_OF_HOURS = 60 * 1  # TODO: 最適な時間を要調査


class BitcoinDataset:
    """
    BitcoinDataset
    """

    def __init__(self):
        self.data = None

    def set_dataset(self, csv):
        """
        データセットを作成
        Params:
            csv (dataframe): originalデータ
        """
        self.data = csv.sort_values(["unixtime"])
        self.add_columns_time()
        self.convert_hlc_to_ratio()
        self.add_column_trend()
        # self.add_column_trend_60_later()  # TODO: 不要になったら削除
        self.add_column_extreme_60_later()
        self.add_columns_close_ratio()
        self.remove_missing_rows()

    def set_dataset_for_test(self, csv):
        """
        TODO: テスト用なので、不要になったら削除
        テスト用データセット作成
        """
        self.data = csv
        self.rename_result_column()
        self.add_column_extreme_60_later()

    def add_column_extreme_60_later(self):
        """
        現在から60分後までの最大値or最小値を追加
        """
        for index, row in self.data.iterrows():
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

    def rename_result_column(self):
        """
        TODO: 一時的なものなので、不要になったら削除
        カラム名を変更
        """
        self.data = self.data.rename(columns={"result": "trend60"})

    def add_columns_time(self):
        """
        現在日時に関する列を追加
        """
        timestamp = pd.Series([dt.fromtimestamp(i) for i in self.data["unixtime"]])
        self.data["day"] = timestamp.dt.day
        self.data["weekday"] = timestamp.dt.dayofweek
        self.data["second"] = (timestamp.dt.hour * 60 + timestamp.dt.minute) * 60
        self.data.drop(columns=["unixtime"], inplace=True)

    def remove_missing_rows(self):
        """
        欠損値を除外する
        """
        self.data.dropna(inplace=True)

    def add_column_trend(self):
        """
        60分前から現在までのトレンドを追加
        """
        for index, _ in self.data.iterrows():
            first_index = index - MINUTES_OF_HOURS
            if first_index < 0:
                continue

            data_in_hours = self.data[["close"]][first_index:index]

            _x = list(range(len(data_in_hours)))
            trend_line = linregress(x=_x, y=data_in_hours["close"])
            self.data.at[index, "trend"] = trend_line[0] / data_in_hours["close"].iat[0]

    def add_column_trend_60_later(self):
        """
        現在から60分後までのトレンドを追加
        """
        self.data["result"] = self.data["trend"].shift(-1 * MINUTES_OF_HOURS)

    def add_columns_close_ratio(self):
        """
        指定した時間前のclose_ratioを現在のopenに対する割合として追加
        """
        minute_list = [1, 2, 5, 10, 15, 30, 60, 120, 240, 480, 720, 1440, 2880, 10080]
        for i in minute_list:
            name = "close_ratio" + str(i)
            self.data[name] = self.data["close_ratio"].shift(
                i
            )  # FIXME: 現在のopenに対する割合になっていない

    def convert_hlc_to_ratio(self):
        """
        価格データをopenに対する割合として追加
        """
        columns = ["high", "low", "close"]
        for column in columns:
            self.data[column + "_ratio"] = self.data[column] / self.data["open"]
