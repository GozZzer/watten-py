import math
import pickle
import socket
import sys
import time
from typing import Any

COL = ["Schell", "Herz", "Eichel", "Laub"]
COL_TELL = [f"[{COL.index(col)}] {col}" for col in COL]
NUM = ["VII", "VIII", "IX", "X", "Unter", "Ober", "König", "Sau"]
FULL_NUM = ["VI", "VII", "VIII", "IX", "X", "Unter", "Ober", "König", "Sau"]
NUM_TELL = [f"[{FULL_NUM.index(num)}] {num}" for num in FULL_NUM]


def send(connection: socket.socket, data: Any) -> None:
    data = pickle.dumps(data)
    connection.send(pickle.dumps(f"_{len(data)}"))
    ack = connection.recv(16)
    if pickle.loads(ack) == "yes":
        connection.send(data)


def receive(connection: socket.socket) -> Any:
    buff = connection.recv(16)
    print(buff)
    buff = pickle.loads(buff)
    if pickle.loads(buff).startswith("_"):
        connection.send(pickle.dumps("yes"))
        data = connection.recv(buff)
        return pickle.loads(data)


def convert_to_readable(card_id):
    if card_id == 32:
        return "Schell", "Weli"
    return get_card_col(card_id), get_card_num(card_id)


def get_card_col(card_id, representation: bool = True, integer: bool = False) -> str | int | tuple[str, int]:
    if card_id == 32:
        if integer and representation:
            return "Schell", 0
        elif integer:
            return 0
        else:
            return "Schell"
    if integer and representation:
        return COL[math.floor(int(card_id) / 8)], math.floor(int(card_id) / 8)
    elif integer:
        return math.floor(int(card_id) / 8)
    else:
        return COL[math.floor(int(card_id) / 8)]


def get_card_num(card_id, representation: bool = True, integer: bool = False) -> str | int | tuple[str, int]:
    if card_id == 32:
        if integer and representation:
            return "Weli", -1
        elif integer:
            return -1
        else:
            return "Weli"
    if integer and representation:
        return NUM[(int(card_id) % 8)], int(card_id) % 8
    elif integer:
        return int(card_id) % 8
    else:
        return NUM[(int(card_id) % 8)]


def display_cards(cards: list):
    cards = [convert_to_readable(card) for card in cards]
    string = ""
    for i in range(len(cards)):
        string = f"{string}[{i + 1}] {cards[i][0]} {cards[i][1]}, "
    print(string[:-2])


def starting_anim(text: str = "Starting Program", counting_char: str = ".", delay: int = 0.5, amount: int = 5):
    for _ in range(amount):
        sys.stdout.write(f"\r{text}")
        sys.stdout.flush()
        text += counting_char
        time.sleep(delay)
    sys.stdout.write("\n")
