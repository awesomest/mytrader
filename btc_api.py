import datetime
import python_bitbankcc
import mysql.connector

DB_HOST = "localhost"
DB_PORT = "4306"
DB_USER = "eraise"
DB_PASSWORD = "eraise"
DB_DATABASE = "eraise"


conn = mysql.connector.connect(
    host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE
)

cursor = conn.cursor()


def insert_candlestic(data: list):
    query = (
        "INSERT INTO candlestick"
        "(open, high, low, close, volume, unixtime) "
        "VALUES (%s, %s, %s, %s, %s, %s)"
    )
    cursor.executemany(query, data)
    conn.commit()


def fetch_candlestick(date_str: str):
    pub = python_bitbankcc.public()

    value = pub.get_candlestick(
        "btc_jpy", "1min", date_str  # TODO: 1min  # TODO: change
    )

    candlestick = value["candlestick"][0]["ohlcv"]
    return candlestick


def fetch_candlestick_daily(date_str: str):
    candlestick = fetch_candlestick(date_str)
    candlestick_list = []
    for ohlcv in candlestick:
        data = (ohlcv[0], ohlcv[1], ohlcv[2], ohlcv[3], ohlcv[4], ohlcv[5] / 1000)
        candlestick_list.append(data)

    return candlestick_list


def get_date_range(start_date: datetime.datetime, end_date: datetime.datetime):
    diff = (end_date - start_date).days + 1
    return (start_date + datetime.timedelta(i) for i in range(diff))


def save_all_candlestick():
    start_date = datetime.date(2020, 4, 5)
    end_date = datetime.date.today() + datetime.timedelta(-1)
    date_range = get_date_range(start_date, end_date)
    for date in date_range:
        print(date)
        date_str = date.strftime("%Y%m%d")
        cv_list = fetch_candlestick_daily(date_str)
        insert_candlestic(cv_list)


save_all_candlestick()

cursor.close()
conn.close()
