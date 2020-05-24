"""models.py"""
from django.db import models


class Candlestick(models.Model):
    """Candlestick"""

    unixtime = models.PositiveIntegerField(unique=True)
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()

    def __str__(self):
        return self.unixtime
