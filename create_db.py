import sqlite3

conn = sqlite3.connect('test.db')

conn.execute('''CREATE TABLE userlog
         (id INTEGER PRIMARY KEY AUTOINCREMENT,
         userInfo       TEXT    NOT NULL,
         loginTime      TEXT     NOT NULL);''')

conn.execute('''CREATE TABLE userInfo
                (userid INTEGER PRIMARY KEY AUTOINCREMENT,
                un TEXT NOT NULL,
                pw TEXT NOT NULL);''')

conn.close()
