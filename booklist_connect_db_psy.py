import csv
import psycopg2


with open('booklist.csv', newline='',encoding = 'utf8') as f:
	#csv_reader = csv.DictReader(f)
	csv_reader = csv.reader(f)
	book_id = []
	book_name = []
	for row in csv_reader:
		book_id.append(row[0])
		book_name.append(row[1])

conn = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
cur = conn.cursor()

cur.execute("DROP TABLE booklist")

cur.execute('''CREATE TABLE booklist(id SERIAL PRIMARY KEY,book_id TEXT,book_name TEXT,if_borrow TEXT,people_id TEXT,borrow_status TEXT,borrow_class TEXT,people_number TEXT,people_name TEXT,borrow_time TEXT);''')

for i in range(0,len(book_id)):
	book_id_i = book_id[i]
	book_name_i = book_name[i]
	cur.execute("INSERT INTO  booklist (book_id, book_name) VALUES ('{bookid}', '{bookname}')".format(bookid=book_id_i,bookname=book_name_i, ))
	conn.commit()

cur.execute("UPDATE booklist SET if_borrow='未借出' WHERE if_borrow IS NULL")
conn.commit()

cur.close()
conn.close()

conn = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
cur = conn.cursor()
with cur:
	cur.execute("SELECT * FROM booklist;")
	b = cur.fetchall()
	print(b)

cur.close()
conn.close()

