"""
btc_api.py
"""
import inspect
import datetime as dt
from logging import getLogger, basicConfig, DEBUG
import python_bitbankcc  # pylint: disable=import-error
import mysql.connector  # pylint: disable=import-error

FORMATTER = "%(levelname)8s : %(asctime)s : %(message)s"
basicConfig(format=FORMATTER)
logger = getLogger(__name__)
logger.setLevel(DEBUG)


class DbHandler:
    """
    DbHandler
    """

    DB_HOST = "localhost"
    DB_PORT = "4306"
    DB_USER = "eraise"
    DB_PASSWORD = "eraise"
    DB_DATABASE = "eraise"

    def __init__(self):
        logger.info(
            "start: DbHandler.{:s}".format(inspect.currentframe().f_code.co_name)
        )
        self.conn = mysql.connector.connect(
            host=self.DB_HOST,
            port=self.DB_PORT,
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            database=self.DB_DATABASE,
        )
        self.cursor = self.conn.cursor()

    def insert(self, query: str, data: list):
        """
        Params:
            query (str): string of query
            data (list): list of candlestick
        """
        self.cursor.executemany(query, data)
        self.conn.commit()

    def select(self, query):
        """
        Params:
            query (str): string of query
        Returns:
            list: records
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def __exit__(self, exc_type, exc_value, traceback):
        logger.info(
            "start: DbHandler.{:s}".format(inspect.currentframe().f_code.co_name)
        )
        self.cursor.close()
        self.conn.close()


class CandlestickHandler:
    """
    CandlestickHandler
    """

    def __init__(self):
        logger.info(
            "start: DbHandler.{:s}".format(inspect.currentframe().f_code.co_name)
        )

    # pylint: disable=no-self-use
    def insert_candlestick(self, data: list):
        """
        Params:
            data (list): list of candlestick
        """
        query = (
            "INSERT INTO candlestick"
            "(open, high, low, close, volume, unixtime) "
            "VALUES (%s, %s, %s, %s, %s, %s)"
        )
        _dh.insert(query, data)

    # pylint: disable=no-self-use
    def select_unsaved_date(self):
        """
        Select last unixtime
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        query = "SELECT unixtime FROM candlestick ORDER BY unixtime DESC LIMIT 1"
        rows = _dh.select(query)
        oldest_date = dt.date(2017, 2, 14)  # TODO: 適当に決めた日付なので要改善
        if len(rows) > 0:
            saved_unixtime = rows[0][0]
            saved_datetime = dt.datetime.fromtimestamp(saved_unixtime)
            unsaved_date = dt.date(
                saved_datetime.year, saved_datetime.month, saved_datetime.day + 1
            )
            return max(oldest_date, unsaved_date)

        return oldest_date

    # pylint: disable=no-self-use
    def fetch_candlestick(self, date_str: str):
        """
        Params:
            date_str (str): string of date
        Returns:
            list: all of list of candlestick
        """
        pub = python_bitbankcc.public()

        value = pub.get_candlestick("btc_jpy", "1min", date_str)

        candlestick = value["candlestick"][0]["ohlcv"]
        return candlestick

    def fetch_candlestick_daily(self, date_str: str):
        """
        Params:
            date_str (str): string of date
        Returns:
            list: list of daily candlestick
        """
        candlestick = self.fetch_candlestick(date_str)
        candlestick_list = []
        for ohlcv in candlestick:
            data = (ohlcv[0], ohlcv[1], ohlcv[2], ohlcv[3], ohlcv[4], ohlcv[5] / 1000)
            candlestick_list.append(data)

        return candlestick_list

    def save_all_candlestick(self):
        """
        Insert all candlesticks into DB
        """
        logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
        unsaved_date = self.select_unsaved_date()
        yesterday = dt.date.today() + dt.timedelta(-1)
        date_range = get_date_range(unsaved_date, yesterday)
        for date in date_range:
            logger.info("date: {:%Y-%m-%d}".format(date))
            date_str = date.strftime("%Y%m%d")
            cv_list = self.fetch_candlestick_daily(date_str)
            self.insert_candlestick(cv_list)


def get_date_range(start_date: dt.datetime, stop_date: dt.datetime):
    """
    Params:
        start_date (datetime): date of start.
        stop_date (datetime): date of end. it's not included.
    Returns:
        list: list of string of date
    """
    logger.info("start: {:s}".format(inspect.currentframe().f_code.co_name))
    diff = (stop_date - start_date).days
    return (start_date + dt.timedelta(i) for i in range(diff))


_dh = DbHandler()


def main():
    """
    main
    """
    _ch = CandlestickHandler()
    _ch.save_all_candlestick()


if __name__ == "__main__":
    main()
