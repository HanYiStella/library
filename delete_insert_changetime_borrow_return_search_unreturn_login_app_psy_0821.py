from flask import Flask, g
from flask import render_template, flash, redirect,session, request, url_for
from flask_wtf import FlaskForm
import csv
import psycopg2
from wtforms import StringField, SelectField, PasswordField, RadioField
from wtforms.validators import DataRequired
import time
import datetime
from flask_mail import Mail, Message
import os
import smtplib 
from werkzeug.security import generate_password_hash, check_password_hash
import copy

app = Flask(__name__)
app.config['SECRET_KEY']='my-son-slowlyslowly'

BOOK_DB_PATH = 'booklist.db'
BOOK_CSV_PATH = 'booklist.csv'
BOOK_SQL_NAME = 'booklist'

PEOPLE_DB_PATH = 'peoplelist.db'
PEOPLE_CSV_PATH = 'peoplelist_include_status.csv'
PEOPLE_SQL_NAME = 'peoplelist'

Manager_DB_PATH = 'loginlist.db'
Manager_SQL_NAME = 'login'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # 邮件服务器地址
app.config['MAIL_PORT'] = 587               # 邮件服务器端口
app.config['MAIL_USE_TLS'] = True   
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') or 'chatbot520@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD') or 'chatbot@520'

mail = Mail(app)

#---------------------------------------------------------------
#Home

@app.route('/library')
def library():
	return render_template('homebase.html')


#--------------------------------------------------------------------
#Login (Manager & User)

class LoginForm(FlaskForm):
	account = StringField('帳號',validators=[DataRequired()])
	#password = StringField('密碼',validators=[DataRequired()])
	password = PasswordField('密碼',validators=[DataRequired()])


@app.route('/login', methods = ['GET', 'POST'])
def login():
	form = LoginForm()
	return render_template('login.html', form=form)

@app.route('/login/success/<account>/<password>')
def login_successed(account, password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]
	print('password:',user_account)
	print('man_pass',account)

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			return render_template('manager_home.html',account=account,password=password)

		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			return render_template('user_home.html', account=account, password=password)
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		print('3')
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)

	conn_login_db.close()

