import datetime
import json
import pickle
import socket
import uuid


class Client:
    def __init__(self, user_id: uuid.UUID, username: str, email: str):
        self.user_id: uuid.UUID = user_id
        self.username = username
        self.email = email

    def __str__(self):
        return f"<Client {self.username}>"

    @classmethod
    def get_user(cls, username: str, password: str):
        dta = None
        with open("user_data.json", "r") as f:
            data = json.load(f)
            user_id = [user_id for user_id in data if data[user_id]["username"] == username]
            if user_id is None:
                return "Invalid Username"
            dta = data[user_id[0]]
        if dta["password"] == password:
            return cls(
                user_id[0],
                dta["username"],
                dta["email"]
            )
        else:
            return "Invalid Password"

    @classmethod
    def get_user_by_node(cls, node):
        with open("user_data.json", "r") as f:
            data = json.load(f)
            try:
                user_lst = [uuid.UUID(uid) for uid in data if uuid.UUID(uid).fields[5] == node]
                times = [datetime.datetime.fromtimestamp((u.time - 0x01b21dd213814000) * 100 / 1e9) for u in user_lst]
                try:
                    user = user_lst[times.index(max(times))]
                except ValueError:
                    return None

                return cls(
                    user,
                    data[str(user)]["username"],
                    data[str(user)]["password"]
                )
            except IndexError:
                return None

    @classmethod
    def new_user(cls, username: str, email: str, password: str):
        new_user_id = None
        with open("user_data.json", "r") as f:
            data = json.load(f)
            try:
                _ = [user_id for user_id in data if data[user_id]["username"] == username][0]
                return f"{username} is already used"
            except IndexError:
                pass
            while new_user_id in data or new_user_id is None:
                new_user_id = uuid.uuid1()
        with open("user_data.json", "w") as f:
            data[str(new_user_id)] = {"username": username, "email": email, "password": password}
            json.dump(data, f, indent=4)
        return cls(
            new_user_id,
            username,
            email
        )


class Task:
    def __init__(self, priority: int = 1, task_type: str = "GET_DATA", connection: socket.socket = None, **kwargs):
        self.connection = connection
        self.priority = priority
        self.task_type = task_type
        self.data = kwargs

    def set_connection(self, conn):
        self.connection = conn

    def do_task(self):
        if self.task_type == "LOGIN":
            user = Client.get_user(self.data["username"], self.data["password"])
            self.connection.send(pickle.dumps(user))
        elif self.task_type == "REGISTER":
            user = Client.new_user(self.data["username"], self.data["email"], self.data["password"])
            self.connection.send(pickle.dumps(user))
