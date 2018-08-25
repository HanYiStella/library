import csv
import psycopg2


conn = psycopg2.connect(database="history", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
cur = conn.cursor()

cur.execute("DROP TABLE history")

cur.execute('''CREATE TABLE history(id SERIAL PRIMARY KEY,borrow_time TEXT,book_id TEXT,book_name TEXT,if_borrow TEXT,people_id TEXT,people_status TEXT,people_class TEXT,people_number TEXT,people_name TEXT);''')


conn.commit()

cur.close()
conn.close()

conn = psycopg2.connect(database="history", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
cur = conn.cursor()
with cur:
	cur.execute("SELECT * FROM history;")
	b = cur.fetchall()
	print(b)

cur.close()
conn.close()

