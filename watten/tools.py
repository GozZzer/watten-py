import math


def convert_to_readable(card_id: int):
    """
    The card is represented by an id.
    This function converts the id to a readable representation

    :param card_id: The ID of the card
    :return: The color and the name of the card
    """
    if card_id == 32:
        return "Schell", "Weli"

    col = ["Schell", "Herz", "Eichel", "Laub"]
    num = ["VII", "VIII", "IX", "X", "Unter", "Ober", "König", "Sau"]
    return col[math.floor(card_id/8)], num[(card_id % 8)]
