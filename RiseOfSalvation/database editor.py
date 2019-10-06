import sqlite3
import os
os.chdir("C:/Users/TYLER/OneDrive/Documents/python_things/real_coursework")
conn = sqlite3.connect('game.db')
cur = conn.cursor()
"""
drop_table = "DROP TABLE login"

cur.execute(drop_table)
"""

#this deleted the old table

"""

conn.execute('''CREATE TABLE accounts
         (username CHAR(30) PRIMARY KEY     NOT NULL,
         password           CHAR(30)    NOT NULL);''')

"""

#created the new table


#cur.execute("PRAGMA foreign_keys = ON")
#cur.execute("""
#    CREATE TABLE records(
#        level INTEGER NOT NULL PRIMARY KEY,
#        time REAL NOT NULL,
#        username CHAR(30) NOT NULL,
#        FOREIGN KEY(username) REFERENCES accounts(username)
#    )
#""")


#this created the records table

conn.execute("INSERT INTO accounts (username,password) \
      VALUES ('hello','hello')");

conn.commit()

#inserted an account into the table

"""
conn.execute("INSERT INTO records (level,time,username) \
      VALUES ('1','23,83','hi')");

conn.commit()
"""
#used to insert records
"""
conn.execute("DELETE FROM records WHERE level=?", ('1'))
conn.commit()
"""
#used to remove rows from the records table
"""
conn.execute("INSERT INTO records (level,time,username) \
      VALUES ('1','23.85','hi')");

conn.commit()
"""
#added a record into the records table
conn.close()










