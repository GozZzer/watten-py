import math
import random

from watten.tools import convert_to_readable


class CardBase:
    def __init__(self, card_id: int):
        """
        The Base Class of a Card to represent a Playing-Card

        :param card_id: The id of the card
        """
        self.card_id: int = card_id

    def __int__(self):
        # Returns the id of the given card
        return int(self.card_id)

    def __repr__(self):
        # Returns the representation of the given card
        color, name = convert_to_readable(int(self))
        return f"<CardBase color={color}, name={name}>"

    def __eq__(self, other):
        # Checks if a card has the same color as another one
        if isinstance(other, CardBase):
            if math.floor(int(self) / 8) == math.floor(int(other) / 8):
                return True
            else:
                return False
        elif isinstance(other, int):
            if math.floor(self.card_id / 8) == math.floor(other / 8):
                return True
            else:
                return False
        else:
            raise NotImplementedError

    def __gt__(self, other):
        if isinstance(other, CardBase):
            if other == self:
                if (int(self) % 8) > (int(other) % 8):
                    return True
                else:
                    return False
            return False
        else:
            raise NotImplementedError

    def __lt__(self, other):
        if isinstance(other, CardBase):
            if other == self:
                if (int(self) % 8) < (int(other) % 8):
                    return True
                else:
                    return False
            return False
        else:
            raise NotImplementedError


class CardDek:
    def __init__(self, cards: list[CardBase]):
        self.cards: list = cards

    def __repr__(self):
        return f"<CardDek cards=len({len(self.cards)})>"

    def __iter__(self):
        return self.cards

    def __getitem__(self, item):
        return self.cards[item]

    def __len__(self):
        return len(self.cards)

    def deal_top_card(self, cards=1):
        tc = self.cards[:cards]
        self.cards = self.cards[cards:]
        return tc


    @staticmethod
    def mix(cards: list[CardBase]) -> list[CardBase]:
        random.shuffle(cards)
        return cards

    @classmethod
    def get_mixed_dek(cls):
        return cls(cards=cls.mix([CardBase(i) for i in range(33)]))


class PlayerDek:
    def __init__(self, name: str, cards: list[CardBase | None] = []):
        self.name: str = name
        self.cards: list[CardBase] = cards

    def __repr__(self):
        return f"<PlayerDek name={self.name} cards=({', '.join(map(str, self.cards))}), id={id(self)}>"

    def __len__(self):
        return len(self.cards)

    def __getitem__(self, item):
        return self.cards[item]

    def __lt__(self, other):
        return len(self.cards) < other

    def __gt__(self, other):
        return len(self.cards) > other

    def append(self, obj):
        self.cards.append(obj)


class GameDek:
    def __init__(self, card_dek: CardDek, players_dek: list[PlayerDek]):
        self.players_dek: list[PlayerDek] = players_dek
        self.card_dek: CardDek = card_dek

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.players_dek[[pl.name for pl in self.players_dek].index(item)]

    def __repr__(self):
        return f"<GameDek player={len(self.players)}, players_dek={self.players_dek}, card_dek={len(self.card_dek)}>"

    @staticmethod
    def deal(dek: CardDek, players: list[str], cards: int = 5) -> list[PlayerDek] | None:
        p_dek = []
        for pl in players:
            pdek = PlayerDek(pl, [CardBase(i) for i in dek.deal_top_card(5)])
            p_dek.append(pdek)
        return p_dek

    @classmethod
    def create_dek(cls, players: list[str]):
        if len(players) != 4:
            return None
        dek = CardDek.get_mixed_dek()
        return cls(
            card_dek=dek,
            players_dek=cls.deal(dek, players=players)
        )
