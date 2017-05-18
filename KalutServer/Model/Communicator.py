import mysql.connector as sql
from hashlib import sha256
import json
from KalutServer.Exceptions import *
import re

class Communicator(object):
    def __init__(self):
        self.connect_to_db()

    # BASIC MYSQL COMMANDS
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
    def commit(self):
        self.conn.commit()
    def logout(self):
        self.conn.cmd_quit()
    # GET/SET KALUTS
    def get_user_kaluts(self, username, password):
        if self.auth_user(username, password)['Auth']:
            uids = self.execute('SELECT my_quizes FROM kalut.users WHERE username="{0}";'.format(username))
            uids = json.loads(uids[0][0])['uids']
            retdata = dict()
            for uid in uids:
                retdata[uid]=self.get_quiz_info(uid)
            return retdata
        else:
            raise InvalidCredentials
    def get_user_fav_kaluts(self, username, password):
        if self.auth_user(username, password)['Auth']:
            uids = self.execute('SELECT fav_quizes FROM kalut.users WHERE username="{0}";'.format(username))
            uids = json.loads(uids[0][0])['uids']
            retdata = dict()
            for uid in uids:
                retdata[uid]=self.get_quiz_info(uid)
            return retdata
        else:
            raise InvalidCredentials
    def get_quiz_info(self, uid):
        query = 'SELECT description FROM kalut.quizes WHERE uid={0};'.format(uid)
        data = self.execute(query)
        if data and data[0] and data[0][0]:
            return data[0][0]
        else:
            return None
    def get_all_quizes_info(self):
        query = 'SELECT uid, description FROM kalut.quizes;'
        res = self.execute(query)
        ret = dict()
        for i in res:
            ret[i[0]]=i[1]
        return ret
    def get_quiz_data(self, uid):
        query = 'SELECT quiz FROM kalut.quizes WHERE uid={0};'.format(uid)
        return self.execute(query)[0][0]
    def add_kalut(self, username, password, description, quiz_data):
        if self.auth_user(username, password)['Auth']:
            # add the quiz to the database
            query = '''
            INSERT INTO kalut.quizes (quiz, description) VALUES
            ("{0}", "{1}");
            '''.format(re.sub(r'([\"])',    r'\\\1', quiz_data), re.sub(r'([\"])',    r'\\\1', description))
            self.execute(query)
            # get the uid of the quiz
            query = 'SELECT last_insert_id();'
            uid = self.execute(query)[0][0]
            # get the my_quizes of the user
            query = 'SELECT my_quizes FROM kalut.users WHERE username="{0}";'.format(username)
            raw_my_quizes = self.execute(query)[0][0]
            # add the uid to the list of uids
            my_quizes = json.loads(raw_my_quizes)
            my_quizes['uids'].append(uid)
            raw_my_quizes = json.dumps(my_quizes)
            # add escape chars
            raw_my_quizes = re.sub(r'([\"])',    r'\\\1', raw_my_quizes)
            # update the database
            query = '''
            UPDATE kalut.users SET
                my_quizes="{0}"
                WHERE username="{1}";
            '''.format(raw_my_quizes, username)
            self.execute(query)
            self.commit()
            return None
        else:
            raise InvalidCredentials
    # USER MANAGER
    def auth_user(self, username, password):
        res = self.execute('SELECT password FROM kalut.users WHERE username="{0}";'.format(username))
        # hasher = sha256()
        # hasher.update(password)
        # return hasher.digest() == res[0][0].encode('ascii')
        if res and res[0] and res[00]:
            return {'Auth' : str(password == res[0][0])}
        else:
            return {'Auth': 'False'}
    def register_user(self, username, password):
        pass
    