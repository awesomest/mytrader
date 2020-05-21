"""
db.py
"""

import inspect
from logging import getLogger, basicConfig, DEBUG
import mysql.connector  # pylint: disable=import-error

FORMATTER = "%(levelname)8s : %(asctime)s : %(message)s"
basicConfig(format=FORMATTER)
logger = getLogger(__name__)
logger.setLevel(DEBUG)


class DbHandler:
    """
    DbHandler
    """

    # TODO: Set with env variables
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
