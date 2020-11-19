from flask import Flask,render_template,redirect,url_for,request
#from datetime import date
from config import Config

import smtplib
import psycopg2
from python.connection_BD import registration,login_user,get_customer_info,get_contract_by_cust,create_contract

app = Flask(__name__)

app.config.from_object(Config)


nickname = None
user_id = None


@app.route('/')
def red():
   return redirect(url_for('mainpage'))


@app.route('/mainpage', methods=['GET', 'POST'])
def mainpage():
    global nickname
    return render_template('mainpage.html', name_c=nickname)


@app.route('/cases')
def cases():
    global nickname
    return render_template('insurance_case.html', name_c=nickname)


@app.route('/new_contract/<price>', methods=['GET', 'POST'])
def new_contract(price):
   global nickname
   global user_id

   if request.method == 'GET' or user_id == None:
      return render_template('flat_form.html', name_c=nickname, price=price)
   else:
      connection = psycopg2.connect(
         app.config['SQLALCHEMY_DATABASE_URI']
         )
      connection.autocommit = True

      area = int(request.form['area'])
      price = request.form['tarif']
      email_user = request.form['email']
      print(price)

      if price == 'beginner':
         real_price = int(area) * 1.2
      elif price == 'plusplus':
         real_price = int(area) * 1.5
      elif price == 'pro':
         real_price = int(area) * 2
      else:
         raise Exception

      create_contract(user_id, price, real_price, '2022-10-10', connection) # TODO Пофіксити на нормальну дату
      send_email(email_user)
      return render_template('payment.html', name_c=nickname, price=price, area=area)


@app.route('/contact')
def contact():
    global nickname
    return render_template('contact.html', name_c=nickname)


@app.route('/my_cabinet')
def my_cabinet():
   connection = psycopg2.connect(
      app.config['SQLALCHEMY_DATABASE_URI']
      )
   connection.autocommit = True
   global nickname
   (customer_id, full_name, age, email, passw, login, bank) = get_customer_info(user_id,connection)[0][1:-1].split(',')

   contracts = get_contract_by_cust(customer_id, connection)
   print(contracts)
   ins_types = []
   ins_exps = []
   if contracts[0] != None:
      for tup in contracts:
         real_tup =tup[1:-1].split(',')
         print(real_tup)
         ins_types.append(real_tup[3])
         ins_exps.append(real_tup[5])
   else:
      ins_types = ['Незадано']
      ins_exps = ['Незадано']
   return render_template('profile_page.html', name_c=nickname, full_name = full_name, age = age, email=email,ins_types = ins_types, ins_exps = ins_exps)


#@app.route('/send', methods=['GET','POST'])
def send_email(email):
   global nickname
   if request.method == 'GET':
      return render_template('mainpage.html', name_c=nickname)
   msg = 'Tut bude infa pro polis (sorry, ne vstyg zapility)'
   server = smtplib.SMTP("smtp.gmail.com", 587)
   server.starttls()
   server.login("cumdickcompany@gmail.com", "DickCumDick")
   server.sendmail("cumdickcompany@gmail.com", email, msg)
   return render_template('mainpage.html', name_c =nickname)


@app.route('/asswecan/<price>')
def form_health(price):
    return render_template('insurance_health_form.html', name_c=nickname, price=price)



@app.route('/login', methods=['GET', 'POST'])
def login():

   global user_id
   global nickname
   if request.method == 'GET':
      return render_template('sign_in.html', name_c =nickname)
   elif request.method == 'POST':
      connection = psycopg2.connect(
         app.config['SQLALCHEMY_DATABASE_URI']
         )
      connection.autocommit = True

      login_name = request.form['login']
      password = request.form['pass']

      exit_code = login_user(login_name, password, connection)
      connection.close()

      if exit_code != -1:
         user_id = exit_code
         nickname = login_name
         print(f'Виконано вхід як {nickname}')
         return render_template('mainpage.html', name_c =nickname)
      else:
         print('Користувача з таким логіном і паролем не знайдено')
         return render_template('sign_in.html', name_c =nickname)


@app.route('/register', methods = ['GET', 'POST'])
def register():
   global nickname
   if request.method == 'POST':
      connection = psycopg2.connect(
         app.config['SQLALCHEMY_DATABASE_URI']
         )
      connection.autocommit = True

      name = request.form['name']
      login = request.form['login']
      password1 = request.form['pass1']
      password2 = request.form['pass2']
      email = request.form['email']
      age = 21 # TODO ПОФІКСИТИ !!!!!1!1!!1!
      card = request.form['card']
      if password1 == password2:
         status = registration(login, password1, email, age, name, card,connection)
         print(status)
         connection.close()
         return render_template('mainpage.html', name_c =nickname)
      else:
         connection.close()
         #print(status)
         return render_template('registration.html', name_c =nickname)
   if request.method == 'GET':
      return render_template('registration.html', name_c =nickname)


@app.route('/logout')
def logout():
   global nickname
   global user_id
   nickname = None
   user_id = None
   return render_template('mainpage.html', name_c =nickname)


if __name__ == '__main__':
   app.run(debug=True)

