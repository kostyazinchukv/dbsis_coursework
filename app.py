from flask import Flask,render_template,redirect,url_for,request, session, g
from config import Config
import smtplib
import psycopg2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from python.connection_BD import registration,login_user,get_customer_info,get_contract_by_cust,create_contract

app = Flask(__name__)


app.config.from_object(Config)
# app.secret_key = 'Heil_Adolf_Hitler'


@app.before_request
def before_request():
   g.user_id = None
   g.nickname = None
   if ('user_id' in session) and ('nickname' in session):
      g.user_id = session['user_id']
      g.nickname = session['nickname']

@app.route('/')
def red():
   return redirect(url_for('mainpage'))


@app.route('/mainpage', methods=['GET', 'POST'])
def mainpage():
    return render_template('mainpage.html')


@app.route('/cases')
def cases():
    return render_template('insurance_case.html')


@app.route('/send_polis')
def send_polis():
   print(session['email_user'])
   print(session['contract_text'])
   send_email(session['email_user'],text = session['contract_text'])
   session.pop('email_user',None)
   session.pop('contract_text', None)

   price1 = session['price']
   area1 = session['area']

   session.pop('price',None)
   session.pop('area', None)

   return render_template('payment.html', price=price1, area=area1)

@app.route('/payment')
def payment():

   end_price = session['real_price']

   text = f"""
   
      Dear Customer,

      Please, make a payment of {end_price} uah to our requisites:
      Card number: 1488 1488 1488 1488. Holder: Cum Dick Dickovich 

      With kind regards,
      CumDickCompany   
   
   """

   send_email(session['email_user'],text)

   return render_template('payment_health.html', price=session['real_price'])

@app.route('/send_polis_health')
def send_polis_health():

   send_email(session['email_user'],text = session['contract_text'])
   #session.pop('email_user',None)
   #session.pop('contract_text', None)
   price1 = session['real_price']
   #session.pop('real_price',None)

   return render_template('payment_health.html', price=price1)

@app.route('/asswecan/<price>', methods=['GET', 'POST'])
def form_health(price):
   if g.user_id == None:
      print('Спершу увійдіть') #TODO Message Flashing
      return redirect(url_for('login'))
   if request.method == 'GET':
      return render_template('insurance_health_form.html', price=price)
   else:
      connection = psycopg2.connect(
         app.config['SQLALCHEMY_DATABASE_URI']
         )
      connection.autocommit = True

      session['price'] = request.form['tariff']

      session['email_user'] = request.form['email']



      if session['price'] == 'beginner':
         real_price = 34
      elif session['price'] == 'plusplus':
         real_price = 45
      elif session['price'] == 'pro':
         real_price = 60
      else:
         raise Exception

      session['real_price'] = real_price

      second_name = request.form['second_name']
      first_name = request.form['first_name']
      third_name_kekw = request.form['third_name_kekw']

      city = request.form['city']
      town = request.form['town']
      street = request.form['street']
      session['birthday'] = request.form['birthday']


      session['contract_text'] = f"""
      Dear {second_name} {first_name} {third_name_kekw},

      This e-mail is generated automatically and is sent to inform you about the terms of 
      your {session['price']}-level insurance agreement. Those are the following:
      The insurance covers health and life of our customer {second_name} {first_name} {third_name_kekw} born on {session['birthday']}, 
      who lives in {city},{town},{street};
      Insurance`s price will be {real_price} uah a day;

      With kind regards,
      CumDickCompany
      """
      create_contract(g.user_id, 'Life '+price, str(real_price), '2022-10-10', connection) # TODO Пофіксити на нормальну дату
      connection.close()

      return render_template('payment_health.html', price=real_price)


