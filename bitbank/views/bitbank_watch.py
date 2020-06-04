"""bitbank_watch.py"""
import json
from logging import getLogger, basicConfig, DEBUG
import socketio

FORMATTER = "%(levelname)8s : %(asctime)s : %(message)s"
basicConfig(format=FORMATTER)
logger = getLogger(__name__)
logger.setLevel(DEBUG)

sio = socketio.Client(
    reconnection=True,
    reconnection_attempts=0,
    reconnection_delay=1,
    reconnection_delay_max=30,
    logger=True,
)


@sio.event
def connect():
    """
    Connect to server
    """
    logger.info("connected to server")
    sio.emit("join-room", "transactions_btc_jpy")


@sio.event
def message(data):
    """
    Message to server
    """
    logger.info("print message")
    logger.info(json.dumps(data, indent=2))


@sio.event
def disconnect():
    """
    Disconnect from server
    """
    logger.info("disconnected from server")
