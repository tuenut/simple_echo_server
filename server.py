import socket
from contextlib import contextmanager
from time import sleep

from loguru import logger


class SimpleEchoServer:
    __serving: bool = False
    __connections: dict = None

    def __init__(self, address: str = None, port: int = 5000):
        self.__address = address or socket.gethostname()
        self.__port = port
        self.__connections = {}

    @contextmanager
    def __open_socket(self):
        if self.__serving:
            raise Exception("Already serving.")

        self.__create_socket()
        self.__bind()

        yield self.__socket

        self.__close()

    def __create_socket(self):
        logger.info("Creating socket.")
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__socket.setblocking(False)

    def __bind(self):
        logger.info("Binding address.")
        self.__socket.bind((self.__address, self.__port))
        self.__socket.listen(5)
        self.__serving = True

    def __close(self):
        self.__close_connections()
        logger.info("Closing socket.")
        self.__socket.close()
        self.__serving = False

    def __close_connections(self):
        logger.info("Closing all connections.")
        for client in list(self.__connections.keys()):
            self.__close_connection(client)

    def run(self):
        with self.__open_socket():
            try:
                self.__main_loop()
            except KeyboardInterrupt:
                logger.info("Server stopped by user.")
            except:
                logger.exception("Server unexpected stop.")

    def __main_loop(self):
        while self.__serving:
            self.__accept_connection()
            self.__handle_connections()
            sleep(0.5)

    def __accept_connection(self):
        try:
            connection, address = self.__socket.accept()
        except BlockingIOError:
            pass
        else:
            logger.info(f"Client from <{address}> connected.")
            connection.setblocking(False)
            self.__connections[address] = connection

    def __handle_connections(self):
        for client in list(self.__connections.keys()):
            self.__handle_connection(client)

    def __handle_connection(self, client):
        conn = self.__connections[client]

        try:
            message = conn.recv(4096)
        except BlockingIOError:
            return
        else:
            logger.info(f"Receive: {message}")

        if message in [b"q\r\n", b'\xff\xf4\xff\xfd\x06', b'\xff\xfb\x06']:
            self.__close_connection(client)
        else:
            conn.send(message)

    def __close_connection(self, client):
        logger.info(f"Close connection with <{client}>.")
        conn = self.__connections[client]
        conn.send(b"Bye!\r\n")
        conn.close()
        del self.__connections[client]
