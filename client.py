import pickle
import socket

from watten2 import tools


def wait_for_message(s: socket.socket):
    data = tools.receive(s)
    match data:
        case "INPUT":
            inp = None
            while not inp:
                inp = input()
            tools.send(s, inp)
            return None
        case "PICKLE":
            data = pickle.loads(tools.receive(s, True))
            if isinstance(data, list):
                tools.display_cards(data)
            return None
        case "CLOSE":
            exit()
        case _:
            return data


def connect_to_server(host: str = "localhost", port: int = 5643):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
        return s
    except ConnectionRefusedError:
        print("The Server is currently not waiting for new connections.")
        exit()


if __name__ == '__main__':
    try:
        sock = connect_to_server()
        while True:
            msg = wait_for_message(sock)
            if msg is not None:
                print(msg)
    except ConnectionResetError:
        print("The server closed")
