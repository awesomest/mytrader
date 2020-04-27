import python_bitbankcc
#import json
import mysql.connector
import datetime
#from datetime import timedelta, datetime, tzinfo

DB_HOST = 'localhost'
DB_PORT = '4306'
DB_USER = 'eraise'
DB_PASSWORD = 'eraise'
DB_DATABASE = 'eraise'

conn = mysql.connector.connect(
  host=DB_HOST,
  port=DB_PORT,
  user=DB_USER,
  password=DB_PASSWORD,
  database=DB_DATABASE
)

cursor = conn.cursor()


def insert_candlestic(data: list):
    query = ("INSERT INTO candlestick"
             "(open, high, low, close, volume, unixtime) "
             "VALUES (%s, %s, %s, %s, %s, %s)")
    cursor.executemany(query, data)
    conn.commit()


def fetch_candlestick(date_str: str):
    pub = python_bitbankcc.public()

    value = pub.get_candlestick(
        'btc_jpy',
        '1min', # TODO: 1min
        date_str # TODO: change
    )

    ohlcv = value["candlestick"][0]["ohlcv"]
    return ohlcv


def fetch_candlestick_daily(date_str: str):
    ohlcv = fetch_candlestick(date_str)
    cv_list = []
    for cv in ohlcv:
        data = (cv[0], cv[1], cv[2], cv[3], cv[4], cv[5]/1000)
        cv_list.append(data)

    return cv_list


def get_date_range(start_date: datetime.datetime, end_date: datetime.datetime):
    diff = (end_date - start_date).days + 1
    return (start_date + datetime.timedelta(i) for i in range(diff))


def save_all_candlestick():
    start_date = datetime.date(2017, 2, 14)
    end_date = datetime.date.today() + datetime.timedelta(-1)
    date_range = get_date_range(start_date, end_date)
    for d in date_range:
        print(d)
        date_str = d.strftime('%Y%m%d')
        cv_list = fetch_candlestick_daily(date_str)
        insert_candlestic(cv_list)


save_all_candlestick()

cursor.close()
conn.close()

