import socket
import pickle
import threading
import queue

from objects import Client, Task


class Server:
    def __init__(self):
        self.server: socket.socket | None = None
        self.host: str | None = None
        self.port: int | None = None
        self.connected_user: list[Client] = []

        self.tasks: queue.Queue | None = None
        self.new_clients: queue.PriorityQueue | None = None
        self.lock: threading.Lock | None = None

        self.new_client_handling_threads = []
        self.task_handler_threads = []
        self.client_receiver_threads = []

    def start_server(self, host: str = "localhost", port: int = 5643):
        print(f"[Server] Creating the Socket")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host, port))
        server.listen()
        print(f"[Server] Listening on {host}:{port}")
        self.server = server
        self.host = host
        self.port = port

    def setup_queues(self):
        print("[Queue] Creating the Queues (new_clients, tasks)")
        self.new_clients = queue.Queue()
        self.tasks = queue.PriorityQueue()
        print("[Queue] Creating the Lock")
        self.lock = threading.Lock()

    def setup_new_client_handler_threads(self, handle_new_clients_amount: int = 5):
        print(f"[Thread] Creating the NewClientHandler ({handle_new_clients_amount})")
        for i in range(handle_new_clients_amount):
            new_client = threading.Thread(name=f"NewClientHandler-{i}", target=self.handle_new_client)
            new_client.start()

    def setup_task_handler_threads(self, task_handler_amount: int = 5):
        print(f"[Thread] Creating the TaskHandler ({task_handler_amount})")
        for i in range(task_handler_amount):
            task_handler = threading.Thread(name=f"TaskHandler-{i}", target=self.handle_task)
            task_handler.start()

    def setup_accept_client_handler_threads(self, accept_client_handler_amount: int = 5):
        print(f"[Thread] Creating the AcceptClientHandler ({accept_client_handler_amount})")
        for i in range(accept_client_handler_amount):
            new_client = threading.Thread(name=f"AcceptClientHandler-{i}", target=self.accept_clients)
            new_client.start()

    def accept_clients(self):
        while True:
            conn, addr = self.server.accept()
            self.new_clients.put((conn, addr))

    def handle_new_client(self):
        while True:
            connection, address = self.new_clients.get()
            client_receiver = threading.Thread(name=f"Receiver", target=self.receive_from_client, args=(connection,))
            self.client_receiver_threads.append(client_receiver)
            client_receiver.start()
            connection, address = None, None

    def receive_from_client(self, connection: socket.socket):
        try:
            self.send(connection, "NODE")
            node = self.recv(connection)
            user = Client.get_user_by_node(node)
            if user in self.connected_user:
                self.send(connection)
            else:
                self.send(connection, user)
                self.connected_user.append(user)
            while True:
                task: Task = self.recv(connection)
                task.set_connection(connection)
                self.tasks.put((task.priority, task))
        except (ConnectionResetError, EOFError):
            disconnect_task: Task = Task(task_type="DISCONNECTED", connection=connection, priority=100)
            self.tasks.put((disconnect_task.priority, disconnect_task))
            return

    def handle_task(self):
        while True:
            if self.tasks.not_empty:
                priority, task = self.tasks.get()
                task.do_task()

    @staticmethod
    def send(conn: socket.socket, data: str = None):
        dta = pickle.dumps(data)
        length = dta.__sizeof__()
        try:
            conn.sendall(pickle.dumps(length))
            ack = conn.recv(32)
            if pickle.loads(ack) == "ACK":
                conn.sendall(dta)
            else:
                raise Exception(f"Couldnt send data ({data})")
        except ConnectionResetError:
            print("The Connection Stopped")
            exit()

    @staticmethod
    def recv(conn: socket.socket):
        length = pickle.loads(conn.recv(128))
        conn.sendall(pickle.dumps("ACK"))
        data = conn.recv(length)
        return pickle.loads(data)

    def run(self):
        self.start_server()
        self.setup_queues()
        self.setup_accept_client_handler_threads()
        self.setup_new_client_handler_threads()

        while True:
            task = Task(task_type=input("Your Task"), connection=None, priority=0)
            self.tasks.put((task.priority, task))

    def stop(self):
        self.server.close()


if __name__ == "__main__":
    server = Server()
    try:
        server.run()
    except KeyboardInterrupt:
        server.stop()
