import sqlite3

conn = sqlite3.connect('server_db.db')

conn.execute('''CREATE TABLE userlog
         (id INTEGER PRIMARY KEY AUTOINCREMENT,
         username      TEXT    NOT NULL,
         useraction     TEXT    NOT NULL,
         loginTime      TEXT     NOT NULL);''')

conn.execute('''CREATE TABLE userInfo
                (userid INTEGER PRIMARY KEY AUTOINCREMENT,
                un TEXT NOT NULL,
                pw TEXT NOT NULL,
                logged_in BOOLEAN NOT NULL);''')

conn.close()
