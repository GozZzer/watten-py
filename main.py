import pickle
import socket
import time
import uuid
from typing import Any

#import kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.input.providers.mouse import MouseMotionEvent
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, Clock
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen

from objects import Client, Task
from tools import check_password, check_username, check_login, check_register

Window.size = (1000, 700)
Window.minimum_width, Window.minimum_height = (900, 600)


class MainScreen(Screen):
    field = ObjectProperty()
    play_button = ObjectProperty()
    self_field = ObjectProperty()
    self_cards = ObjectProperty()
    started: bool = False
    clicked_card: ObjectProperty | None = None

    def update_field(self):
        if self.started is True:
            self.play_button.disabled = True
            self.play_button.opacity = 0
        else:
            self.play_button.disabled = False
            self.play_button.opacity = .5
            self.self_cards.clear_widgets()

    def get_card(self, instance, motion: MouseMotionEvent, *args):
        wid = [instance.pos[0], instance.pos[0] + instance.size[0]]
        high = [instance.pos[1], instance.pos[1] + instance.size[1]]
        if wid[0] < motion.pos[0] < wid[1] and high[0] < motion.pos[1] < high[1]:
            print(instance)
            self.clicked_card = instance

    def draw_cards(self):
        for i in range(5):
            card = Label(text=f"Card{i}", outline_color=(1, 1, 1, 1))
            with card.canvas:
                Color(1., 1., 0)
                Rectangle(size=card.size, pos=card.pos)
            card.bind(on_touch_down=self.get_card)
            self.self_cards.add_widget(card)

    def start_game(self):
        self.started = True
        self.update_field()
        self.draw_cards()


class ProfileScreen(Screen):
    account_name = ObjectProperty()

    def enter(self):
        app = App.get_running_app()
        if app.user is None:
            self.manager.current = "plogin"
        else:
            self.account_name.text = f"Account: {app.user.username}"

    def logout(self):
        app = App.get_running_app()
        app.user.username = None
        self.account_name.text = "None"
        self.manager.current = "plogin"
        self.manager.transition.direction = "left"

    pass


class ProfileLoginScreen(Screen):
    pass


class SettingsScreen(Screen):
    pass


class LoginScreen(Screen):
    username = ObjectProperty()
    password = ObjectProperty()

    def login(self):
        self.username.read_only = True
        self.password.read_only = True

        username = self.username.text
        password = self.password.text
        self.password.text = ""
        # Check if the text input has been inserted
        missing = ""
        if username == "":
            missing += "Username"
        if password == "":
            if missing == "":
                missing += "Password"
            else:
                missing += "/Password"
        if missing:
            missing_popup = Popup(title="Missing Input", content=Label(text=f"{missing} is missing"),
                                  size_hint=(None, None), size=(dp(400), dp(400)))
            missing_popup.open()
            return

        # Check if the text input is valid
        text = ""
        c_username = check_username(username)
        if c_username is not True:
            text += "Usernames with " + c_username
        c_password = check_password(password)
        if c_password is not True:
            if text == "":
                text += "Passwords with " + c_password
            else:
                text += "\nPasswords with " + c_password
        if text:
            invalid_popup = Popup(title="Invalid Input", content=Label(text=text + "\nare not valid"),
                                  size_hint=(None, None), size=(dp(400), dp(400)))
            invalid_popup.open()
            return

        app: WattenApp = App.get_running_app()
        app.send(Task(task_type="LOGIN", username=username, password=password, priority=50))

        user = app.recv()
        if user is None:
            login_popup = Popup(title="Invalid Login-data", content=Label(text="Your Login-data is invalid, make sure you entered the correct data."
                                                                               "\nOr you are not registered yet."),
                                size_hint=(None, None), size=(dp(400), dp(400)))
            login_popup.open()
            return
        app.user = user
        valid_popup = Popup(title="Login Successful", content=Label(text=f"You are now logged in as {username}"),
                            size_hint=(None, None), size=(dp(400), dp(400)))
        valid_popup.open()

        self.manager.current = "main"
        self.manager.transition.direction = "left"


class RegisterScreen(Screen):
    username = ObjectProperty()
    email = ObjectProperty()
    password = ObjectProperty()
    c_password = ObjectProperty()

    def register(self):
        app: WattenApp = App.get_running_app()
        app.send(Task(task_type="REGISTER", priority=50, username=self.username.text, email=self.email.text, password=self.password.text))
        c_register: Client | str = app.recv()
        if not isinstance(c_register, Client):
            username_popup = Popup(title="Invalid Input", content=Label(text=c_register),
                                   size_hint=(None, None), size=(dp(400), dp(400)))
            username_popup.open()
            return
        app.user = c_register
        registered_popup = Popup(title="Successfully Registered", content=Label(text="You have been registered"),
                                 size_hint=(None, None), size=(dp(400), dp(400)))
        registered_popup.open()
        self.manager.current = "login"
        self.manager.transition.direction = "right"


class WattenApp(App):
    def __init__(self, **kwargs):
        self.conn = None
        self.user = None
        super().__init__(**kwargs)

    def setup_connection(self, host: str = "localhost", port: int = 5643):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print((host, port))
        try:
            sock.connect((host, port))
            self.conn = sock
        except ConnectionRefusedError:
            print(f"Connection refused to {host}:{port}")
            exit()

    def recv_user(self):
        dta = self.recv()
        if dta == "NODE":
            node = uuid.getnode()
            self.send(pickle.dumps(node))
            user = self.recv()
            self.user = user

    def send(self, data: Any):
        dta = pickle.dumps(data)
        length = dta.__sizeof__()
        try:
            self.conn.sendall(pickle.dumps(length))
            ack = self.conn.recv(32)
            if pickle.loads(ack) == "ACK":
                self.conn.sendall(dta)
            else:
                raise Exception(f"Couldnt send data ({data})")
        except ConnectionResetError:
            print("The Server Stopped Working")
            exit()

    def recv(self):
        data = self.conn.recv(1024)
        length = pickle.loads(data)
        self.conn.sendall(pickle.dumps("ACK"))
        try:
            return pickle.loads(self.conn.recv(length))
        except ConnectionResetError:
            print("The Server Stopped Working")
            exit()

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(ProfileLoginScreen(name="plogin"))
        sm.add_widget(RegisterScreen(name="register"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(ProfileScreen(name="profile"))
        self.load_kv("watten.kv")
        return sm

    def run(self):
        Clock.schedule_once(self.setup_connection, -1)
        Clock.schedule_once(self.recv_user, -1)
        super().run()


if __name__ == '__main__':
    WattenApp().run()
