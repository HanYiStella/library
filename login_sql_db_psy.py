import csv
import psycopg2

from werkzeug.security import generate_password_hash, check_password_hash


conn = psycopg2.connect(database="login", user="stella", password="Janeslowly")
cur = conn.cursor()

#cur.execute("DROP TABLE loginlist")

#cur.execute('''CREATE TABLE loginlist(id SERIAL PRIMARY KEY, account TEXT, password TEXT, email TEXT, status TEXT);''')

#manager_password = generate_password_hash('manager_password')
#user_password = generate_password_hash('user_password')

#cur.execute("UPDATE loginlist SET email='kayz20176@gmail.com' WHERE email IS NULL")
cur.execute("UPDATE loginlist SET password='manager_password' WHERE id='1'")
cur.execute("UPDATE loginlist SET password='user_password' WHERE id='2'")
#cur.execute("INSERT INTO loginlist (account, password) VALUES ('manager_account', '{password}')".format(password=manager_password))
#cur.execute("INSERT INTO loginlist (account, password) VALUES ('user_account', '{password}')".format(password=user_password))

conn.commit()

cur.close()
conn.close()

