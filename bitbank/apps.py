"""apps.py"""
from django.apps import AppConfig

# from bitbank.views import bitbank_watch


class BitbankConfig(AppConfig):
    """BitbankConfig"""

    name = "bitbank"

    def ready(self):
        """
        when Django starts.
        """
        # bitbank_watch.sio.connect("wss://stream.bitbank.cc", transports=["websocket"])  # TODO:
