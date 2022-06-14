import math
import random

from .tools import convert_to_readable


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
        """
        Create a new deck of Cards

        :param cards: The list of cards a Dek includes
        """
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
        """
        Return an amount of cards and delete them from the deck

        :param cards: The amount of cards
        :return: The selected cards
        """
        tc = self.cards[:cards]
        self.cards = self.cards[cards:]
        return tc

    @staticmethod
    def mix(cards: list[CardBase]) -> list[CardBase]:
        """
        Mix a deck of cards

        :param cards: The dek of cards to mix
        :return: The mixed dek
        """
        random.shuffle(cards)
        return cards

    @classmethod
    def get_mixed_dek(cls):
        """
        Returns mixed Card Dek

        :return: CardDek object with mixed cards
        """
        return cls(cards=cls.mix([CardBase(i) for i in range(33)]))


class GameDek:
    def __init__(self, card_dek: CardDek, players: list):
        """
        Create A dek of cards including the dek of every player and the other cards of the dek

        :param card_dek: The Dek of cards not belonging to anyone
        :param players: A list of Players
        """
        self.players: list = players
        self.card_dek: CardDek = card_dek

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.players[[pl.name for pl in self.players].index(item)]

    def __repr__(self):
        return f"<GameDek players={', '.join([pl.name for pl in self.players])}, card_dek={len(self.card_dek)}>"

    def start_round(self):
        pass

    @staticmethod
    def deal(dek: CardDek, players: list, cards: int = 5) -> list | None:
        """
        Deal an amount of cards to several Players

        :param dek: The Dek of cards
        :param players:
        :param cards:
        :return:
        """
        for pl in players:
            pl.dek = [CardBase(i) for i in dek.deal_top_card(cards)]
        return players

    @classmethod
    def create_dek(cls, players: list):
        """
        Create a Game Dek with the names of the Players
        The Dek includes 5 Cards for every Player and a mixed dek

        :param players: The names of the Player
        :return: A New Game Dek
        """
        if len(players) != 4:
            return None
        dek = CardDek.get_mixed_dek()

        return cls(
            card_dek=dek,
            players=cls.deal(dek, players=players)
        )
