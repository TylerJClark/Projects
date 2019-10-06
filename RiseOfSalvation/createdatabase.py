import sqlite3
conn = sqlite3.connect('game.db')
print("Opened database successfully")

"""
conn.execute('''CREATE TABLE login
         (username CHAR(30) PRIMARY KEY     NOT NULL,
         password           CHAR(30)    NOT NULL);''')
"""


#print("Table created successfully")
conn.execute("INSERT INTO login (username,password) \
      VALUES ('hi','hi')");

cursor = conn.execute("SELECT username,password from login")
for row in cursor:
    print("Username",row[0],"Password",row[1])

conn.commit()
conn.close()
