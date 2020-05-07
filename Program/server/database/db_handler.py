
import sqlite3

from datetime import datetime

class DatabaseHandler:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)

    def login(self, un, pw):
        print('db_handler - login')
        user = self.connection.execute(
            '''
            SELECT * FROM userInfo WHERE un = (?) and pw = (?);
            ''',
            (un, pw)
        ).fetchone()

        if user is not None:
            print('User exist and password is correct')
            return True
        else:
            return False

    def logout(self):
        pass

    def insert(self, action, user):
        self.connection.execute(
            '''
            INSERT INTO userlog (username, useraction, loginTime)
                        VALUES (?, ?, ?)
            ''',
            (   user, action, datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        )
        self.connection.commit()

    def get_user_log(self, user):
        data = self.connection.execute(
            '''
            SELECT * FROM userlog WHERE username = (?)
            ''',
            (user,)
        ).fetchall()        

        return data
