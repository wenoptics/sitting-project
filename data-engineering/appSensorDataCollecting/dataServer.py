import json
import logging
from websocket_server import WebsocketServer

WS_PORT = 13254


def new_client(client, server):
    # server.send_message_to_all("")
    print('Phone connected', client)


def on_sensor_data_recv(client, server, message):
    """
    Recv sensor data message from Phone
    :param client:
    :param server:
    :param message:
    :return:
    """
    try:
        data = json.loads(message)
    except json.decoder.JSONDecodeError:
        print('raw message:', message)
    else:
        print(data)


server = WebsocketServer(WS_PORT, host='0.0.0.0', loglevel=logging.INFO)
server.set_fn_new_client(new_client)
server.set_fn_message_received(on_sensor_data_recv)
server.run_forever()
