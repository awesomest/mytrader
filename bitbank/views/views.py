"""views.py"""
import datetime as dt
import pickle
from logging import getLogger, basicConfig, DEBUG
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
import pandas as pd  # pylint: disable=import-error
from . import dataset as ds
from . import bitcoin
from . import simulator

FORMATTER = "%(levelname)8s : %(asctime)s : %(message)s"
basicConfig(format=FORMATTER)
logger = getLogger(__name__)
logger.setLevel(DEBUG)


def index(request):
    """index"""
    return render(request, "bitbank/index.html")


def fetch(request):
    """fetch"""
    today = dt.date.today()
    tomorrow = dt.date.today() + dt.timedelta(1)
    date_range = ds.get_date_range(today, tomorrow)
    ds.save_all_candlestick(date_range)
    return HttpResponseRedirect(reverse("bitbank:results", args=("success",)))


def dataset(request, version):
    """dataset"""
    if version == "candlestick":
        return HttpResponseRedirect(reverse("bitbank:results", args=("failed",)))

    # TODO: Load from DB
    csv = pd.read_csv(
        "bitbank/static/bitbank/datasets/candlestick.csv"
    )  # TODO: Check error
    data = ds.set_dataset(csv, version)
    ds.plot(data, version)
    return redirect("/static/bitbank/graphs/" + version + "_dataset.png")


def train(request, version):
    """train"""
    csv = pd.read_csv("bitbank/static/bitbank/datasets/latest.csv")
    # 最後20%のデータでテスト
    test_ratio = 0.2
    test_start = int(len(csv) * (1 - test_ratio))
    csv = csv[:test_start]

    (data_train, _, label_train, _) = bitcoin.set_train_test_dataset(csv, test_ratio)
    model = bitcoin.create_model(data_train, label_train)

    pickle_file = "bitbank/static/bitbank/models/" + version + ".pickle"
    with open(pickle_file, mode="wb",) as file:
        pickle.dump(model, file)

    bitcoin.plot(csv, model, version)
    return redirect("/static/bitbank/graphs/" + version + "_predict.png")


def simulate(request, version):
    """simulate"""
    csv = pd.read_csv("bitbank/static/bitbank/datasets/latest.csv")

    pickle_file = "bitbank/static/bitbank/models/" + version + ".pickle"
    with open(pickle_file, mode="rb") as file:
        model = pickle.load(file)

    # 最後20%のデータでテスト
    test_ratio = 0.2
    test_start = int(len(csv) * (1 - test_ratio))
    data = csv[test_start:]

    _s = simulator.BitcoinSimulator(200000)

    y_assets = _s.simulate(data, model)
    print(y_assets[-1])

    simulator.plot(data, model, y_assets, version + "_simulate")
    return redirect("/static/bitbank/graphs/" + version + "_predict.png")


def results(request, results_str):
    """results"""
    return render(request, "bitbank/results.html", {"results": results_str})
