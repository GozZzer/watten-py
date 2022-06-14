import socket
import pickle

import tools


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
            return None
        case "CLOSE":
            exit()
        case _:
            return data


def connect_to_server(host: str = "localhost", port: int = 5643):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s


if __name__ == '__main__':
    try:
        sock = connect_to_server()
        while True:
            msg = wait_for_message(sock)
            if msg is not None:
                print(msg)
    except ConnectionResetError:
        print("The server closed")
