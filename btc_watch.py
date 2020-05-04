import json
import logging
import socketio

logging.basicConfig(
    level=logging.ERROR,
    filename="./try.log",
    format="%(levelname)s : %(asctime)s : %(message)s",
)
logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)

sio = socketio.Client(
    reconnection=True,
    reconnection_attempts=0,
    reconnection_delay=1,
    reconnection_delay_max=30,
    logger=True,
)
logger.info("Created socketio client")


@sio.event
def connect():
    logger.info("connected to server")
    sio.emit("join-room", "transactions_btc_jpy")


@sio.event
def message(data):
    logger.info("print message")
    print(json.dumps(data, indent=2))


@sio.event
def disconnect():
    logger.info("disconnected from server")


sio.connect("wss://stream.bitbank.cc", transports=["websocket"])
sio.wait()
