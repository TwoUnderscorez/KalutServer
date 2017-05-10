import mysql.connector as sql
class Communicator(object):
    def __init__():
        self.connect_to_db()
        
    def connect_to_db(self):
        self.conn = sql.connect(
            user='kalut',
            password='!',
            host='kalut.ml',
            database='kalut'
        )
        self.cur = conn.cursor()