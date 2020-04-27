from sklearn.linear_model import LinearRegression
import pickle

class BitcoinRegression:
    def __init__(self, csv):
        # TODO: select columus
        self.columns = ['unixtime', 'open', 'close', 'low', 'high', 'volume', 'diff1', 'diff2', 'result']
        csv = csv[self.columns][2:-60*6] # remove rows includes NaN or result=0
        self.data = csv.sort_values(['unixtime'])

    def predict(self, x):
        return self.model.predict(x)

    def train(self):
        self.model = LinearRegression()
        self.model.fit(self.data_train, self.label_train)

    def load_model(self, name):
        with open(name, mode='rb') as f:
            self.model = pickle.load(f)

    def save_model(self, name):
        with open(name, mode='wb') as f:
            pickle.dump(self.model, f)

    def calc_avg_pred(self):
        sum_score = 0
        test_percentage = 20
        test_ratio = test_percentage / 100
        times = 100 - test_percentage
        for i in range(times):
            start_ratio = i / 100
            self.set_train_test_dataset(start_ratio, test_ratio)
            self.train()
            ac_score = self.model.score(self.data_test, self.label_test)
            sum_score += ac_score

        return sum_score / times

    def set_train_test_dataset(self, start_ratio, test_ratio):
        """
        テストデータは１つの期間を使用する
        ランダムに抽出すると、直前・直後のデータがヒントになってしまうから。

        Parameters
        ----------
        start_ratio : float
        test_ratio: float
        """

        columns = self.columns.copy()
        columns.remove('result')

        test_start = int(len(self.data) * start_ratio)
        test_end = test_start + int(len(self.data) * test_ratio)

        self.data_train = self.data[columns][:test_start]
        self.data_train = self.data_train.append(self.data[columns][test_end:])
        self.data_test = self.data[columns][test_start:test_end]
        self.label_train = self.data['result'][:test_start]
        self.label_train = self.label_train.append(self.data['result'][test_end:])
        self.label_test = self.data['result'][test_start:test_end]

