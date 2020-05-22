"""
create_data.py
"""

import pandas as pd
import matplotlib.pyplot as plt
from mylib import dataset
from mylib import graph


def plot(data, file_name):
    """
    :param data:
    :param file_name:
    :return:
    """

    _, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
    graph.plot_close(data, ax1)
    graph.plot_label(data, ax1)

    data2 = data[-500:]
    graph.plot_close(data2, ax2)
    graph.plot_label(data2, ax2)

    plt.savefig("graphs/" + file_name + ".png")


def main():
    """
    :return:
    """

    file_name = "v0.0.13-test"
    csv = pd.read_csv("datasets/v0.0.13.csv")
    _b = dataset.BitcoinDataset(file_name)
    _b.set_dataset(csv)

    _x = _b.data

    plot(_x, file_name + "_data")


if __name__ == "__main__":
    main()
