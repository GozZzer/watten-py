import random


class Game:
    def __init__(self, game_id: int, lad: bool = True):
        self.game_id: int = game_id
        self.lad: int = lad
        self.player = {}
        self.cards = []
        self.points = [0, 0]
        self.sets = [0, 0]
        self.curr_set = []

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.player[list(self)[item]]
        elif isinstance(item, str):
            return self.player[list(self)[list(self).index(item)]]

    def __bool__(self):
        return self.lad
        
    def __iter__(self):
        return iter([pl for pl in self.player])

    def get_cards(self) -> None:
        self.cards = list(range(33))
        self.mix_cards()

    def mix_cards(self) -> None:
        random.shuffle(self.cards)

    def deal_top_card(self, cards=1) -> list[int] | int:
        top_card = self.cards[:cards]
        self.cards = self.cards[cards:]
        return top_card
