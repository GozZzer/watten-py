import math

from watten.objects import CardBase


def convert_to_readable(card_id: int | CardBase):
    if isinstance(card_id, CardBase):
        card_id = card_id.card_id
    if card_id == 32:
        return "Schell", "Weli"

    col = ["Schell", "Herz", "Eichel", "Laub"]
    num = ["VII", "VIII", "IX", "X", "Unter", "Ober", "König", "Sau"]
    return col[math.floor(card_id/8)], num[(card_id % 8)]
