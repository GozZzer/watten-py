from random import randint

class PlayerBase:
    __slots__ = ["display_name"]
    def __init__(self, display_name: str):
        self.display_name = display_name

class OfflinePlayer(PlayerBase):
    __slots__ = PlayerBase.__slots__ + ["player_dek"]
    def __init__(self, player_dek: list = None, **kwargs):
        self.player_dek = player_dek
        super().__init__(**kwargs)

class AIPlayer(OfflinePlayer):
    __slots__ = OfflinePlayer.__slots__ + ["ai_name", "ai"]
    def __init__(self, ai: bool = True, **kwargs):
        self.ai_name = f"AI_{randint(1000, 9999)}"
        self.ai = ai
        super().__init__(**kwargs)

class OnlinePlayer(OfflinePlayer):
    __slots__ = OfflinePlayer.__slots__ + ["player_id", "game_id", "searching", "playing"]
    def __init__(self, player_id: str, game_id: str = None, **kwargs):
        self.player_id = player_id
        self.game_id = game_id
        self.searching = False
        self.playing = False
        super().__init__(**kwargs)

    @classmethod
    def login(cls, username: str, password: str):
        return cls(
            name=username,

        )

    @classmethod
    def register(cls, username: str, password: str, email: str):
        return cls(
            name=username
        )

class Player:
    __slots__ = ["name", "player_id", "player_dek", "game_id", "searching", "playing", "ai"]
    def __init__(self, name: str = None, player_id: str = None, player_dek: list = None, game_id: str = None, ai: bool = False):
        self.name = name
        self.player_id = player_id
        self.player_dek = player_dek
        self.game_id = game_id
        self.searching = False
        self.playing: bool = False
        self.ai: bool = ai

    def __repr__(self):
        return f"<Player name={self.name}, id={self.player_id}, dek={self.player_dek}, game={self.game_id}, playing={self.playing}>"

    def find_game(self):
        pass






    @classmethod
    def ai(cls):
        return cls(
            name=f"AI_{randint(1000, 9999)}",
            ai=True
        )


class Game:
    def __init__(self, players: list[Player], game_id: str):
        self.players = players
        self.game_id = game_id


    @classmethod
    def start(cls, players: list[Player]):

