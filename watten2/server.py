import multiprocessing
import pickle
import socket
import threading
import time
from typing import Any

from watten2.games import Game

from watten2.tools import send, receive, NUM_TELL, COL_TELL, get_card_col, get_card_num, convert_to_readable, FULL_NUM, COL



class Server:
    def __init__(self, thread_process: bool = True):
        self.thread_process: bool = thread_process
        self.sock: socket.socket | None = None
        self.games: list[Game] | None = []
        self.game_thr_proc: list[threading.Thread | multiprocessing.Process] | None = []

    def start_server(self, host: str = "localhost", port: int = 5643, listen: int = 16):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(listen)
        self.wait_for_gamestart()

    def wait_for_gamestart(self, amount: int = 4):
        game = Game(len(self.games))
        print(f"[Game #{game.game_id}] Waiting for players to join a game...")
        for i in range(amount):
            conn, addr = self.sock.accept()
            address = f"{addr[0]}-0"
            while address in game.player:
                address = f"{address[:-1]}{str(int(address[-1]) + 1)}"
            game.player[address] = {}
            game.player[address]["name"] = None
            game.player[address]["conn"] = conn
            game.player[address]["dek"] = []
            while game.player[address]["name"] is None:
                self.send_to_connection(conn, "Please insert a name:", "INPUT")
                name = self.receive_from_connection(conn)
                game.player[address]["name"] = name
            print(f"[Game #{game.game_id}] {game.player[address]['name']} joined. ({address}) (Status: {i+1}/{amount})")
            if amount - (i + 1) != 0:
                self.send_to_connection(conn, f"You have to wait for {amount-(i+1)} more players")
            for pl in list(game.player.keys())[:-1]:
                if amount - (i + 1) != 0:
                    self.send_to_connection(game.player[pl]["conn"], f"{amount-(i+1)} more players")
        if self.thread_process:
            game_thread = threading.Thread(target=self.start_game, args=(game,))
            game_thread.start()
            self.game_thr_proc.append(game_thread)
        else:
            game_process = multiprocessing.Process(target=self.start_game, args=(game,))
            game_process.start()
            self.game_thr_proc.append(game_process)
        self.games.append(game)
        self.wait_for_gamestart()

    def start_game(self, game: Game):
        print(f"[Game #{game.game_id}] Started")
        self.send_to_game(game, "Game starts...")
        cur = 0
        playing = True
        while playing:
            playing_game = [game[(cur + i) % 4] for i in range(1, 5)]
            game.get_cards()
            for player in playing_game:
                player["dek"] = game.deal_top_card(5)
            self.send_to_game(game, "%p shuffled, and everyone got 5 Cards", defined_player=playing_game[3]["name"])
            for player in playing_game:
                self.send_to_connection(player["conn"], "These are your cards", "PICKLE", pickle.dumps(player["dek"]))

            if not game:
                self.send_to_game(game, f"%p is choosing a number", defined_player=playing_game[0]["name"])
                repr_num = None
                int_num = None
                while repr_num is None:
                    self.send_to_connection(playing_game[0]["conn"], "What number you want to set?", ", ".join(NUM_TELL), "INPUT")
                    try:
                        num = int(self.receive_from_connection(playing_game[0]["conn"]))
                        num -= 1
                        if not (-1 <= num <= len(NUM_TELL)-2):
                            num = None
                        else:
                            int_num = num
                            repr_num = NUM_TELL[num]
                    except TypeError:
                        self.send_to_connection(playing_game[0]["conn"], "Invalid Input")
                        num = None
                self.send_to_game(game, f"%p set {repr_num} as a number", defined_player=playing_game[0]['name'])

                self.send_to_game(game, f"%p is choosing a color", defined_player=playing_game[3]["name"])
                repr_col = None
                int_col = None
                while repr_col is None:
                    self.send_to_connection(playing_game[3]["conn"], "What color you want to set?", ", ".join(COL_TELL), "INPUT")
                    try:
                        col = int(self.receive_from_connection(playing_game[3]["conn"]))
                        if not (0 <= col <= len(COL_TELL)-1):
                            repr_col = None
                        else:
                            int_col = col
                            repr_col = COL_TELL[col]
                    except TypeError:
                        self.send_to_connection(playing_game[3]["conn"], "Invalid Input")
                        col = None

                self.send_to_game(game, f"%p set {repr_col[4:]} as a color", defined_player=playing_game[3]['name'])
                self.send_to_game(game, f"{repr_col[4:]} {repr_num[4:]} is the best card")
            else:
                repr_col, int_col = get_card_col(playing_game[-1]["dek"][0], True, True)
                repr_num, int_num = get_card_num(playing_game[0]["dek"][0], True, True)

                self.send_to_connection(playing_game[0]["conn"], f"{repr_col} {repr_num} is the best card")
                self.send_to_connection(playing_game[-1]["conn"], f"{repr_col} {repr_num} is the best card")

            game_winner = -1
            while game_winner == -1:
                set_winner = -1
                for i in range(5):
                    game.curr_set = []
                    for player in playing_game:
                        self.send_to_connection(player["conn"], "These are your cards", "PICKLE", pickle.dumps(player["dek"]))
                        self.send_to_connection(player["conn"], f"What card do you want to play? [1 - {len(player['dek'])}]", "INPUT")
                        card = int(self.receive_from_connection(player["conn"])) - 1

                        game.curr_set.append(player["dek"][card])
                        player["dek"].pop(card)
                        self.send_to_game(game, "Current Set:", "PICKLE", pickle.dumps(game.curr_set))
                    set_winner = self.check_set_winner(game.curr_set, int_col, int_num)
                    playing_game = playing_game[set_winner:] + playing_game[:set_winner]
                    game.points[set_winner % 2] += 1
                    if any(game.points) == 3:
                        game.sets[game.points.index(3)] += 1
                        break
                self.send_to_game(game, f"Team {set_winner % 2} Won The set and got a gamepoint")
                if any(game.sets) == 11:
                    game_winner = set_winner % 2
                    break
            self.send_to_game(game, f"Team {game_winner % 2} Won the whole set with {' - '.join(game.sets)}")

            cur += 1
            cur = cur % 4
            playing = False
            time.sleep(1)

        self.send_to_game(game, "CLOSE")

    @staticmethod
    def check_set_winner(set_dek: list[int], high_col: int, high_num: int) -> int:
        winner_index = 0
        round_col = get_card_col(set_dek[0], False, True)
        # print(f"Highest Card: {COL[high_col]} {FULL_NUM[high_num+1]}")
        for card in set_dek:
            # print("Winner:", winner_index)
            card_num = get_card_num(card, False, True)
            card_col = get_card_col(card, False, True)
            # print(f"Player Card: {COL[card_col]} {FULL_NUM[card_num+1]}")
            if card_num == high_num and card_col == high_col:
                # Rechter hat gewonnen
                return set_dek.index(card)
            elif card_num == high_num:
                # Linker wurde gespilt
                if get_card_num(set_dek[winner_index], False, True) != high_num:
                    # Kein Linker zuvor
                    winner_index = set_dek.index(card)
            elif card_col == high_col:
                # Trumpf wurde gespielt
                if get_card_col(set_dek[winner_index]) != high_col:
                    # 1. Trumpf
                    winner_index = set_dek.index(card)
                else:
                    if get_card_num(set_dek[winner_index]) < card_num:
                        # Höherer Trumpf
                        winner_index = set_dek.index(card)
            else:
                if get_card_col(set_dek[winner_index]) != high_col and get_card_num(set_dek[winner_index], False, True) != high_num:
                    # Zuvor kein Trumpf oder Schlag
                    if round_col == card_col and get_card_num(set_dek[winner_index], False, True) < card_num:
                        winner_index = set_dek.index(card)

        return winner_index

    @staticmethod
    def send_to_game(game: Game, *data: list | str | bytes, defined_player: str = None):
        if isinstance(data, str):
            for name, conn, dek in [game.player[pl].values() for pl in game.player]:
                if defined_player:
                    if name == defined_player:
                        if "is" in data:
                            send(conn, data.replace("%p", "You").replace("is", "are"))
                        else:
                            send(conn, data.replace("%p", "You"))
                    else:
                        send(conn, data.replace("%p", defined_player))
                else:
                    send(conn, data)
        elif isinstance(data, tuple):
            for dat in data:
                for name, conn, dek in [game.player[pl].values() for pl in game.player]:
                    if defined_player:
                        if name == defined_player:
                            if "is" in dat:
                                send(conn, dat.replace("%p", "You").replace("is", "are"))
                            else:
                                send(conn, dat.replace("%p", "You"))
                        else:
                            send(conn, dat.replace("%p", defined_player))
                    else:
                        send(conn, dat)

    @staticmethod
    def receive_from_connection(conn: socket.socket, pickl: bool = False):
        return receive(conn, pickl)

    @staticmethod
    def send_to_connection(conn: socket.socket, *data: tuple[Any] | str | bytes):
        if isinstance(data, tuple):
            for dat in data:
                send(conn, dat)
        else:
            send(conn, data)

    def run(self, *args, **kwargs):
        self.start_server(*args, **kwargs)

