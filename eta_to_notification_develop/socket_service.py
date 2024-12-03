import binascii
import os
import socket
import threading

from model.tracker import TrackerMessage
from utils.tracker_update import TrackerUpdate
from loguru import logger
from parser import parse
import datetime


class SocketService():
    # creation of the socket
    ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()  # Standard loopback interface address (localhost)
    port = 4440
    logger.info(port)

    def __init__(self) -> None:
        try:
            self.ServerSocket.bind((self.host, self.port))
            # self.ServerSocket.setblocking(False)
        except socket.error as e:
            logger.error(str(e))

        logger.debug(f'Waiting for a Connection on {self.host}:{self.port} ...')  # nopep8

        self.ServerSocket.listen(5)

    def client_thread(self, connection, address):
        logger.debug(f"Connected by {address}")
        cur_thread = threading.current_thread()
        while True:
            data = connection.recv(1024)
            if not data:
                break
            # logger.debug(f'Raw Bytes: {binascii.hexlify(data)}')
            # logger.debug(f'Current Thread: {cur_thread.name}')
            parsed_message = parse(data, address)
            # logger.info(parsed_message)
            if 'AVL_data' in parsed_message:
                # logger.info(parsed_message['AVL_data'])
                for data in parsed_message['AVL_data']:
                    tracker_update = TrackerMessage(**{
                        "lat": data['GPS_element']['latitude'],
                        "long": data['GPS_element']['longitude'],
                        "time": datetime.datetime.fromtimestamp(data['timestamp']/1000).strftime('%Y-%m-%dT%H:%M:%SZ')
                    })
                    logger.info(tracker_update)
                    update = TrackerUpdate.is_arrived(tracker_update)
                    logger.info(update)

    def run_forever(self):
        while True:
            Client, address = self.ServerSocket.accept()
            # logger.debug('Connected to: ' + address[0] + ':' + str(address[1]))
            # start_new_thread(self.client_thread, (Client, address, ))
            threading.Thread(target=self.client_thread,
                             args=(Client, address)).start()
            # ThreadCount += 1
            # print('Thread Number: ' + str(ThreadCount))
        self.ServerSocket.close()

    def close(self):
        self.ServerSocket.close()
