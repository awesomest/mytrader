"""
simulate_trading.py
"""

import pickle
import pandas as pd
import matplotlib.pyplot as plt
from mylib import simulator
from mylib import graph


def plot(data, model, y_assets, file_name):
    """
    :param data:
    :param model:
    :param y_assets:
    :param file_name:
    :return:
    """

    _, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
    graph.plot_close(data, ax1)
    graph.plot_predict(data, model, ax1)
    ax2.plot(list(range(len(data))), y_assets, label="assets")
    ax2.legend()

    plt.savefig("graphs/" + file_name + ".png")


def main():
    """
    :return:
    """

    file_name = "v0.0.13"
    csv = pd.read_csv("datasets/" + file_name + ".csv")

    with open("models/" + file_name + ".pickle", mode="rb") as file:
        model = pickle.load(file)

    # 最後20%のデータでテスト
    test_ratio = 0.2
    test_start = int(len(csv) * (1 - test_ratio))
    data = csv[test_start:]

    _s = simulator.BitcoinSimulator(200000)

    y_assets = _s.simulate(data, model)
    print(y_assets[-1])

    plot(data, model, y_assets, file_name + "_simulate")


if __name__ == "__main__":
    main()
