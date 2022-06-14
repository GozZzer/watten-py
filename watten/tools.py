import math
import bcrypt


def convert_to_readable(card_id):
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
    return col[math.floor(int(card_id)/8)], num[(int(card_id) % 8)]


def encrypt(text: str):
    return bcrypt.hashpw(text.encode("utf-8"), bcrypt.gensalt(14))


def decrypt(text: str, hsh: bytes):
    return True if bcrypt.checkpw(text.encode("utf-8"), hsh) else False
