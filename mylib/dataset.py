from datetime import datetime as dt

minutes_of_hours = 60 * 6 # TODO: 最適な時間を要調査

class BitcoinDataset:
    def __init__(self, csv):
        #csv = csv[1645000:]
        csv = csv.reset_index()
        csv = csv[['unixtime', 'open', 'close', 'low', 'high', 'volume']]
        self.data = csv.sort_values(['unixtime'])
        self.format()
        self.add_result()
        self.add_column_diff_all(3)
        self.remove_missing_rows()

    def format(self):
        self.data['timestamp'] = [dt.fromtimestamp(l) for l in self.data['unixtime']]
        self.data['result'] = 0

    def remove_missing_rows(self):
        last = max(0, len(self.data) - minutes_of_hours)
        self.data = self.data.loc[2:last] # remove rows includes NaN or result=0

    # 目的変数を設定
    # 以後6時間の最適解を求める
    def add_result(self):
        for index, row in self.data.iterrows():
            if index + minutes_of_hours >= len(self.data):
                break

            last_index = index + minutes_of_hours
            data_in_hours = self.data[index:last_index]
            current_average = (row['high'] + row['low']) / 2

            highest_index    = data_in_hours['high'].idxmax() # 最大の高値を取得
            highest          = data_in_hours['high'][highest_index]
            highest_unixtime = data_in_hours['unixtime'][highest_index]
            # 5%未満の変動は無視する
            if highest < current_average * 1.05:
                highest_gradient = float('inf')
            else:
                highest_gradient = max([0, self.calc_gradient(row['unixtime'], current_average, highest_unixtime, highest)])

            lowest_index    = data_in_hours['low'].idxmin() # 最小の安値を取得
            lowest          = data_in_hours['low'][lowest_index]
            lowest_unixtime = data_in_hours['unixtime'][lowest_index]
            # 5%未満の変動は無視する
            if lowest > current_average * 0.95:
                lowest_gradient = float('inf')
            else:
                lowest_gradient = max([0, -1 * self.calc_gradient(row['unixtime'], current_average, lowest_unixtime, lowest)])

            # 次のX時間での最大値 or 最小値を目的変数として設定する
            # 傾きが大きい方を目的変数に設定する
            if highest_gradient > lowest_gradient:
                self.data.at[index, 'result'] = highest
            else:
                self.data.at[index, 'result'] = lowest

    def calc_gradient(self, x1, y1, x2, y2):
        if x2 == x1:
            return float('inf')
        return (y2 - y1) / (x2 - x1)

    def add_column_diff_all(self, n):
        for i in list(range(1, n)):
            self.set_column_diff_i(i)

    def set_column_diff_i(self, i):
        name = 'diff' + str(i)
        self.data[name] = self.data['open'].shift(i)

