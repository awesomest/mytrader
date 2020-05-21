"""
btc_api.py
"""

from mylib import candlestick  # pylint: disable=import-error


def main():
    """
    main
    """
    _ch = candlestick.CandlestickHandler()
    _ch.save_all_candlestick()


if __name__ == "__main__":
    main()
