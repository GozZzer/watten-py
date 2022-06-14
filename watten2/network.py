import logging
import random
import socket
import sys
from threading import Thread
from multiprocessing.pool import ThreadPool
import threading

from watten2 import tools


class WattenClient:
    def __init__(self, client_id: int, status: str = "waiting", game_id: int = None, connection: socket.socket = None, address: str = None, port: int = None):
        self.client_id: int = client_id
        self.client_name: str | None = None
        self.status: str = status
        self.game_id: int | None = game_id
        self.connection: socket.socket = connection
        self.address: str = address
        self.port: int = port

    def __repr__(self):
        return f"<WattenClient [{self.status}] client_id: {self.client_id}, game_id: {self.game_id}, address: {self.address}>"

    def send(self, message: str = None):
        tools.send(self.connection, message)

    @staticmethod
    def receive(conn: socket.socket):
        return tools.receive(conn)

class GameMaster:
    # __slots__ = ["address", "port", "server", "waiting_clients", "playing_clients", "log", "logger", "logging"]
    """
    The GameMaster will be the head of a Server so Games are running on a GameMaster.                                                       
    The GameMaster is able to execute changes on a Game and View all attributes of any game.
    He got an overview of all the current games, clients, ...
    """

    def __init__(self, address: str = "localhost", port: int = 5643, server: socket.socket = None, log: bool = True, logger: logging.Logger = None, max_games: int = 4):
        self.address: str = address
        self.port: int = port
        self.server: socket.socket | None = server
        self.waiting_clients: list[WattenClient] = []
        self.playing_clients: list[list[WattenClient]] = []
        self.accept_client_pool: list[ThreadPool] = [ThreadPool(4) for _ in range(max_games)]
        print(self.accept_client_pool[0])
        self.logging: bool = log
        self.logger: logging.Logger = logger
        if server is None:
            self.setup_server()

    def setup_server(self, max_connections: int = 20) -> None:
        """
        Set up the server of the GameMaster if there is no server set
        Binds the server to the address/port

        :param max_connections: The amount of Connections the server listens to
        :return: None
        """
        if not self.server:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.address, self.port))
        self.server.listen(max_connections)
        if self.logging is True:
            self.logger.info(f"A New server socket got created running on {self.address}/{self.port} (Listening to {max_connections} clients)")

    def allow_clients_to_join(self, client_amount: int = 4) -> None:
        thread = threading.Thread(target=self.wait_for_full_games)
        thread.start()
        current_player = len(self.waiting_clients) + len(self.playing_clients)
        outp = self.accept_client_pool[0].map(self.accept_client, range(current_player + 1, current_player + 1 + client_amount))
        self.accept_client_pool[0].
        print(self.playing_clients)
        print("accept")
        """for i in range(current_player + 1, current_player + 1 + client_amount):
            
            thread = threading.Thread(target=self.accept_client, args=(i,), name=f"Thread-ACTJ")
            thread.start()
        if self.logging is True:
            self.logger.info("4 new threads were created to allow clients to join the server")
        for thre in [th for th in threading.enumerate() if th.name == "Thread-ACTJ"]:
            thre.join()
            if self.logging is True:
                self.logger.info(f"Connection from {self.waiting_clients[-1].address}")"""

    def wait_for_full_games(self):
        player = []
        game_id = len(self.playing_clients)
        while len(self.waiting_clients) < 4:
            for client in self.waiting_clients[0:4]:
                player.append(client)

            self.playing_clients.append(player)
        self.waiting_clients = self.waiting_clients[4:]
        thread = threading.Thread(target=self.start_game, args=(game_id, player,))
        thread.start()
        if self.logging is True:
            self.logger.info(f"A new Game Starts")
        thread.join()

    def accept_client(self, client_id: int = None):
        if not client_id:
            client_id = random.randint(1000, 9999)
        connection, address = self.server.accept()
        return WattenClient(client_id, connection=connection, address=address[0], port=address[1])
        # self.waiting_clients.append(WattenClient(client_id, connection=connection, address=address[0], port=address[1]))

    def start_game(self, game_id: int, clients: list[WattenClient]):
        for client in clients:
            client.send("Welcome to Watten-py")