@app.route('/login/solution', methods=['POST'])
def login_solution():

	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	account_input = request.form.get('account')
	password_input = request.form.get('password')

	login_db.execute("SELECT account, password, status FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password, status FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = generate_password_hash(manager_detail[1])

	user_account = user_detail[0]
	user_password = generate_password_hash(user_detail[1])

	if (account_input==manager_account):
		print('manager')
		check_manager = check_password_hash(manager_password,password_input)
		if (check_manager==1):
			go_to_manager_home = url_for('login_successed', account=account_input, password=manager_password)
			return redirect(go_to_manager_home)

		else:
			error = "帳號或密碼輸入錯誤"
			form = LoginForm()
			return render_template('login.html',form=form, error=error)

	elif (account_input==user_account):
		print('user')
		if(check_password_hash(user_password, password_input)==1):
			go_to_user_home = url_for('login_successed', account=account_input, password=user_password)
			return redirect(go_to_user_home)

		else:
			error = "帳號或密碼輸入錯誤"
			form = LoginForm()
			return render_template('login.html',form=form, error=error)

	else:
		error = "帳號或密碼輸入錯誤"
		form = LoginForm()
		return render_template('login.html',form=form, error=error)

	conn_login_db.close()


#---------------------------------------------------------------------------------------------
#Forget password

class ForgetForm(FlaskForm):
	account = StringField('你的帳號',validators=[DataRequired()])

@app.route('/forget_password/input', methods = ['GET', 'POST'])
def forget_input():
	form = ForgetForm()
	return render_template('forget_input.html', form=form)

@app.route('/forget_password/solution', methods = ['GET', 'POST'])
def forget_solution():

	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	account_input = request.form.get('account')

	login_db.execute("SELECT email FROM loginlist WHERE account='{account}' ".format(account=account_input, ))
	select_email = login_db.fetchone()

	if (select_email==None):
		error = "帳號輸入錯誤"
		form = ForgetForm()
		return render_template('forget_input.html',form=form, error=error)

	else:
		login_db.execute("SELECT password FROM loginlist WHERE account='{account}'".format(account=account_input, ))
		select_password = login_db.fetchone()
		the_password = select_password[0]
		reset_mail = select_email[0]

		msg = Message('您的密碼', sender='chatbot520@gmail.com', recipients=[reset_mail])
		msg.html = render_template('mail_password_body.html',  password=the_password, )
		mail.send(msg)
		return render_template('send_mail_success.html',reset_mail=reset_mail, )
	conn_login_db.close()




#-------------------------------------------------------------------
#email 連結有誤，以下幾行未測試過

class ForgetResetForm(FlaskForm):
	new_password = StringField('新的密碼',validators=[DataRequired()])
	new_password_again = StringField('再輸入一次',validators=[DataRequired()])


@app.route('/froget_reset/<account>', methods = ['GET', 'POST'])
def forget_reset(account):
	form = ForgetResetForm()
	#reset_solution_url = '/forget/reset/<{account}>/solution'.format(account=account)
	return render_template('forget_reset_input.html', form=form, account=account, )


@app.route('/froget_reset/<account>/solution', methods = ['GET', 'POST'])
def forget_reset_solution(account):

	new_password = request.form.get('new_password')
	new_password_again = request.form.get('new_password_again')

	if (new_password!=new_password_again):
		error = '兩次密碼輸入不一樣'
		form = ForgetResetForm()
		return render_template('forget_reset_input.html', form=form, account=account, error=error, )

	else:
		new_password_update = generate_password_hash(new_password)

		conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
		login_db = conn_login_db.cursor()

		login_db.execute("UPDATE loginlist SET password={new_password} WHERE account={account}".format(new_password=new_password_update, account=account, ))
		login_db.commit()
		error = "更新成功！"
		form = LoginForm()
		return render_template('login.html',form=form, error=error)
	conn_login_db.close()

#email 連結有誤，以上幾行未測試過
#-----------------------------------------------------------------------------



#---------------------------------------------------------------
#Search Book

class SearchForm(FlaskForm):
	key_word = StringField('關鍵字',validators=[DataRequired()])


@app.route('/search', methods = ['GET', 'POST'])
def search():
    form = SearchForm()
    return render_template('search_input.html',title = 'Search',form=form)


@app.route('/search_solution', methods=['POST'])
def search_solution():

	conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
	book_db = conn_book_db.cursor()

	#conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
	#peo_db = conn_peo_db.cursor()

	key_word = request.form.get('key_word')

	book_db.execute("SELECT book_id, book_name, if_borrow FROM booklist WHERE book_name LIKE '%{keyword}%' OR book_id LIKE '%{key}%'".format(keyword=key_word,key=key_word ))
	search_book = book_db.fetchall()

	if (search_book==[]):
		error = "我們找不到{key_word}".format(key_word=key_word)
		form = SearchForm()
		return render_template('search_input.html',form=form, error=error)

	else:
		return render_template(
			'search_solution.html',
			search_book=search_book,
	)

		conn_book_db.close()

#---------------------------------------------------------------
#Borrow Book

class Borrow_Peo_Form(FlaskForm):
	people_word = StringField('成員編碼',validators=[DataRequired()])

class Borrow_Book_Form(FlaskForm):
	book_word = StringField('書目編碼',validators=[DataRequired()])

@app.route('/borrow/peo_again/<account>/<password>/<error>', methods = ['GET', 'POST'])
def borrow_peo_again(account,password,error):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			form = Borrow_Peo_Form()
			back_home = '管理者'
			return render_template('borrow_again_peoinput.html', form=form, error=error, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			form = Borrow_Peo_Form()
			back_home = '使用者'
			return render_template('borrow_again_peoinput.html', form=form, error=error, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


@app.route('/borrow/people_id/input/<account>/<password>', methods = ['GET', 'POST'])
def borrow_peo(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			form = Borrow_Peo_Form()
			back_home = '管理者'
			return render_template('borrow_peo_id_input.html',form=form, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			form = Borrow_Peo_Form()
			back_home = '使用者'
			return render_template('borrow_peo_id_input.html',form=form, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)



@app.route('/borrow/book_id/input/<account>/<password>', methods = ['GET', 'POST'])
def borrow_book(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			peo_db = conn_peo_db.cursor()
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			book_db = conn_book_db.cursor()

			borrow_peo_id = request.form.get('people_word')

			peo_db.execute("SELECT people_id, people_status, people_class, people_number, people_name FROM peoplelist WHERE people_id = '{peopleid}'".format(peopleid=borrow_peo_id, ))
			b = peo_db.fetchone()

			if (b==None):
				borrow_peo_again_url = url_for('borrow_peo_again',error='資料裡沒有{peo_id}這個成員'.format(peo_id=borrow_peo_id), account=account, password=password)
				return redirect(borrow_peo_again_url)

			else:
				book_db.execute("SELECT id FROM booklist WHERE people_id='{peopleid}'".format(peopleid=borrow_peo_id))
				peo_bor_book_number = book_db.fetchall()

				peo_db.execute("SELECT people_id, people_status, people_class, people_number, people_name FROM peoplelist WHERE people_id = '{peopleid}'".format(peopleid=borrow_peo_id, ))
				bor_peo_id, bor_peo_sta, bor_peo_class, bor_peo_num, bor_peo_name = peo_db.fetchone()

				book_db.execute("SELECT book_id, book_name, borrow_time FROM booklist WHERE people_id='{peopleid}'".format(peopleid=borrow_peo_id))
				print_bor_book = book_db.fetchall()

				form = Borrow_Book_Form()
				back_home = '管理者'
				return render_template('borrow_book_id_input.html',form=form, peo_id=bor_peo_id, peo_sta=bor_peo_sta, peo_class=bor_peo_class, peo_num=bor_peo_num, peo_name=bor_peo_name, print_bor_book=print_bor_book, peo_word=borrow_peo_id, account=account, password=password, back_home=back_home,  )

		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			peo_db = conn_peo_db.cursor()
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			book_db = conn_book_db.cursor()

			borrow_peo_id = request.form.get('people_word')

			peo_db.execute("SELECT people_id, people_status, people_class, people_number, people_name FROM peoplelist WHERE people_id = '{peopleid}'".format(peopleid=borrow_peo_id, ))
			b = peo_db.fetchone()

			if (b==None):
				borrow_peo_again_url = url_for('borrow_peo_again',error='資料裡沒有{peo_id}這個成員'.format(peo_id=borrow_peo_id), account=account, password=password)
				return redirect(borrow_peo_again_url)

			else:
				book_db.execute("SELECT id FROM booklist WHERE people_id='{peopleid}'".format(peopleid=borrow_peo_id))
				peo_bor_book_number = book_db.fetchall()

				peo_db.execute("SELECT people_id, people_status, people_class, people_number, people_name FROM peoplelist WHERE people_id = '{peopleid}'".format(peopleid=borrow_peo_id, ))
				bor_peo_id, bor_peo_sta, bor_peo_class, bor_peo_num, bor_peo_name = peo_db.fetchone()

				book_db.execute("SELECT book_id, book_name, borrow_time FROM booklist WHERE people_id='{peopleid}'".format(peopleid=borrow_peo_id))
				print_bor_book = book_db.fetchall()

				form = Borrow_Book_Form()
				back_home = '使用者'
				return render_template('borrow_book_id_input.html',form=form, peo_id=bor_peo_id, peo_sta=bor_peo_sta, peo_class=bor_peo_class, peo_num=bor_peo_num, peo_name=bor_peo_name, print_bor_book=print_bor_book, peo_word=borrow_peo_id, account=account, password=password, back_home=back_home,  )

		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)



@app.route('/borrow/book_again/<account>/<password>/<error>/<print_bor_book>/<peo_word>', methods = ['GET', 'POST'])
def borrow_book_again(account,password,error, print_bor_book, peo_word):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			form = Borrow_Book_Form()
			back_home = '管理者'
			return render_template('borrow_again_bookinput.html', account=account, password=password, form=form,error=error, print_bor_book=print_bor_book, peo_word=peo_word, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			form = Borrow_Book_Form()
			back_home = '使用者'
			return render_template('borrow_again_bookinput.html', account=account, password=password, form=form,error=error, print_bor_book=print_bor_book, peo_word=peo_word, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


@app.route('/borrow_solution/<account>/<password>', methods=['POST'])
def borrow_solution(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			peo_db = conn_peo_db.cursor()
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			book_db = conn_book_db.cursor()
			conn_history_db = psycopg2.connect(database="history", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			history_db = conn_history_db.cursor()

			borrow_book_id = request.form.get('book_word')
			borrow_peo_id = request.form.get('peo_word')

			book_db.execute("SELECT book_name, if_borrow, people_id, borrow_status, borrow_class, people_number, people_name, borrow_time FROM booklist WHERE book_id = '{bookid}'".format(bookid=borrow_book_id, ))
			a = book_db.fetchone()

			peo_db.execute("SELECT people_id, people_status, people_class, people_number, people_name FROM peoplelist WHERE people_id = '{peopleid}'".format(peopleid=borrow_peo_id, ))
			b = peo_db.fetchone()

			book_db.execute("SELECT book_id, book_name, borrow_time FROM booklist WHERE people_id='{peopleid}'".format(peopleid=borrow_peo_id))
			print_bor_book = book_db.fetchall()

			peo_db.execute("SELECT people_id, people_status, people_class, people_number, people_name FROM peoplelist WHERE people_id = '{peopleid}'".format(peopleid=borrow_peo_id, ))
			bor_peo_id, bor_peo_sta, bor_peo_cla, bor_peo_num, bor_peo_name = peo_db.fetchone()

			if (a==None):
				form = Borrow_Book_Form()
				back_home = '管理者'
				return render_template('borrow_solution.html',account=account,password=password,form=form, peo_id=bor_peo_id, peo_sta=bor_peo_sta, peo_class=bor_peo_cla, peo_num=bor_peo_num, peo_name=bor_peo_name, print_bor_book=print_bor_book, peo_word=borrow_peo_id, error='資料裡沒有{book_id}這本書'.format(book_id=borrow_book_id), back_home=back_home, )


			else:
				book_db.execute("SELECT book_name, if_borrow FROM booklist WHERE book_id = '{bookid}'".format(bookid=borrow_book_id, ))
				bor_book_name, bor_book_ifborrow = book_db.fetchone()

				book_db.execute("SELECT id FROM booklist WHERE people_id='{peopleid}'".format(peopleid=borrow_peo_id))
				bor_book_num = len(book_db.fetchall())

				book_db.execute("SELECT book_id, book_name, borrow_time FROM booklist WHERE people_id='{peopleid}'".format(peopleid=borrow_peo_id))
				print_bor_book = book_db.fetchall()

				if (bor_book_ifborrow=='已借出'):
					form = Borrow_Book_Form()
					back_home = '管理者'
					return render_template('borrow_solution.html', account=account, password=password, form=form, peo_id=bor_peo_id, peo_sta=bor_peo_sta, peo_class=bor_peo_cla, peo_num=bor_peo_num, peo_name=bor_peo_name, print_bor_book=print_bor_book, peo_word=borrow_peo_id, error='{book_id}已被借出'.format(book_id=borrow_book_id), back_home=back_home, )

				elif (bor_book_name==None):
					error = '未找到{borrow_book_id}此本書'.format(borrow_book_id=borrow_book_id, )
					form = Borrow_Book_Form()
					back_home = '管理者'
					return render_template('borrow_solution.html', account=account, password=password, form=form, peo_id=bor_peo_id, peo_sta=bor_peo_sta, peo_class=bor_peo_cla, peo_num=bor_peo_num, peo_name=bor_peo_name, print_bor_book=print_bor_book, peo_word=borrow_peo_id, error=error, back_home=back_home, )

				elif (bor_peo_sta=='學生' or bor_peo_sta=='家長'):
					if (bor_book_num>=2):
						borrow_peo_again_url = url_for('borrow_peo_again', account=account, password=password, error='{peo_id}已達借書上限'.format(peo_id=borrow_peo_id), print_bor_book=print_bor_book)
						return redirect(borrow_peo_again_url)

					else:
						#bor_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) -----此為import time 的方法
						time_now = datetime.datetime.now()
						bor_time = "{year_now}.{month_now}.{day_now} {hour_now}:{minute_now}:{second_now}".format(year_now=time_now.year, month_now=time_now.month, day_now=time_now.day, hour_now=time_now.hour, minute_now=time_now.minute, second_now=time_now.second, )
						book_db.execute(
							"UPDATE booklist SET if_borrow='已借出',"
							"people_id='{peo_id}', borrow_status='{bor_sta}', "
							"borrow_class='{bor_cla}', people_number='{peo_num}', "
							"people_name='{peo_name}', borrow_time='{bor_time}' "
							"WHERE book_id='{bookid}'".format(peo_id=bor_peo_id, bor_sta=bor_peo_sta, bor_cla=bor_peo_cla, peo_num=bor_peo_num, peo_name=bor_peo_name, bor_time=bor_time, bookid=borrow_book_id, ))
						conn_book_db.commit()

						history_db.execute("INSERT INTO history (borrow_time,book_id,book_name,if_borrow,people_id,people_status,people_class,people_number,people_name) "
							"VALUES ('{borrow_time}','{borrow_book_id}','{bor_book_name}', "
							"'借出','{borrow_peo_id}','{bor_peo_sta}','{bor_peo_cla}','{bor_peo_num}', "
							"'{bor_peo_name}')".format(borrow_time=bor_time, borrow_book_id=borrow_book_id, bor_book_name=bor_book_name, borrow_peo_id=borrow_peo_id, bor_peo_sta=bor_peo_sta, bor_peo_cla=bor_peo_cla, bor_peo_num=bor_peo_num, bor_peo_name=bor_peo_name, ))
						conn_history_db.commit()

						book_db.execute("SELECT book_id, book_name, borrow_time FROM booklist WHERE people_id='{peopleid}'".format(peopleid=borrow_peo_id))
						print_bor_book = book_db.fetchall()

						form = Borrow_Book_Form()
						back_home = '管理者'
						return render_template('borrow_solution.html', account=account, password=password,form=form, peo_id=bor_peo_id, peo_sta=bor_peo_sta, peo_class=bor_peo_cla, peo_num=bor_peo_num, peo_name=bor_peo_name, print_bor_book=print_bor_book, peo_word=borrow_peo_id, back_home=back_home, )

				else:
					time_now = datetime.datetime.now()
					bor_time = "{year_now}.{month_now}.{day_now} {hour_now}:{minute_now}:{second_now}".format(year_now=time_now.year, month_now=time_now.month, day_now=time_now.day, hour_now=time_now.hour, minute_now=time_now.minute, second_now=time_now.second, )

					book_db.execute(
						"UPDATE booklist SET if_borrow='已借出',"
						"people_id='{peo_id}', borrow_status='{bor_sta}', "
						"borrow_class='{bor_cla}', people_number='{peo_num}', "
						"people_name='{peo_name}', borrow_time='{bor_time}' "
						"WHERE book_id='{bookid}'".format(peo_id=bor_peo_id, bor_sta=bor_peo_sta, bor_cla=bor_peo_cla, peo_num=bor_peo_num, peo_name=bor_peo_name, bor_time=bor_time, bookid=borrow_book_id, ))
					conn_book_db.commit()

					history_db.execute("INSERT INTO history (borrow_time,book_id,book_name,if_borrow,people_id,people_status,people_class,people_number,people_name) "
							"VALUES ('{borrow_time}','{borrow_book_id}','{bor_book_name}', "
							"'借出','{borrow_peo_id}','{bor_peo_sta}','{bor_peo_cla}','{bor_peo_num}', "
							"'{bor_peo_name}')".format(borrow_time=bor_time, borrow_book_id=borrow_book_id, bor_book_name=bor_book_name, borrow_peo_id=borrow_peo_id, bor_peo_sta=bor_peo_sta, bor_peo_cla=bor_peo_cla, bor_peo_num=bor_peo_num, bor_peo_name=bor_peo_name, ))
					conn_history_db.commit()

					book_db.execute("SELECT book_id, book_name, borrow_time FROM booklist WHERE people_id='{peopleid}'".format(peopleid=borrow_peo_id))
					print_bor_book = book_db.fetchall()

					form = Borrow_Book_Form()
					back_home = '管理者'
					return render_template('borrow_solution.html', account=account, password=password,form=form, peo_id=bor_peo_id, peo_sta=bor_peo_sta, peo_class=bor_peo_cla, peo_num=bor_peo_num, peo_name=bor_peo_name, print_bor_book=print_bor_book, peo_word=borrow_peo_id, back_home=back_home, )

				conn_book_db.close()
				conn_peo_db.close()

		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			peo_db = conn_peo_db.cursor()
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			book_db = conn_book_db.cursor()

			borrow_book_id = request.form.get('book_word')
			borrow_peo_id = request.form.get('peo_word')

			book_db.execute("SELECT book_name, if_borrow, people_id, borrow_status, borrow_class, people_number, people_name, borrow_time FROM booklist WHERE book_id = '{bookid}'".format(bookid=borrow_book_id, ))
			a = book_db.fetchone()

			peo_db.execute("SELECT people_id, people_status, people_class, people_number, people_name FROM peoplelist WHERE people_id = '{peopleid}'".format(peopleid=borrow_peo_id, ))
			b = peo_db.fetchone()

			book_db.execute("SELECT book_id, book_name, borrow_time FROM booklist WHERE people_id='{peopleid}'".format(peopleid=borrow_peo_id))
			print_bor_book = book_db.fetchall()

			peo_db.execute("SELECT people_id, people_status, people_class, people_number, people_name FROM peoplelist WHERE people_id = '{peopleid}'".format(peopleid=borrow_peo_id, ))
			bor_peo_id, bor_peo_sta, bor_peo_class, bor_peo_num, bor_peo_name = peo_db.fetchone()

			if(a==None):
				form = Borrow_Book_Form()
				back_home = '使用者'
				return render_template('borrow_solution.html', account=account, password=password, form=form, peo_id=bor_peo_id, peo_sta=bor_peo_sta, peo_class=bor_peo_class, peo_num=bor_peo_num, peo_name=bor_peo_name, print_bor_book=print_bor_book, peo_word=borrow_peo_id, error='資料裡沒有{book_id}這本書'.format(book_id=borrow_book_id), back_home=back_home, )

			else:
				book_db.execute("SELECT book_name, if_borrow FROM booklist WHERE book_id = '{bookid}'".format(bookid=borrow_book_id, ))
				bor_book_name, bor_book_ifborrow = book_db.fetchone()

				book_db.execute("SELECT id FROM booklist WHERE people_id='{peopleid}'".format(peopleid=borrow_peo_id))
				bor_book_num = len(book_db.fetchall())

				book_db.execute("SELECT book_id, book_name, borrow_time FROM booklist WHERE people_id='{peopleid}'".format(peopleid=borrow_peo_id))
				print_bor_book = book_db.fetchall()

				if (bor_book_ifborrow=='已借出'):
					form = Borrow_Book_Form()
					back_home = '使用者'
					return render_template('borrow_solution.html', account=account, password=password, form=form, peo_id=bor_peo_id, peo_sta=bor_peo_sta, peo_class=bor_peo_class, peo_num=bor_peo_num, peo_name=bor_peo_name, print_bor_book=print_bor_book, peo_word=borrow_peo_id, error='{book_id}已被借出'.format(book_id=borrow_book_id), back_home=back_home, )

				elif (bor_book_name==None):
					error = '未找到{borrow_book_id}此本書'.format(borrow_book_id=borrow_book_id, )
					form = Borrow_Book_Form()
					back_home = '使用者'
					return render_template('borrow_solution.html', account=account, password=password, form=form, peo_id=bor_peo_id, peo_sta=bor_peo_sta, peo_class=bor_peo_cla, peo_num=bor_peo_num, peo_name=bor_peo_name, print_bor_book=print_bor_book, peo_word=borrow_peo_id, error=error, back_home=back_home, )

				elif (bor_peo_sta=='學生' or bor_peo_sta=='家長'):
					if (bor_book_num>=2):
						borrow_peo_again_url = url_for('borrow_peo_again', account=account, password=password, error='{peo_id}已達借書上限'.format(peo_id=borrow_peo_id), print_bor_book=print_bor_book)
						return redirect(borrow_peo_again_url)

					else:
						#bor_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) -----此為import time 的方法
						time_now = datetime.datetime.now()
						bor_time = "{year_now}.{month_now}.{day_now} {hour_now}:{minute_now}:{second_now}".format(year_now=time_now.year, month_now=time_now.month, day_now=time_now.day, hour_now=time_now.hour, minute_now=time_now.minute, second_now=time_now.second, )
						book_db.execute(
							"UPDATE booklist SET if_borrow='已借出',"
							"people_id='{peo_id}', borrow_status='{bor_sta}', "
							"borrow_class='{bor_cla}', people_number='{peo_num}', "
							"people_name='{peo_name}', borrow_time='{bor_time}' "
							"WHERE book_id='{bookid}'".format(peo_id=bor_peo_id, bor_sta=bor_peo_sta, bor_cla=bor_peo_class, peo_num=bor_peo_num, peo_name=bor_peo_name, bor_time=bor_time, bookid=borrow_book_id, ))
						conn_book_db.commit()

						history_db.execute("INSERT INTO history (borrow_time,book_id,book_name,if_borrow,people_id,people_status,people_class,people_number,people_name) "
							"VALUES ('{borrow_time}','{borrow_book_id}','{bor_book_name}', "
							"'借出','{borrow_peo_id}','{bor_peo_sta}','{bor_peo_cla}','{bor_peo_num}', "
							"'{bor_peo_name}')".format(borrow_time=bor_time, borrow_book_id=borrow_book_id, bor_book_name=bor_book_name, borrow_peo_id=borrow_peo_id, bor_peo_sta=bor_peo_sta, bor_peo_cla=bor_peo_cla, bor_peo_num=bor_peo_num, bor_peo_name=bor_peo_name, ))
						conn_history_db.commit()

						book_db.execute("SELECT book_id, book_name, borrow_time FROM booklist WHERE people_id='{peopleid}'".format(peopleid=borrow_peo_id))
						print_bor_book = book_db.fetchall()

						form = Borrow_Book_Form()
						back_home = '使用者'
						return render_template('borrow_solution.html', account=account, password=password,form=form, peo_id=bor_peo_id, peo_sta=bor_peo_sta, peo_class=bor_peo_class, peo_num=bor_peo_num, peo_name=bor_peo_name, print_bor_book=print_bor_book, peo_word=borrow_peo_id, back_home=back_home, )

				else:
					time_now = datetime.datetime.now()
					bor_time = "{year_now}.{month_now}.{day_now} {hour_now}:{minute_now}:{second_now}".format(year_now=time_now.year, month_now=time_now.month, day_now=time_now.day, hour_now=time_now.hour, minute_now=time_now.minute, second_now=time_now.second, )

					book_db.execute(
						"UPDATE booklist SET if_borrow='已借出',"
						"people_id='{peo_id}', borrow_status='{bor_sta}', "
						"borrow_class='{bor_cla}', people_number='{peo_num}', "
						"people_name='{peo_name}', borrow_time='{bor_time}' "
						"WHERE book_id='{bookid}'".format(peo_id=bor_peo_id, bor_sta=bor_peo_sta, bor_cla=bor_peo_cla, peo_num=bor_peo_num, peo_name=bor_peo_name, bor_time=bor_time, bookid=borrow_book_id, ))
					conn_book_db.commit()

					history_db.execute("INSERT INTO history (borrow_time,book_id,book_name,if_borrow,people_id,people_status,people_class,people_number,people_name) "
						"VALUES ('{borrow_time}','{borrow_book_id}','{bor_book_name}', "
						"'借出','{borrow_peo_id}','{bor_peo_sta}','{bor_peo_cla}','{bor_peo_num}', "
						"'{bor_peo_name}')".format(borrow_time=bor_time, borrow_book_id=borrow_book_id, bor_book_name=bor_book_name, borrow_peo_id=borrow_peo_id, bor_peo_sta=bor_peo_sta, bor_peo_cla=bor_peo_cla, bor_peo_num=bor_peo_num, bor_peo_name=bor_peo_name, ))
					conn_history_db.commit()

					book_db.execute("SELECT book_id, book_name, borrow_time FROM booklist WHERE people_id='{peopleid}'".format(peopleid=borrow_peo_id))
					print_bor_book = book_db.fetchall()

					form = Borrow_Book_Form()
					back_home = '使用者'
					return render_template('borrow_solution.html', account=account, password=password,form=form, peo_id=bor_peo_id, peo_sta=bor_peo_sta, peo_class=bor_peo_class, peo_num=bor_peo_num, peo_name=bor_peo_name, print_bor_book=print_bor_book, peo_word=borrow_peo_id, back_home=back_home, )

				conn_book_db.close()
				conn_peo_db.close()

		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


#--------------------------------------------------------------------------
#Return Book

class Return_Peo_Form(FlaskForm):
	people_word = StringField('成員編碼',validators=[DataRequired()])

class Return_Book_Form(FlaskForm):
	book_word = StringField('書目編碼',validators=[DataRequired()])

@app.route('/return/peo_again/<account>/<password>/<error>', methods = ['GET', 'POST'])
def return_peo_again(account,password,error):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			form = Return_Peo_Form()
			back_home = '管理者'
			return render_template('return_again_peoinput.html', form=form, error=error, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			form = Return_Peo_Form()
			back_home = '使用者'
			return render_template('return_again_peoinput.html', form=form, error=error, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)



@app.route('/return/people_id/input/<account>/<password>', methods = ['GET', 'POST'])
def return_peo(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			form = Return_Peo_Form()
			back_home = '管理者'
			return render_template('return_peo_id_input.html',form=form, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			form = Return_Peo_Form()
			back_home = '使用者'
			return render_template('return_peo_id_input.html',form=form, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


@app.route('/return/book_id/input/<account>/<password>', methods = ['GET', 'POST'])
def return_book(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			peo_db = conn_peo_db.cursor()
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			book_db = conn_book_db.cursor()

			return_peo_id = request.form.get('people_word')

			peo_db.execute("SELECT people_id, people_status, people_class, people_number, people_name FROM peoplelist WHERE people_id = '{peopleid}'".format(peopleid=return_peo_id, ))
			b = peo_db.fetchone()

			if (b==None):
				return_peo_again_url = url_for('return_peo_again',error='資料裡沒有{peo_id}這個成員'.format(peo_id=return_peo_id), account=account, password=password, )
				return redirect(return_peo_again_url)

			else:
				peo_db.execute("SELECT people_id, people_status, people_class, people_number, people_name FROM peoplelist WHERE people_id = '{peopleid}'".format(peopleid=return_peo_id, ))
				ret_peo_id, ret_peo_sta, ret_peo_class, ret_peo_num, ret_peo_name = peo_db.fetchone()

				book_db.execute("SELECT book_id, book_name, borrow_time FROM booklist WHERE people_id='{peopleid}'".format(peopleid=return_peo_id))
				print_bor_book = book_db.fetchall()

				form = Return_Book_Form()
				back_home = '管理者'
				return render_template('return_book_id_input.html',form=form, peo_id=ret_peo_id, peo_sta=ret_peo_sta, peo_class=ret_peo_class, peo_num=ret_peo_num, peo_name=ret_peo_name, print_bor_book=print_bor_book, peo_word=return_peo_id, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			peo_db = conn_peo_db.cursor()
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			book_db = conn_book_db.cursor()

			return_peo_id = request.form.get('people_word')

			peo_db.execute("SELECT people_id, people_status, people_class, people_number, people_name FROM peoplelist WHERE people_id = '{peopleid}'".format(peopleid=return_peo_id, ))
			b = peo_db.fetchone()

			if (b==None):
				return_peo_again_url = url_for('return_peo_again',error='資料裡沒有{peo_id}這個成員'.format(peo_id=return_peo_id), account=account, password=password, )
				return redirect(return_peo_again_url)

			else:
				peo_db.execute("SELECT people_id, people_status, people_class, people_number, people_name FROM peoplelist WHERE people_id = '{peopleid}'".format(peopleid=return_peo_id, ))
				ret_peo_id, ret_peo_sta, ret_peo_class, ret_peo_num, ret_peo_name = peo_db.fetchone()

				book_db.execute("SELECT book_id, book_name, borrow_time FROM booklist WHERE people_id='{peopleid}'".format(peopleid=return_peo_id))
				print_bor_book = book_db.fetchall()

				form = Return_Book_Form()
				back_home = '使用者'
				return render_template('return_book_id_input.html',form=form, peo_id=ret_peo_id, peo_sta=ret_peo_sta, peo_class=ret_peo_class, peo_num=ret_peo_num, peo_name=ret_peo_name, print_bor_book=print_bor_book, peo_word=return_peo_id, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


@app.route('/return/book_again/<account>/<password>/<error>/<print_bor_book>/<peo_word>', methods = ['GET', 'POST'])
def return_book_again(account,password,error, print_bor_book, peo_word):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			form = Return_Book_Form()
			back_home = '管理者'
			return render_template('return_again_bookinput.html',form=form,error=error, print_bor_book=print_bor_book, peo_word=peo_word, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			form = Return_Book_Form()
			back_home = '使用者'
			return render_template('return_again_bookinput.html',form=form,error=error, print_bor_book=print_bor_book, peo_word=peo_word, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


@app.route('/return_solution/<account>/<password>', methods=['POST'])
def return_solution(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			peo_db = conn_peo_db.cursor()
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			book_db = conn_book_db.cursor()
			conn_history_db = psycopg2.connect(database="history", user="stella", password="Janeslowly")
			history_db = conn_history_db.cursor()

			return_book_id = request.form.get('book_word')
			return_peo_id = request.form.get('peo_word')

			#顯示資料，確認有無上傳成功
			#for row in book_db.execute("SELECT * FROM booklist"):
			#		print(row)
			#for row in peo_db.execute("SELECT * FROM peoplelist"):
			#	print(row)

			book_db.execute("SELECT book_name, if_borrow, people_id, borrow_status, borrow_class, people_number, people_name, borrow_time FROM booklist WHERE book_id = '{bookid}'".format(bookid=return_book_id, ))
			a = book_db.fetchone()

			peo_db.execute("SELECT people_id, people_status, people_class, people_number, people_name FROM peoplelist WHERE people_id = '{peopleid}'".format(peopleid=return_peo_id, ))
			b = peo_db.fetchone()

			book_db.execute("SELECT book_id, book_name, borrow_time FROM booklist WHERE people_id='{peopleid}'".format(peopleid=return_peo_id))
			print_bor_book = book_db.fetchall()

			if(a==None):
				return_book_again_url = url_for('return_book_again',error='資料裡沒有{book_id}這本書'.format(book_id=return_book_id), print_bor_book=print_bor_book, peo_word=return_peo_id, account=account, password=password, )
				return redirect(return_book_again_url)

			else:
				book_db.execute("SELECT book_name, if_borrow FROM booklist WHERE book_id = '{bookid}'".format(bookid=return_book_id, ))
				ret_book_name, ret_book_ifborrow = book_db.fetchone()

				peo_db.execute("SELECT people_id, people_status, people_class, people_number, people_name FROM peoplelist WHERE people_id = '{peopleid}'".format(peopleid=return_peo_id, ))
				ret_peo_id, ret_peo_sta, ret_peo_class, ret_peo_num, ret_peo_name = peo_db.fetchone()

				book_db.execute("SELECT id FROM booklist WHERE people_id='{peopleid}'".format(peopleid=return_peo_id))
				bor_book_num = len(book_db.fetchall())

				if (ret_book_ifborrow=='未借出'):
					return_book_again_url = url_for('return_book_again',error='{book_id}已被借出'.format(book_id=return_book_id), print_bor_book=print_bor_book, peo_word=return_peo_id, account=account, password=password, )
					return redirect(return_book_again_url)

				else:
					book_db.execute("UPDATE booklist SET if_borrow='未借出', people_id=Null, borrow_status=Null, borrow_class=Null, people_number=Null, people_name=Null, borrow_time=Null WHERE book_id='{bookid}'".format( bookid=return_book_id, ))
					conn_book_db.commit()

					book_db.execute("SELECT book_id, book_name, borrow_time FROM booklist WHERE people_id='{peopleid}'".format(peopleid=return_peo_id))
					print_bor_book = book_db.fetchall()

					time_now = datetime.datetime.now()
					ret_time = "{year_now}.{month_now}.{day_now} {hour_now}:{minute_now}:{second_now}".format(year_now=time_now.year, month_now=time_now.month, day_now=time_now.day, hour_now=time_now.hour, minute_now=time_now.minute, second_now=time_now.second, )

					history_db.execute("INSERT INTO history (borrow_time,book_id,book_name,if_borrow,people_id,people_status,people_class,people_number,people_name) "
						"VALUES ('{return_time}','{return_book_id}','{ret_book_name}', "
						"'還書','{return_peo_id}','{ret_peo_sta}','{ret_peo_cla}','{ret_peo_num}', "
						"'{ret_peo_name}')".format(return_time=ret_time, return_book_id=return_book_id, ret_book_name=ret_book_name, return_peo_id=return_peo_id, ret_peo_sta=ret_peo_sta, ret_peo_cla=ret_peo_class, ret_peo_num=ret_peo_num, ret_peo_name=ret_peo_name, ))
					conn_history_db.commit()

					form = Return_Book_Form()
					back_home = '管理者'
					return render_template('return_solution.html',form=form, peo_id=ret_peo_id, peo_sta=ret_peo_sta, peo_class=ret_peo_class, peo_num=ret_peo_num, peo_name=ret_peo_name, print_bor_book=print_bor_book, peo_word=return_peo_id, account=account, password=password, back_home=back_home, )


				conn_book_db.close()
				conn_peo_db.close()

		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			peo_db = conn_peo_db.cursor()
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			book_db = conn_book_db.cursor()

			return_book_id = request.form.get('book_word')
			return_peo_id = request.form.get('peo_word')

			#顯示資料，確認有無上傳成功
			#for row in book_db.execute("SELECT * FROM booklist"):
			#		print(row)
			#for row in peo_db.execute("SELECT * FROM peoplelist"):
			#	print(row)

			book_db.execute("SELECT book_name, if_borrow, people_id, borrow_status, borrow_class, people_number, people_name, borrow_time FROM booklist WHERE book_id = '{bookid}'".format(bookid=return_book_id, ))
			a = book_db.fetchone()

			peo_db.execute("SELECT people_id, people_status, people_class, people_number, people_name FROM peoplelist WHERE people_id = '{peopleid}'".format(peopleid=return_peo_id, ))
			b = peo_db.fetchone()

			book_db.execute("SELECT book_id, book_name, borrow_time FROM booklist WHERE people_id='{peopleid}'".format(peopleid=return_peo_id))
			print_bor_book = book_db.fetchall()

			if(a==None):
				return_book_again_url = url_for('return_book_again',error='資料裡沒有{book_id}這本書'.format(book_id=return_book_id), print_bor_book=print_bor_book, peo_word=return_peo_id, account=account, password=password, )
				return redirect(return_book_again_url)

			else:
				book_db.execute("SELECT book_name, if_borrow FROM booklist WHERE book_id = '{bookid}'".format(bookid=return_book_id, ))
				ret_book_name, ret_book_ifborrow = book_db.fetchone()

				peo_db.execute("SELECT people_id, people_status, people_class, people_number, people_name FROM peoplelist WHERE people_id = '{peopleid}'".format(peopleid=return_peo_id, ))
				ret_peo_id, ret_peo_sta, ret_peo_class, ret_peo_num, ret_peo_name = peo_db.fetchone()

				book_db.execute("SELECT id FROM booklist WHERE people_id='{peopleid}'".format(peopleid=return_peo_id))
				bor_book_num = len(book_db.fetchall())

				if (ret_book_ifborrow=='未借出'):
					return_book_again_url = url_for('return_book_again',error='{book_id}已被借出'.format(book_id=return_book_id), print_bor_book=print_bor_book, peo_word=return_peo_id, account=account, password=password, )
					return redirect(return_book_again_url)

				else:
					book_db.execute("UPDATE booklist SET if_borrow='未借出', people_id=Null, borrow_status=Null, borrow_class=Null, people_number=Null, people_name=Null, borrow_time=Null WHERE book_id='{bookid}'".format( bookid=return_book_id, ))
					conn_book_db.commit()

					book_db.execute("SELECT book_id, book_name, borrow_time FROM booklist WHERE people_id='{peopleid}'".format(peopleid=return_peo_id))
					print_bor_book = book_db.fetchall()

					time_now = datetime.datetime.now()
					ret_time = "{year_now}.{month_now}.{day_now} {hour_now}:{minute_now}:{second_now}".format(year_now=time_now.year, month_now=time_now.month, day_now=time_now.day, hour_now=time_now.hour, minute_now=time_now.minute, second_now=time_now.second, )

					history_db.execute("INSERT INTO history (borrow_time,book_id,book_name,if_borrow,people_id,people_status,people_class,people_number,people_name) "
						"VALUES ('{return_time}','{return_book_id}','{ret_book_name}', "
						"'還書','{return_peo_id}','{ret_peo_sta}','{ret_peo_cla}','{ret_peo_num}', "
						"'{ret_peo_name}')".format(return_time=ret_time, return_book_id=return_book_id, ret_book_name=ret_book_name, return_peo_id=return_peo_id, ret_peo_sta=ret_peo_sta, ret_peo_cla=ret_peo_class, ret_peo_num=ret_peo_num, ret_peo_name=ret_peo_name, ))
					conn_history_db.commit()

					history_db.execute("SELECT * FROM history")
					print(history_db.fetchall())

					form = Return_Book_Form()
					back_home = '使用者'
					return render_template('return_solution.html',form=form, peo_id=ret_peo_id, peo_sta=ret_peo_sta, peo_class=ret_peo_class, peo_num=ret_peo_num, peo_name=ret_peo_name, print_bor_book=print_bor_book, peo_word=return_peo_id, account=account, password=password, back_home=back_home, )

				conn_book_db.close()
				conn_peo_db.close()

		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


#------------------------------------------------------------------
#Unreturn Book

class UnreturnForm(FlaskForm):
	key_word = StringField('關鍵字：', description=['可輸入書目編碼、書名、成員編碼、成員姓名、成員班級、成員身份等關鍵字。'],validators=[DataRequired()],)


@app.route('/unreturn/<account>/<password>', methods = ['GET', 'POST'])
def unreturn(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]
	print('password:',user_account)
	print('man_pass',account)

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			form = UnreturnForm()
			back_home = '管理者'
			return render_template('unreturn_input.html', form=form, account=account, password=password, back_home=back_home, )

		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


@app.route('/unreturn_solution/<account>/<password>', methods=['GET', 'POST'])
def unreturn_solution(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]
	print('password:',user_account)
	print('man_pass',account)

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			book_db = conn_book_db.cursor()
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			peo_db = conn_peo_db.cursor()

			key_word = request.form.get('key_word')

			book_db.execute(
				"SELECT * "
				"FROM booklist "
				"WHERE if_borrow='已借出' AND (book_name LIKE '%{keyword}%' "
				"OR book_id LIKE '%{keyword}%' OR people_id LIKE '%{keyword}%'"
				"OR people_name LIKE '%{keyword}%' OR borrow_class LIKE '%{keyword}%'"
				"OR borrow_status LIKE '%{keyword}%')".format(keyword=key_word, ))

			unreturn_book = book_db.fetchall()

			if (unreturn_book==[]):
				error = "我們找不到{key_word}".format(key_word=key_word)
				form = UnreturnForm()
				back_home = '管理者'
				return render_template('unreturn_input.html',form=form, error=error, account=account, password=password, back_home=back_home, )

			else:
				back_home = '管理者'
				return render_template('unreturn_solution.html',unreturn_book=unreturn_book,account=account, password=password, back_home=back_home, )

			conn_book_db.close()

		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			book_db = conn_book_db.cursor()
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			peo_db = conn_peo_db.cursor()

			key_word = request.form.get('key_word')

			book_db.execute(
				"SELECT *"
				"FROM booklist "
				"WHERE if_borrow='已借出' AND (book_name LIKE '%{keyword}%' "
				"OR book_id LIKE '%{keyword}%' OR people_id LIKE '%{keyword}%'"
				"OR people_name LIKE '%{keyword}%' OR borrow_class LIKE '%{keyword}%'"
				"OR borrow_status LIKE '%{keyword}%')".format(keyword=key_word, ))

			unreturn_book = book_db.fetchall()

			if (unreturn_book==[]):
				error = "我們找不到{key_word}".format(key_word=key_word)
				form = UnreturnForm()
				back_home = '使用者'
				return render_template('unreturn_input.html',form=form, error=error, account=account, password=password, back_home=back_home, )

			else:
				back_home = '使用者'
				return render_template('unreturn_solution.html',unreturn_book=unreturn_book,account=account, password=password, back_home=back_home, )

			conn_book_db.close()

		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)



@app.route('/unreturn_all/<account>/<password>', methods=['GET', 'POST'])
def unreturn_all(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]
	print('password:',user_account)
	print('man_pass',account)

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			book_db = conn_book_db.cursor()

			book_db.execute("SELECT * FROM booklist WHERE if_borrow='已借出'")
			all_unreturn_book = book_db.fetchall()
			back_home = '管理者'
			return render_template('unreturn_solution.html',unreturn_book=all_unreturn_book,account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			book_db = conn_book_db.cursor()

			book_db.execute("SELECT * FROM booklist WHERE if_borrow='已借出'")
			all_unreturn_book = book_db.fetchall()
			back_home = '使用者'
			return render_template('unreturn_solution.html',unreturn_book=all_unreturn_book,account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)





#----------------------------------------------------------------------------------
#Manager Book And Delete Book

class ManageBookForm(FlaskForm):
	account = StringField('帳號',validators=[DataRequired()])
	password = StringField('密碼',validators=[DataRequired()])


@app.route('/manager_book/choose/<account>/<password>')
def book_choose(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			back_home = '管理者'
			return render_template('book_choose.html', account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			back_home = '使用者'
			return render_template('book_choose.html', account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


class DeleteBook_Search_Form(FlaskForm):
	key_word = StringField('關鍵字',validators=[DataRequired()])

@app.route('/delete_book/search/<account>/<password>', methods = ['GET', 'POST'])
def delete_book_search(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			form = DeleteBook_Search_Form()
			back_home = '管理者'
			return render_template('delete_book_search.html', form=form, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			form = DeleteBook_Search_Form()
			back_home = '使用者'
			return render_template('delete_book_search.html', form=form, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)

class DeleteBook_Input_Form(FlaskForm):
	book_id_input = StringField('書目編碼', validators=[DataRequired()])

@app.route('/delete_book/input/<account>/<password>', methods = ['GET', 'POST'])
def delete_book_input(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", )
			book_db = conn_book_db.cursor()

			key_word = request.form.get('key_word')

			book_db.execute(
				"SELECT book_id, book_name, if_borrow,"
				"people_id, borrow_status, borrow_class, "
				"people_number, people_name, borrow_time "
				"FROM booklist "
				"WHERE book_name LIKE '%{keyword}%' "
				"OR book_id LIKE '%{keyword}%'".format(keyword=key_word, ))

			search_book = book_db.fetchall()

			if (search_book==[]):
				error = "我們找不到{key_word}".format(key_word=key_word)
				form = DeleteBookForm()
				back_home = '管理者'
				return render_template('delete_book_search.html', form=form, error=error, account=account, password=password, back_home=back_home, )

			else:
				form = DeleteBook_Input_Form()
				back_home = '管理者'
				return render_template('delete_book_input.html', form=form, search_book=search_book, key_word=key_word, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", )
			book_db = conn_book_db.cursor()

			key_word = request.form.get('key_word')

			book_db.execute(
				"SELECT book_id, book_name, if_borrow,"
				"people_id, borrow_status, borrow_class, "
				"people_number, people_name, borrow_time "
				"FROM booklist "
				"WHERE book_name LIKE '%{keyword}%' "
				"OR book_id LIKE '%{keyword}%'".format(keyword=key_word, ))

			search_book = book_db.fetchall()

			if (search_book==[]):
				error = "我們找不到{key_word}".format(key_word=key_word)
				form = DeleteBookForm()
				back_home = '使用者'
				return render_template('delete_book_search.html', form=form, error=error, account=account, password=password, back_home=back_home, )

			else:
				form = DeleteBook_Input_Form()
				back_home = '使用者'
				return render_template('delete_book_input.html', form=form, search_book=search_book, key_word=key_word, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


@app.route('/delete_book/sure/<account>/<password>/<key_word>', methods = ['GET', 'POST'])
def delete_book_sure(account,password,key_word):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", )
			book_db = conn_book_db.cursor()

			book_id_input = request.form.get('book_id_input')

			book_db.execute("SELECT * FROM booklist WHERE book_id='{book_id_input}'".format(book_id_input=book_id_input))
			select_delete_book = book_db.fetchone()

			book_db.execute(
				"SELECT book_id, book_name, if_borrow,"
				"people_id, borrow_status, borrow_class, "
				"people_number, people_name, borrow_time "
				"FROM booklist "
				"WHERE book_name LIKE '%{keyword}%' "
				"OR book_id LIKE '%{keyword}%'".format(keyword=key_word, ))
			search_book = book_db.fetchall()

			if (select_delete_book==None):
				form = DeleteBook_Input_Form()
				back_home = '管理者'
				return render_template('delete_book_input.html', form=form, search_book=search_book, account=account, password=password, back_home=back_home, )

			else:
				select_book_id = select_delete_book[1]
				back_home = '管理者'
				return render_template('delete_book_sure.html', select_delete_book=select_delete_book, select_book_id=select_book_id, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", )
			book_db = conn_book_db.cursor()

			book_id_input = request.form.get('book_id_input')

			book_db.execute("SELECT * FROM booklist WHERE book_id='{book_id_input}'".format(book_id_input=book_id_input))
			select_delete_book = book_db.fetchone()

			book_db.execute(
				"SELECT book_id, book_name, if_borrow,"
				"people_id, borrow_status, borrow_class, "
				"people_number, people_name, borrow_time "
				"FROM booklist "
				"WHERE book_name LIKE '%{keyword}%' "
				"OR book_id LIKE '%{keyword}%'".format(keyword=key_word, ))
			search_book = book_db.fetchall()

			if (select_delete_book==None):
				form = DeleteBook_Input_Form()
				back_home = '使用者'
				return render_template('delete_book_input.html', form=form, search_book=search_book, account=account, password=password, back_home=back_home, )

			else:
				select_book_id = select_delete_book[1]
				back_home = '使用者'
				return render_template('delete_book_sure.html', select_delete_book=select_delete_book, select_book_id=select_book_id, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


@app.route('/delete_book/solution/<account>/<password>/<select_book_id>', methods = ['GET', 'POST'])
def delete_book_solution(account,password,select_book_id):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", )
			book_db = conn_book_db.cursor()

			book_db.execute("SELECT * FROM booklist WHERE book_id='{select_book_id}'".format(select_book_id=select_book_id, ))
			select_book = book_db.fetchone()

			book_db.execute("UPDATE booklist " 
				"SET book_name=Null, if_borrow=Null,"
				"people_id=Null, borrow_status=Null,"
				"borrow_class=Null, people_number=Null, people_name=Null, borrow_time=Null "
				"WHERE book_id='{select_book_id}'".format(select_book_id=select_book_id, ))
			conn_book_db.commit()
			back_home = '管理者'
			return render_template('delete_book_success.html', select_book=select_book, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", )
			book_db = conn_book_db.cursor()

			book_db.execute("SELECT * FROM booklist WHERE book_id='{select_book_id}'".format(select_book_id=select_book_id, ))
			select_book = book_db.fetchone()

			book_db.execute("UPDATE booklist " 
				"SET book_name=Null, if_borrow='未借出',"
				"people_id=Null, borrow_status=Null,"
				"borrow_class=Null, people_number=Null, people_name=Null, borrow_time=Null "
				"WHERE book_id='{select_book_id}'".format(select_book_id=select_book_id, ))
			conn_book_db.commit()
			back_home = '使用者'
			return render_template('delete_book_success.html', select_book=select_book, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


#--------------------------------------------------------------------------------------
#Insert Book

class InsertBookForm(FlaskForm):
	insert_book_id = StringField('書目編碼：', description=['編碼開頭必須為Ｂ，後面加上五碼數字'], validators=[DataRequired()])
	insert_book_name = StringField('書名：',validators=[DataRequired()])


@app.route('/insert_book/input/<account>/<password>', methods = ['GET', 'POST'])
def insert_book_input(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", )
			book_db = conn_book_db.cursor()

			book_db.execute("SELECT book_id FROM booklist WHERE book_name IS NULL")
			empty_book_id = book_db.fetchall() #顯示空的book_id給使用者看

			book_db.execute("SELECT id,book_id FROM booklist ORDER BY id DESC LIMIT 1")
			max_book_id = book_db.fetchone() #顯示最大值的book_id給使用者看

			form = InsertBookForm()
			back_home = '管理者'
			return render_template('insert_book_input.html', form=form, empty_book_id=empty_book_id, max_book_id=max_book_id, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", )
			book_db = conn_book_db.cursor()

			book_db.execute("SELECT book_id FROM booklist WHERE book_name IS NULL")
			empty_book_id = book_db.fetchall() #顯示空的book_id給使用者看

			book_db.execute("SELECT id,book_id FROM booklist ORDER BY id DESC LIMIT 1")
			max_book_id = book_db.fetchone() #顯示最大值的book_id給使用者看

			form = InsertBookForm()
			back_home = '使用者'
			return render_template('insert_book_input.html', form=form, empty_book_id=empty_book_id, max_book_id=max_book_id, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


@app.route('/insert_book/again/<account>/<password>/<error>', methods = ['GET', 'POST'])
def insert_book_again(account,password,error):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", )
			book_db = conn_book_db.cursor()

			book_db.execute("SELECT book_id FROM booklist WHERE book_name IS NULL")
			empty_book_id = book_db.fetchall() #顯示空的book_id給使用者看

			book_db.execute("SELECT id,book_id FROM booklist ORDER BY id DESC LIMIT 1")
			max_book_id = book_db.fetchone() #顯示最大值的book_id給使用者看

			form = InsertBookForm()
			back_home = '管理者'
			return render_template('insert_book_input.html', form=form, empty_book_id=empty_book_id, max_book_id=max_book_id, error=error, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", )
			book_db = conn_book_db.cursor()

			book_db.execute("SELECT book_id FROM booklist WHERE book_name IS NULL")
			empty_book_id = book_db.fetchall() #顯示空的book_id給使用者看

			book_db.execute("SELECT id,book_id FROM booklist ORDER BY id DESC LIMIT 1")
			max_book_id = book_db.fetchone() #顯示最大值的book_id給使用者看

			form = InsertBookForm()
			back_home = '使用者'
			return render_template('insert_book_input.html', form=form, empty_book_id=empty_book_id, max_book_id=max_book_id, error=error, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


@app.route('/insert_book/solution/<account>/<password>', methods = ['GET', 'POST'])
def insert_book_solution(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", )
			book_db = conn_book_db.cursor()

			book_id_input = request.form.get('insert_book_id')
			book_name_input = request.form.get('insert_book_name')

			book_db.execute("SELECT book_id,book_name FROM booklist WHERE book_id='{book_id_input}'".format(book_id_input=book_id_input, ))
			select_book = book_db.fetchone()

			if (book_id_input[0]!='B' or len(book_id_input)!=6 or str.isdigit(book_id_input[1:])!=1):
				error = '書目編碼輸入錯誤！書目編碼需為6碼，且第1碼需為B後五碼需為數字！'.format(book_id_input=book_id_input)
				insert_book_again = url_for('insert_book_again',error=error, account=account, password=password, )
				return redirect(insert_book_again)

			elif (select_book==None):
				book_db.execute("INSERT INTO booklist (book_id,book_name,if_borrow) VALUES ('{book_id_input}','{book_name_input}','未借出')".format(book_id_input=book_id_input, book_name_input=book_name_input, ))
				conn_book_db.commit()

				book_db.execute("SELECT * FROM booklist WHERE book_id='{book_id_input}'".format(book_id_input=book_id_input, ))
				print_insert_book = book_db.fetchone()
				back_home = '管理者'
				return render_template('insert_book_success.html',print_insert_book=print_insert_book, account=account, password=password, back_home=back_home, )

			elif (select_book[1]!=None):
				error = '{book_id_input}已有書名'.format(book_id_input=book_id_input)
				insert_book_again = url_for('insert_book_again',error=error, account=account, password=password, )
				return redirect(insert_book_again)

			else:
				book_db.execute("UPDATE booklist SET book_name='{book_name_input}', if_borrow='未借出'".format(book_name_input=book_name_input, ))
				conn_book_db.commit()
				book_db.execute("SELECT * FROM booklist WHERE book_id='{book_id_input}'".format(book_id_input=book_id_input, ))
				print_insert_book = book_db.fetchone()

				book_db.close()
				conn_book_db.close()
				back_home = '管理者'
				return render_template('insert_book_success.html', print_insert_book=print_insert_book, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_book_db = psycopg2.connect(database="booklist", user="stella", password="Janeslowly", )
			book_db = conn_book_db.cursor()

			book_id_input = request.form.get('insert_book_id')
			book_name_input = request.form.get('insert_book_name')

			book_db.execute("SELECT book_id,book_name FROM booklist WHERE book_id='{book_id_input}'".format(book_id_input=book_id_input, ))
			select_book = book_db.fetchone()

			if (select_book==None):
				book_db.execute("INSERT INTO booklist (book_id,book_name,if_borrow) VALUES ('{book_id_input}','{book_name_input}','未借出')".format(book_id_input=book_id_input, book_name_input=book_name_input, ))
				conn_book_db.commit()

				book_db.execute("SELECT * FROM booklist WHERE book_id='{book_id_input}'".format(book_id_input=book_id_input, ))
				print_insert_book = book_db.fetchone()
				back_home = '使用者'
				return render_template('insert_book_success.html',print_insert_book=print_insert_book, account=account, password=password, back_home=back_home, )

			elif (select_book[1]!=''):
				error = '{book_id_input}已有書名'.format(book_id_input=book_id_input)
				insert_book_again = url_for('insert_book_again',error=error, account=account, password=password, )
				return redirect(insert_book_again)

			else:
				book_db.execute("UPDATE booklist SET book_name='{book_name_input}', if_borrow='未借出'".format(book_name_input=book_name_input, ))
				conn_book_db.commit()
				book_db.execute("SELECT * FROM booklist WHERE book_id='{book_id_input}'".format(book_id_input=book_id_input, ))
				print_insert_book = book_db.fetchone()

				book_db.close()
				conn_book_db.close()
				back_home = '使用者'
				return render_template('insert_book_success.html', print_insert_book=print_insert_book, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


#----------------------------------------------------------------------------------
#Manager People And Delete People

@app.route('/manager_people/choose/<account>/<password>')
def people_choose(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			back_home = '管理者'
			return render_template('people_choose.html', account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			back_home = '使用者'
			return render_template('people_choose.html', account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


class DeletePeo_Search_Form(FlaskForm):
	key_word = StringField('關鍵字',validators=[DataRequired()])

@app.route('/delete_peo/search/<account>/<password>', methods = ['GET', 'POST'])
def delete_peo_search(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			form = DeletePeo_Search_Form()
			back_home = '管理者'
			return render_template('delete_peo_search.html', form=form, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			form = DeletePeo_Search_Form()
			back_home = '使用者'
			return render_template('delete_peo_search.html', form=form, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)



class DeletePeo_Input_Form(FlaskForm):
	peo_id_input = StringField('成員編碼', validators=[DataRequired()])

@app.route('/delete_peo/input/<account>/<password>', methods = ['GET', 'POST'])
def delete_peo_input(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", )
			peo_db = conn_peo_db.cursor()

			key_word = request.form.get('key_word')

			peo_db.execute(
				"SELECT people_id, people_status,"
				"people_class, people_number, people_name "
				"FROM peoplelist "
				"WHERE people_name LIKE '%{keyword}%' "
				"OR people_id LIKE '%{keyword}%'".format(keyword=key_word, ))

			search_peo = peo_db.fetchall()

			if (search_peo==[]):
				error = "我們找不到{key_word}".format(key_word=key_word)
				form = DeletePeo_Search_Form()
				back_home = '管理者'
				return render_template('delete_peo_search.html', form=form, error=error, account=account, password=password, back_home=back_home, )

			else:
				form = DeletePeo_Input_Form()
				back_home = '管理者'
				return render_template('delete_peo_input.html', form=form, search_peo=search_peo, key_word=key_word, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", )
			peo_db = conn_peo_db.cursor()

			key_word = request.form.get('key_word')

			peo_db.execute(
				"SELECT people_id, people_status,"
				"people_class, people_number, people_name "
				"FROM peoplelist "
				"WHERE people_name LIKE '%{keyword}%' "
				"OR people_id LIKE '%{keyword}%'".format(keyword=key_word, ))

			search_peo = peo_db.fetchall()

			if (search_peo==[]):
				error = "我們找不到{key_word}".format(key_word=key_word)
				form = DeletePeo_Search_Form()
				back_home = '使用者'
				return render_template('delete_peo_search.html', form=form, error=error, account=account, password=password, back_home=back_home, )

			else:
				form = DeletePeo_Input_Form()
				back_home = '使用者'
				return render_template('delete_peo_input.html', form=form, search_book=search_peo, key_word=key_word, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)



@app.route('/delete_peo/sure/<account>/<password>/<key_word>', methods = ['GET', 'POST'])
def delete_peo_sure(account,password,key_word):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", )
			peo_db = conn_peo_db.cursor()

			peo_id_input = request.form.get('peo_id_input')

			peo_db.execute("SELECT * FROM peoplelist WHERE people_id='{peo_id_input}'".format(peo_id_input=peo_id_input))
			select_delete_peo = peo_db.fetchone()

			peo_db.execute(
				"SELECT people_id, people_status, people_class, "
				"people_number, people_name "
				"FROM peoplelist "
				"WHERE people_name LIKE '%{keyword}%' "
				"OR people_id LIKE '%{keyword}%'".format(keyword=key_word, ))
			search_peo = peo_db.fetchall()

			if (select_delete_peo==None):
				form = DeletePeo_Input_Form()
				back_home = '管理者'
				return render_template('delete_peo_input.html', form=form, search_peo=search_peo, account=account, password=password, back_home=back_home, )

			else:
				select_peo_id = select_delete_peo[1]
				back_home = '管理者'
				return render_template('delete_peo_sure.html', select_delete_peo=select_delete_peo, select_peo_id=select_peo_id, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", )
			peo_db = conn_peo_db.cursor()

			peo_id_input = request.form.get('peo_id_input')

			peo_db.execute("SELECT * FROM peoplelist WHERE people_id='{peo_id_input}'".format(peo_id_input=peo_id_input))
			select_delete_peo = peo_db.fetchone()

			peo_db.execute(
				"SELECT people_id, people_status, people_class, "
				"people_number, people_name "
				"FROM peoplelist "
				"WHERE people_name LIKE '%{keyword}%' "
				"OR people_id LIKE '%{keyword}%'".format(keyword=key_word, ))
			search_peo = peo_db.fetchall()

			if (select_delete_peo==None):
				form = DeletePeo_Input_Form()
				back_home = '使用者'
				return render_template('delete_peo_input.html', form=form, search_peo=search_peo, account=account, password=password, back_home=back_home, )

			else:
				select_peo_id = select_delete_peo[1]
				back_home = '使用者'
				return render_template('delete_peo_sure.html', select_delete_peo=select_delete_peo, select_peo_id=select_peo_id, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)



@app.route('/delete_peo/solution/<account>/<password>/<select_peo_id>', methods = ['GET', 'POST'])
def delete_peo_solution(account,password,select_peo_id):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", )
			peo_db = conn_peo_db.cursor()

			peo_db.execute("SELECT * FROM peoplelist WHERE people_id='{select_peo_id}'".format(select_peo_id=select_peo_id, ))
			select_peo = peo_db.fetchone()

			peo_db.execute("UPDATE peoplelist " 
				"SET people_status=Null,"
				"people_class=Null, people_number=Null, people_name=Null "
				"WHERE people_id='{select_peo_id}'".format(select_peo_id=select_peo_id, ))
			conn_peo_db.commit()
			back_home = '管理者'
			return render_template('delete_peo_success.html', select_peo=select_peo, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", )
			peo_db = conn_peo_db.cursor()

			peo_db.execute("SELECT * FROM peoplelist WHERE peo_id='{select_peo_id}'".format(select_peo_id=select_peo_id, ))
			select_peo = peo_db.fetchone()

			peo_db.execute("UPDATE peoplelist " 
				"SET people_status=Null,"
				"people_class=Null, people_number=Null, people_name=Null "
				"WHERE people_id='{select_peo_id}'".format(select_peo_id=select_peo_id, ))
			conn_peo_db.commit()
			back_home = '使用者'
			return render_template('delete_peo_success.html', select_peo=select_peo, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)



#--------------------------------------------------------------------------------------
#Insert People

class InsertPeoForm(FlaskForm):
	insert_peo_id = StringField('成員編碼：', description=['編碼必須是五碼數字'],validators=[DataRequired()])
	insert_peo_status = SelectField('成員身份：', choices=[('老師', '老師'),('學生', '學生'),('家長', '家長'),])
	insert_peo_class = StringField('成員班級：', validators=[DataRequired()])
	insert_peo_number = StringField('班級座號：', validators=[DataRequired()])
	insert_peo_name = StringField('成員姓名：',validators=[DataRequired()])


@app.route('/insert_peo/input/<account>/<password>', methods = ['GET', 'POST'])
def insert_peo_input(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", )
			peo_db = conn_peo_db.cursor()

			peo_db.execute("SELECT people_id FROM peoplelist WHERE people_name IS NULL")
			empty_peo_id = peo_db.fetchall() #顯示空的book_id給使用者看

			peo_db.execute("SELECT id,people_id FROM peoplelist ORDER BY id DESC LIMIT 1")
			max_peo_id = peo_db.fetchone() #顯示最大值的book_id給使用者看

			form = InsertPeoForm()
			back_home = '管理者'
			return render_template('insert_peo_input.html', form=form, empty_peo_id=empty_peo_id, max_peo_id=max_peo_id, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", )
			peo_db = conn_peo_db.cursor()

			peo_db.execute("SELECT people_id FROM peoplelist WHERE people_name IS NULL")
			empty_peo_id = peo_db.fetchall() #顯示空的book_id給使用者看

			peo_db.execute("SELECT id,people_id FROM peoplelist ORDER BY id DESC LIMIT 1")
			max_peo_id = peo_db.fetchone() #顯示最大值的book_id給使用者看

			form = InsertPeoForm()
			back_home = '使用者'
			return render_template('insert_peo_input.html', form=form, empty_peo_id=empty_peo_id, max_peo_id=max_peo_id, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


@app.route('/insert_peo/again/<account>/<password>/<error>', methods = ['GET', 'POST'])
def insert_peo_again(account,password,error):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", )
			peo_db = conn_peo_db.cursor()

			peo_db.execute("SELECT people_id FROM peoplelist WHERE people_name IS NULL")
			empty_peo_id = peo_db.fetchall() #顯示空的book_id給使用者看

			peo_db.execute("SELECT id,people_id FROM peoplelist ORDER BY id DESC LIMIT 1")
			max_peo_id = peo_db.fetchone() #顯示最大值的book_id給使用者看

			form = InsertPeoForm()
			back_home = '管理者'
			return render_template('insert_peo_input.html', form=form, empty_peo_id=empty_peo_id, max_peo_id=max_peo_id, error=error, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", )
			peo_db = conn_peo_db.cursor()

			peo_db.execute("SELECT people_id FROM peoplelist WHERE people_name IS NULL")
			empty_peo_id = peo_db.fetchall() #顯示空的book_id給使用者看

			peo_db.execute("SELECT id,people_id FROM peoplelist ORDER BY id DESC LIMIT 1")
			max_peo_id = peo_db.fetchone() #顯示最大值的book_id給使用者看

			form = InsertPeoForm()
			back_home = '使用者'
			return render_template('insert_peo_input.html', form=form, empty_peo_id=empty_peo_id, max_peo_id=max_peo_id, error=error, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)



@app.route('/insert_peo/solution/<account>/<password>', methods = ['GET', 'POST'])
def insert_peo_solution(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", )
			peo_db = conn_peo_db.cursor()

			peo_id_input = request.form.get('insert_peo_id')
			peo_sta_input = request.form.get('insert_peo_status')
			peo_cla_input = request.form.get('insert_peo_class')
			peo_num_input = request.form.get('insert_peo_number')
			peo_name_input = request.form.get('insert_peo_name')

			peo_db.execute("SELECT people_id,people_name FROM peoplelist WHERE people_id='{peo_id_input}'".format(peo_id_input=peo_id_input, ))
			select_peo = peo_db.fetchone()

			id_is_number = str.isdigit(peo_id_input)

			if (len(peo_id_input)!=5 or id_is_number!=1):
				error = '成員編碼輸入錯誤！成員編碼需為5碼數字'.format(peo_id_input=peo_id_input)
				insert_peo_again = url_for('insert_peo_again',error=error, account=account, password=password, )
				return redirect(insert_peo_again)

			elif (select_peo==None):
				peo_db.execute("INSERT INTO peoplelist (people_id,people_status,people_class,people_number,people_name) VALUES ('{peo_id_input}','{peo_sta_input}','{peo_cla_input}','{peo_num_input}','{peo_name_input}')".format(peo_id_input=peo_id_input, peo_sta_input=peo_sta_input, peo_cla_input=peo_cla_input, peo_num_input=peo_num_input, peo_name_input=peo_name_input, ))
				conn_peo_db.commit()

				peo_db.execute("SELECT * FROM peoplelist WHERE people_id='{peo_id_input}'".format(peo_id_input=peo_id_input, ))
				print_insert_peo = peo_db.fetchone()
				back_home = '管理者'
				return render_template('insert_peo_success.html',print_insert_peo=print_insert_peo, account=account, password=password, back_home=back_home, )

			elif (select_peo[1]!=None):
				error = '{peo_id_input}已有成員'.format(peo_id_input=peo_id_input)
				insert_peo_again = url_for('insert_peo_again',error=error, account=account, password=password, )
				return redirect(insert_peo_again)

			else:
				peo_db.execute("UPDATE peoplelist SET people_status='{peo_sta}', people_class='{peo_cla}', people_number='{peo_num}', people_name='{peo_name}' WHERE people_id='{peo_id_input}'".format(peo_sta=peo_sta_input, peo_cla=peo_cla_input, peo_num=peo_num_input, peo_name=peo_name_input, peo_id_input=peo_id_input, ))
				conn_peo_db.commit()

				peo_db.execute("SELECT * FROM peoplelist WHERE people_id='{peo_id_input}'".format(peo_id_input=peo_id_input, ))
				print_insert_peo = peo_db.fetchone()

				peo_db.close()
				conn_peo_db.close()
				back_home = '管理者'
				return render_template('insert_peo_success.html', print_insert_peo=print_insert_peo, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", )
			peo_db = conn_peo_db.cursor()

			peo_id_input = request.form.get('insert_peo_id')
			peo_sta_input = request.form.get('insert_peo_status')
			peo_cla_input = request.form.get('insert_peo_class')
			peo_num_input = request.form.get('insert_peo_number')
			peo_name_input = request.form.get('insert_peo_name')

			peo_db.execute("SELECT people_id,people_name FROM peoplelist WHERE people_id='{peo_id_input}'".format(peo_id_input=peo_id_input, ))
			select_peo = peo_db.fetchone()

			if (select_peo==None):
				peo_db.execute("INSERT INTO peoplelist (people_id,people_status,people_class,people_number,people_name) VALUES ('{peo_id_input}','{peo_sta_input}','{peo_cla_input}','{peo_num_input}','{peo_name_input}')".format(peo_id_input=peo_id_input, peo_sta_input=peo_sta_input, peo_cla_input=peo_cla_input, peo_num_input=peo_num_input, peo_name_input=peo_name_input, ))
				conn_peo_db.commit()

				peo_db.execute("SELECT * FROM peoplelist WHERE people_id='{peo_id_input}'".format(peo_id_input=peo_id_input, ))
				print_insert_peo = peo_db.fetchone()
				back_home = '使用者'
				return render_template('insert_peo_success.html',print_insert_peo=print_insert_peo, account=account, password=password, back_home=back_home, )

			elif (select_peo[1]!=''):
				error = '{peo_id_input}已有書名'.format(peo_id_input=peo_id_input)
				insert_peo_again = url_for('insert_peo_again',error=error, account=account, password=password, )
				return redirect(insert_peo_again)

			else:
				peo_db.execute("UPDATE peoplelist SET people_status='{peo_sta}', people_class='{peo_cla}', people_number='{peo_num}', people_name='{peo_name}' WHERE people_id='{peo_id_input}'".format(peo_sta=peo_sta_input, peo_cla=peo_cla_input, peo_num=peo_num_input, peo_name=peo_name_input, peo_id_input=peo_id_input, ))
				conn_peo_db.commit()

				peo_db.execute("SELECT * FROM peoplelist WHERE people_id='{peo_id_input}'".format(peo_id_input=peo_id_input, ))
				print_insert_peo = peo_db.fetchone()

				peo_db.close()
				conn_peo_db.close()
				back_home = '使用者'
				return render_template('insert_peo_success.html', print_insert_peo=print_insert_peo, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)



#-----------------------------------------------------------------------------------------
#成員搜尋

class Search_Peo_Form(FlaskForm):
	peo_key_word = StringField('成員關鍵字：',description=['可輸入想查詢的成員姓名、編碼、班級、座號、身份等關鍵字'], validators=[DataRequired()])

@app.route('/people_search/<account>/<password>', methods = ['GET', 'POST'])
def people_search(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			form = Search_Peo_Form()
			back_home = '管理者'
			return render_template('peo_search_input.html', form=form, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			form = Search_Peo_Form()
			back_home = '使用者'
			return render_template('peo_search_input.html', form=form, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


@app.route('/people_search/all/<account>/<password>', methods = ['GET', 'POST'])
def peo_search_all(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			peo_db = conn_peo_db.cursor()

			peo_db.execute("SELECT * FROM peoplelist")
			peo_search_all = peo_db.fetchall()

			conn_peo_db.close()
			back_home = '管理者'
			return render_template('peo_detail.html', account=account, password=password, peo_search_all=peo_search_all, back_home=back_home, )

		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			peo_db = conn_peo_db.cursor()

			book_db.execute("SELECT * FROM peoplelist")
			peo_search_all = book_db.fetchall()
			conn_peo_db.close()
			back_home = '使用者'
			return render_template('peo_detail.html', account=account, password=password, peo_search_all=peo_search_all, back_home=back_home, )
			
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


@app.route('/people_search/solution/<account>/<password>', methods = ['GET', 'POST'])
def peo_search_solution(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			peo_db = conn_peo_db.cursor()

			peo_key_word = request.form.get('peo_key_word')

			peo_db.execute("SELECT * FROM peoplelist WHERE "
				"people_id LIKE '%{peo_key_word}%' OR people_status LIKE '%{peo_key_word}%' OR "
				"people_class LIKE '%{peo_key_word}%' OR people_number LIKE '%{peo_key_word}%' OR "
				"people_name LIKE'%{peo_key_word}%'".format(peo_key_word=peo_key_word))
			peo_search_all = peo_db.fetchall()
			if (peo_search_all==[]):
				error = '我們找不到{peo_key_word}'.format(peo_key_word=peo_key_word, )
				form = Search_Peo_Form()
				back_home = '管理者'
				return render_template('peo_search_input.html', form=form, account=account, password=password, error=error, back_home=back_home, )
			else:
				back_home = '管理者'
				return render_template('peo_detail.html', peo_search_all=peo_search_all, account=account, password=password, back_home=back_home, )

		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_peo_db = psycopg2.connect(database="peoplelist", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			peo_db = conn_peo_db.cursor()

			peo_key_word = request.form.get('peo_key_word')

			peo_db.execute("SELECT * FROM peoplelist WHERE "
				"people_id LIKE '%{peo_key_word}%' OR people_status LIKE '%{peo_key_word}%' OR "
				"people_class LIKE '%{peo_key_word}%' OR people_number LIKE '%{peo_key_word}%' OR "
				"people_name LIKE'%{peo_key_word}%'")
			peo_search_all = peo_db.fetchall()
			if (peo_search_all==[]):
				error = '我們找不到{peo_key_word}'.format(peo_key_word=peo_key_word, )
				form = Search_Peo_Form()
				back_home = '使用者'
				return render_template('peo_search_input.html', form=form, account=account, password=password, error=error, back_home=back_home, )
			else:
				back_home = '使用者'
				return render_template('peo_detail.html', peo_search_all=peo_search_all, account=account, password=password, back_home=back_home, )

		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


#-----------------------------------------------------------------------------------
#歷史紀錄


class HistoryForm(FlaskForm):
	peo_cla_input = StringField('班級', validators=[DataRequired()])
	peo_name_input = StringField('姓名', validators=[DataRequired()])
	peo_id_input = StringField('成員編碼', validators=[DataRequired()])

@app.route('/history_input/<account>/<password>', methods = ['GET', 'POST'])
def history_input(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			form = HistoryForm()
			back_home = '管理者'
			return render_template('history_input.html', form=form, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			form = HistoryForm()
			back_home = '使用者'
			return render_template('history_input.html', form=form, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


@app.route('/history_soultion/<account>/<password>', methods = ['GET', 'POST'])
def history_solution(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			conn_history_db = psycopg2.connect(database="history", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			history_db = conn_history_db.cursor()

			peo_cla_input = request.form.get('peo_cla_input')
			peo_name_input = request.form.get('peo_name_input')
			peo_id_input = request.form.get('peo_id_input')

			history_db.execute("SELECT * FROM history WHERE people_class='{peo_cla}' AND people_name='{peo_name}' AND people_id='{peo_id}' AND if_borrow='借出'".format(peo_cla=peo_cla_input, peo_name=peo_name_input, peo_id=peo_id_input))
			select_history = history_db.fetchall()

			if (select_history==[]):
				error = '我們找不到班級為{peo_cla}、姓名為{peo_name}、成員編碼為{peo_id}都符何的歷史紀錄。'.format(peo_cla=peo_cla_input, peo_name=peo_name_input, peo_id=peo_id_input, )
				form = HistoryForm()
				back_home = '管理者'
				return render_template('history_input.html', form=form, account=account, password=password, error=error, back_home=back_home, )
			else:
				back_home = '管理者'
				return render_template('history_solution.html', select_history=select_history, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	elif (account==user_account):
		check_user = check_password_hash(password,user_password)
		if (check_user==1):
			conn_history_db = psycopg2.connect(database="history", user="stella", password="Janeslowly", host="127.0.0.1", port="5432")
			history_db = conn_history_db.cursor()

			peo_cla_input = request.form.get('peo_cla_input')
			peo_name_input = request.form.get('peo_name_input')
			peo_id_input = request.form.get('peo_id_input')

			history_db.execute("SELECT * FROM history WHERE people_class='{peo_cla}' AND people_name='{peo_name}' AND people_id='{peo_id}' AND if_borrow='借出'".format(peo_cla=peo_cla_input, peo_name=peo_name_input, peo_id=peo_id_input))
			select_history = history_db.fetchall()

			if (select_history==[]):
				error = '我們找不到班級為{peo_cla}、姓名為{peo_name}、成員編碼為{peo_id}都符何的歷史紀錄。'.format(peo_cla=peo_cla_input, peo_name=peo_name_input, peo_id=peo_id_input, )
				form = HistoryForm()
				back_home = '使用者'
				return render_template('history_input.html', form=form, account=account, password=password, error=error, back_home=back_home, )
			else:
				back_home = '使用者'
				return render_template('history_solution.html', select_history=select_history, account=account, password=password, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


#-------------------------------------------------------------------------------
#帳號管理（更改密碼或信箱）


class ChangeForm(FlaskForm):
	change_account = StringField('輸入您的帳號：',validators=[DataRequired()])

@app.route('/manager_change/input/<account>/<password>', methods = ['GET', 'POST'])
def manager_change_input(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			form = ChangeForm()
			back_home = '管理者'
			return render_template('change_account_input.html', form=form, account=account, password=password, back_home=back_home,)
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)
	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)



@app.route('/manager_change/choose/<account>/<password>', methods = ['GET', 'POST'])
def manager_change_choose(account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			change_account = request.form.get('change_account')


			login_db.execute("SELECT * FROM loginlist WHERE account='{change_account}'".format(change_account=change_account, ))
			select_account = login_db.fetchall()

			if (select_account==[]):
				error = '我們找不到{change_account}這個帳號'.format(change_account=change_account, )
				form = ChangeForm()
				back_home = '管理者'
				return render_template('change_account_input.html', form=form, account=account, password=password, error=error, back_home=back_home, )
			else:
				back_home = '管理者'
				return render_template('change_choose.html',account=account,password=password, change_account=change_account, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)
	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)



class PasswordForm(FlaskForm):
	oringin_password = PasswordField('原密碼',validators=[DataRequired()])
	new_password = PasswordField('新的密碼',validators=[DataRequired()])
	new_password_again = PasswordField('再輸入一次',validators=[DataRequired()])


@app.route('/manager_change/password/<account>/<password>/<change_account>', methods = ['GET', 'POST'])
def manager_change_password(account,password, change_account):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			#change_account = request.form.get('change_account')

			form = PasswordForm()
			back_home = '管理者'
			return render_template('change_password_input.html', form=form, account=account, password=password, change_account=change_account, back_home=back_home, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)
	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)





@app.route('/manager_change/solution/<account>/<password>/<change_account>', methods = ['GET', 'POST'])
def manager_change_solution(change_account,account,password):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			new_password = request.form.get('new_password')
			new_password_again = request.form.get('new_password_again')
			oringin_password = request.form.get('oringin_password')

			login_db.execute("SELECT * FROM loginlist WHERE password='{oringin_password}'".format(oringin_password=oringin_password, ))
			check_password = login_db.fetchall()

			if (new_password!=new_password_again ):
				error = '兩個密碼輸入不同！'
				form = PasswordForm()
				back_home = '管理者'
				return render_template('change_password_input.html', form=form, account=account, password=password, change_account=change_account, error=error, back_home=back_home, )
			elif (check_password==[]):
				error = '原密碼輸入錯誤！'
				form = PasswordForm()
				back_home = '管理者'
				return render_template('change_password_input.html', form=form, account=account, password=password, change_account=change_account, error=error, back_home=back_home,)
			else:
				login_db.execute("UPDATE loginlist SET password='{new_password}' WHERE account='{change_account}'".format(new_password=new_password, change_account=change_account, ))
				conn_login_db.commit()
				back_home = '管理者'
				return render_template('change_success.html', account=account, password=password, change_account=change_account, back_home=back_home, )

		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)
	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)
















class EmailInputForm(FlaskForm):
	the_password = PasswordField('請輸入密碼：',validators=[DataRequired()])
	new_email = StringField('新的信箱：',validators=[DataRequired()])
	new_email_again = StringField('再輸入一次新的信箱：',validators=[DataRequired()])


@app.route('/change/email/input/<account>/<password>/<change_account>', methods = ['GET', 'POST'])
def change_email_input(account,password,change_account):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			form = EmailInputForm()
			back_home = '管理者'
			return render_template('change_email_input.html', form=form, account=account, password=password, back_home=back_home, change_account=change_account, )
		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)


@app.route('/change/email/solution/<account>/<password>/<change_account>', methods = ['GET', 'POST'])
def change_email_solution(account,password,change_account):
	conn_login_db = psycopg2.connect(database="login", user="stella", password="Janeslowly", )
	login_db = conn_login_db.cursor()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='1' ")
	manager_detail = login_db.fetchone()

	login_db.execute("SELECT account, password FROM loginlist WHERE id='2' ")
	user_detail = login_db.fetchone()

	manager_account = manager_detail[0]
	manager_password = manager_detail[1]

	user_account = user_detail[0]
	user_password = user_detail[1]

	if (account==manager_account):
		check_manager = check_password_hash(password,manager_password)
		if (check_manager==1):
			the_password = request.form.get('the_password')
			new_email = request.form.get('new_email')
			new_email_again = request.form.get('new_email_again')

			login_db.execute("SELECT password FROM loginlist WHERE account='{change_account}'".format(change_account=change_account, ))
			ture_password = login_db.fetchone()

			if (new_email!=new_email_again):
				error = '兩次信箱輸入不一致！'
				form = EmailInputForm()
				back_home = '管理者'
				return render_template('change_email_input.html', form=form, account=account, password=password, error=error, back_home=back_home, change_account=change_account, )
			elif (the_password!=ture_password[0]):
				error = '密碼輸入不正確！'
				form = EmailInputForm()
				back_home = '管理者'
				return render_template('change_email_input.html', form=form, account=account, password=password, error=error, back_home=back_home, change_account=change_account, )
			else:
				login_db.execute("UPDATE loginlist SET email='{new_email}'".format(new_email=new_email, ))
				conn_login_db.commit()

				login_db.execute("SELECT email FROM loginlist WHERE account='{change_account}'".format(change_account=change_account, ))
				select_send_mail = login_db.fetchone()
				send_mail = select_send_mail[0]

				msg = Message('更改信箱成功！', sender='chatbot520@gmail.com', recipients=[send_mail])
				msg.html = render_template('mail_change_body.html' )
				mail.send(msg)
				return render_template('mail_change_success.html', account=account, password=password, send_mail=send_mail, change_account=change_account, )

		else:
			back_to_library_home = url_for('library')
			return redirect(back_to_library_home)

	else:
		back_to_library_home = url_for('library')
		return redirect(back_to_library_home)














if __name__ == "__main__":
    app.run(debug=True)


