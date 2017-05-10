import mysql.connector as sql
from hashlib import sha256
import json
from KalutServer.Exceptions import *

class Communicator(object):
    def __init__(self):
        self.connect_to_db()

    def connect_to_db(self):
        self.conn = sql.connect(
            user='kalut',
            password=file('C:\\keys\\pwd.txt', 'r').readline(),
            host='kalut.ml',
            database='kalut'
        )
        self.cur = self.conn.cursor()

    def execute(self, cmd):
        if not self.conn.is_connected():
            self.connect_to_db()
        self.cur.execute(cmd)
        try:
            return self.cur.fetchall()
        except:
            return None

    def get_user_kaluts(self, username, password):
        if self.auth_user(username, password):
            res = self.execute('SELECT my_quizes FROM kalut.users WHERE username="{0}";'.format(username))
            res = json.loads(res[0][0])
            return res['uids']
        else:
            raise InvalidCredentials
    def get_user_fav_kaluts(self, username, password):
        if self.auth_user(username, password):
            res = self.execute('SELECT fav_quizes FROM kalut.users WHERE username="{0}";'.format(username))
            res = json.loads(res[0][0])
            return res['uids']
        else:
            raise InvalidCredentials
    def auth_user(self, username, password):
        res = self.execute('SELECT password FROM kalut.users WHERE username="{0}";'.format(username))
        # hasher = sha256()
        # hasher.update(password)
        # return hasher.digest() == res[0][0].encode('ascii')
        return password == res[0][0]