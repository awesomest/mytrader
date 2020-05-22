"""
create_model.py
"""

import pickle
import pandas as pd
import matplotlib.pyplot as plt
from mylib import bitcoin
from mylib import graph


def plot(data, model, file_name):
    """
    :param data:
    :param model:
    :param file_name:
    :return:
    """

    _, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))

    graph.plot_close(data, ax1)
    graph.plot_predict(data, model, ax1)

    data2 = data[-500:]
    graph.plot_close(data2, ax2)
    graph.plot_predict(data2, model, ax2)

    plt.savefig("graphs/" + file_name + ".png")


def main():
    """
    :return:
    """

    file_name = "v0.0.13"
    csv = pd.read_csv("datasets/" + file_name + ".csv")
    # 最後20%のデータでテスト
    test_ratio = 0.2
    test_start = int(len(csv) * (1 - test_ratio))
    csv = csv[:test_start]

    (data_train, _, label_train, _) = bitcoin.set_train_test_dataset(csv, test_ratio)
    model = bitcoin.create_model(data_train, label_train)

    with open("models/" + file_name + ".pickle", mode="wb") as file:
        pickle.dump(model, file)

    # Check
    bitcoin.calc_avg_score(csv)
    plot(csv, model, file_name + "_predict")


if __name__ == "__main__":
    main()
