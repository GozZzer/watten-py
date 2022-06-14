from getpass import getpass
from watten import Player, GameDek

if __name__ == '__main__':
    """match str(input("Register [R] or Login [L]:\n")).upper():
        case "R":
            email = input("Email: ")
            user = input("Username: ")
            password = getpass()
            pl = Player.register(email, user, password)
        case "L":
            user = input("Username: ")
            password = getpass()
            pl = Player.login(user, password)
        case _:
            print("Okay then you can't Play Watten Here!")
            exit()
    match str(input("Do you want to play? Y/N")).upper():
        case "Y":
            game = GameDek.create_dek([pl.name, Player("AI1"), Player("AI2"), Player("AI3")])"""
    game = GameDek.create_dek([Player("Daniel"), Player.ai(), Player.ai(), Player.ai()])

    print(game)


