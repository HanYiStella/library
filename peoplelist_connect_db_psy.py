import csv
import psycopg2


with open('peoplelist_include_class.csv', newline='',encoding = 'utf8') as f:
	#csv_reader = csv.DictReader(f)
	csv_reader = csv.reader(f)
	peo_id = []
	peo_class = []
	peo_sta = []
	peo_num = []
	peo_name = []
	for row in csv_reader:
		peo_id.append(row[0])
		peo_class.append(row[1])
		peo_sta.append(row[2])
		peo_num.append(row[3])
		peo_name.append(row[4])


conn = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
cur = conn.cursor()

cur.execute("DROP TABLE peoplelist")

cur.execute('''CREATE TABLE peoplelist(
	id SERIAL PRIMARY KEY,
	people_id TEXT,
    people_status TEXT,
    people_class TEXT,
    people_number TEXT,
    people_name TEXT);''')

for i in range(0,len(peo_id)):
	peo_id_i = peo_id[i]
	peo_class_i = peo_class[i]
	peo_sta_i = peo_sta[i]
	peo_num_i = peo_num[i]
	peo_name_i = peo_name[i]
	#print(type(book_id_i))
	#print(book_id_i)

	cur.execute("INSERT INTO  peoplelist (people_id, people_class, people_status, people_number, people_name) VALUES ('{peoid}', '{peoclass}', '{peosta}', '{peonum}', '{peoname}')".format(peoid=peo_id_i,peoclass=peo_class_i,peosta=peo_sta_i,peonum=peo_num_i,peoname=peo_name_i, ))

#cur.execute("INSERT INTO booklist (book_id, book_name) VALUES (%s, %s)",(100,'test1'))
	#cur.execute(my_insert)
	conn.commit()
cur.close()
conn.close()

conn = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
cur = conn.cursor()
with cur:
	cur.execute("SELECT * FROM peoplelist;")
	b = cur.fetchall()
	print(b)

cur.close()
conn.close()