@app.route('/new_contract/<price>', methods=['GET', 'POST'])
def new_contract(price):
   if g.user_id == None:
      print('Спершу увійдіть') #TODO Message Flashing
      return redirect(url_for('login'))
   if request.method == 'GET':
      return render_template('flat_form.html', price=price)
   else:
      connection = psycopg2.connect(
         app.config['SQLALCHEMY_DATABASE_URI']
         )
      connection.autocommit = True

      session['area'] = int(request.form['area'])
      session['price'] = request.form['tarif']

      session['email_user'] = request.form['email']


      if session['price'] == 'beginner':
         real_price = int(session['area']) * 1.2
      elif session['price'] == 'plusplus':
         real_price = int(session['area']) * 1.5
      elif session['price'] == 'pro':
         real_price = int(session['area']) * 2
      else:
         raise Exception

      session['real_price'] = real_price

      second_name = request.form['second_name']
      first_name = request.form['first_name']
      third_name_kekw = request.form['third_name_kekw']

      city = request.form['city']
      town = request.form['town']
      street = request.form['street']

      session['contract_text'] = f"""
      Dear {second_name} {first_name} {third_name_kekw},

      This e-mail is generated automatically and is sent to inform you about the terms of
      your {session['price']}-level insurance agreement. Those are the following:
      The insurance covers an {session['area']}-sq.m. household, situated at
      {city},{town},{street}
      It`s price will be {real_price} uah a day;

      With kind regards,
      CumDickCompany
      """
      create_contract(g.user_id, 'Household '+price, str(real_price), '2022-10-10', connection) # TODO Пофіксити на нормальну дату
      connection.close()

      return render_template('payment.html', price=session['price'], area=session['area'])


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/my_cabinet')
def my_cabinet():
   connection = psycopg2.connect(
      app.config['SQLALCHEMY_DATABASE_URI']
      )
   connection.autocommit = True

   (customer_id, full_name, age, email, passw, login, bank) = get_customer_info(g.user_id,connection)[0][1:-1].split(',')

   contracts = get_contract_by_cust(customer_id, connection)
   connection.close()

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
   return render_template('profile_page.html', full_name = full_name, age = age, email=email,ins_types = ins_types, ins_exps = ins_exps)


def send_email(email, text = 'Tut bude infa pro polis (sorry, ne vstyg zapility)'):
   msg = MIMEMultipart()
   msg['From'] = 'CumDickCompany'
   msg['To'] = str(email)
   msg['Subject'] = 'Insurance'

   msg.attach(MIMEText(text, 'plain'))

   text = msg.as_string()

   server = smtplib.SMTP("smtp.gmail.com", 587)
   server.starttls()
   server.login("cumdickcompany@gmail.com", "DickCumDick")
   server.sendmail("cumdickcompany@gmail.com", email, text)
   return render_template('mainpage.html')






@app.route('/login', methods=['GET', 'POST'])
def login():
   if request.method == 'GET':
      return render_template('sign_in.html')

   elif request.method == 'POST':
      session.pop('user_id', None)
      session.pop('nickname', None)

      connection = psycopg2.connect(
         app.config['SQLALCHEMY_DATABASE_URI']
         )
      connection.autocommit = True

      login_name = request.form['login']
      password = request.form['pass']

      exit_code = login_user(login_name, password, connection)
      connection.close()

      if exit_code != -1:
         session['user_id'] = exit_code
         session['nickname'] = login_name

         print('Успішно авторизовано')  # TODO Message Flashing
         return redirect(url_for("mainpage"))
      else:
         print('Користувача з таким логіном і паролем не знайдено') #TODO Message Flashing
         return render_template('sign_in.html')


@app.route('/register', methods = ['GET', 'POST'])
def register():
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
         return render_template('mainpage.html')
      else:
         connection.close()
         #print(status)
         return render_template('registration.html')
   if request.method == 'GET' and g.user_id == None:
      return render_template('registration.html')
   else:
      redirect(url_for('mainpage'))



@app.route('/logout')
def logout():
   session.pop('user_id', None)
   session.pop('nickname', None)
   g.nickname = None
   g.user_id = None
   return render_template('mainpage.html')


if __name__ == '__main__':
   app.run(debug=True)
