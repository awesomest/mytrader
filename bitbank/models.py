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
