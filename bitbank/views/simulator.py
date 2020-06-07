"""simulator.py"""
import inspect
from logging import getLogger, basicConfig, DEBUG
import matplotlib  # pylint: disable=import-error
import matplotlib.pyplot as plt  # pylint: disable=import-error,wrong-import-position
from . import graph  # pylint: disable=relative-beyond-top-level

matplotlib.use("Agg")
from . import bitcoin  # pylint: disable=wrong-import-position,relative-beyond-top-level
from . import user  # pylint: disable=wrong-import-position,relative-beyond-top-level

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
        self.user = user.BitcoinUser(yen)

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
                # TODO: fix ratio. good to reset index?
                logger.info("  index: {:.2%}".format(index / len(data_simulation)))

            self.user.transact(row)
            assets.append(self.user.total)

        return assets


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

    plt.savefig("bitbank/static/bitbank/graphs/" + file_name + "_simulate.png")
