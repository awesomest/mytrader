"""apps.py"""
from django.apps import AppConfig


class BitbankConfig(AppConfig):
    """BitbankConfig"""

    name = "bitbank"

    def ready(self):
        """
        when Django starts.
        """
