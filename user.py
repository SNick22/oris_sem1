from flask_login import UserMixin
from DataBase import Database

db = Database()


class User(UserMixin):
    def __init__(self, login):
        self.login = login
        self.id = db.get_data(f"select user_pk from users where login = '{self.login}'")[0][0]

    def is_admin(self):
        return db.get_data(f"select is_admin from users where user_pk = {self.id}")[0][0]