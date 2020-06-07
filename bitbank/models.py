"""models.py"""
from django.db import models


class Candlestick(models.Model):
    """Candlestick"""

    unixtime = models.PositiveIntegerField(unique=True)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()

    def __str__(self):
        # pylint: disable=invalid-str-returned
        return str(self.unixtime)


class Prediction(models.Model):
    """Prediction"""

    unixtime = models.PositiveIntegerField(unique=True)
    price = models.FloatField()  # btc price with yen
    # TODO: Add currency name to support others

    def __str__(self):
        # pylint: disable=invalid-str-returned
        return str(self.unixtime)


class Trade(models.Model):
    """Trade"""

    unixtime = models.PositiveIntegerField(unique=True)
    side = models.CharField(max_length=8)  # "buy" or "sell"
    price = models.FloatField()  # price of btc with yen
    amount = models.FloatField()  # btc amount

    def __str__(self):
        # pylint: disable=invalid-str-returned
        return str(self.unixtime)


class AssetHistory(models.Model):
    """AssetHistory"""

    unixtime = models.PositiveIntegerField(unique=True)
    yen = models.FloatField()  # price of yen
    btc = models.FloatField()  # price of btc with yen
    asset = models.FloatField()  # btc amount

    def __str__(self):
        # pylint: disable=invalid-str-returned
        return str(self.unixtime)
