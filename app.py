from flask import Flask,render_template,redirect,url_for,request, session, g, flash
from config import Config
import smtplib
import psycopg2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from python.connection_BD import registration,login_user,get_customer_info,get_contract_by_cust,create_contract,\
   update_customer,get_customer_by_login,get_customer_i_by_login,update_customer_role,update_payment_status,\
    update_child_payment_status,create_child_contract,get_children_by_login, get_child_contract_by_cust12
import datetime
import hashlib


def to_sha(hash_string):
   sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
   return sha_signature


app = Flask(__name__)


app.config.from_object(Config)
#app.secret_key = 'Heil_Adolf_зшзHitler'


@app.before_request
def before_request():
   g.user_id = None
   g.nickname = None
   g.c_role = None
   g.customer_list = []
   g.admin_name = None
   g.admin_card = None
   g.admin_role = None
   g.childs = []


   if ('user_id' in session) and ('nickname' in session) and ('role' in session):
      g.user_id = session['user_id']
      g.nickname = session['nickname']
      g.c_role = session['role']



@app.route('/')
def red():
   return redirect(url_for('mainpage'))

@app.route('/users/update_role', methods=['POST'])
def update_role():

   connection = psycopg2.connect(
      app.config['SQLALCHEMY_DATABASE_URI']
   )
   connection.autocommit = True

   update_customer_role(session['log'],request.form['radio'],connection)

   connection.close()

   return redirect(url_for('admin_page'))


@app.route('/users/admin_page', methods=['GET', 'POST'])
def admin_page():
   if g.c_role == '"Full Master"' or g.c_role =='"Fucking Slave"':
      if request.method == 'POST':

         connection = psycopg2.connect(
            app.config['SQLALCHEMY_DATABASE_URI']
         )
         connection.autocommit = True

         log = request.form['log']
         session['log'] = log

         g.customer_list = get_customer_by_login(log, connection)

         (g.admin_name, g.admin_card, g.admin_role) = get_customer_i_by_login(session['log'],connection)

         print(g.admin_role)
         if g.admin_role == 'Fucking Slave':
            g.admin_role_user = 'Менеджер'
         elif g.admin_role == 'Full Master':
            g.admin_role_user = 'Адміністратор'
         elif g.admin_role == 'leatherman':
            g.admin_role_user = 'Користувач'

         g.childs = get_children_by_login(session['log'],connection)
         print(g.childs)

      return render_template('users/admin_page.html')

   else:
      flash('Ви не адмін!')
      return redirect(url_for('mainpage'))

@app.route('/mainpage', methods=['GET', 'POST'])
def mainpage():
    return render_template('mainpage.html')


@app.route('/contracts/cases',methods=['GET'])
def cases():
    return render_template('contracts/insurance_case.html')


@app.route('/send_polis')
def send_polis():

   send_email(session['email_user'],text = session['contract_text'])

   return render_template('payment.html', real_price=session['real_price'])

@app.route('/payment') # PUT
def payment():

   text = f"""
   
      Dear Customer,

      Please, make a payment of {session['real_price']} uah to our requisites:
      Card number: 1488 1488 1488 1488. Holder: Cum Dick Dickovich 

      With kind regards,
      CumDickCompany   
   
   """
   send_email(session['email_user'],text)

   if 'is_child' in session:
      update_child_payment_status(session['contract_id'])
   else:
      update_payment_status(session['contract_id'])

   try:
      session.pop('is_child')
   except:
      pass

   return render_template('payment.html', real_price=session['real_price'])

@app.route('/contracts/health_insurance/<price>', methods=['GET', 'POST']) # Health
def form_health(price):
   """
   if g.user_id == None:
      print('Спершу увійдіть')
      return redirect(url_for('login'))
   """
   if request.method == 'GET':
      return render_template('contracts/insurance_health_form.html', price=price)
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

      end_date = request.form['end_date']


      try:
        if request.form['child'] == 'Yes':

            child_second_name = request.form['child_second_name']
            child_first_name = request.form['child_first_name']
            child_third_name_kekw = request.form['child_third_name_kekw']
            session['child_birthday'] = request.form['child_birthday']

            session['contract_text'] = f"""
            Dear {second_name} {first_name} {third_name_kekw},

            This e-mail is generated automatically and is sent to inform you about the terms of 
            your {session['price']}-level insurance agreement. Those are the following:
            The insurance covers health and life of the child {child_second_name} {child_first_name} {child_third_name_kekw} 
            born on {session['child_birthday']}, 
            of our customer: {second_name} {first_name} {third_name_kekw} born on {session['birthday']}, 
            who lives in {city},{town},{street};
            Insurance`s price will be {real_price} uah a day;

            With kind regards,
            CumDickCompany
            """

            session['is_child'] = 1

            status = create_child_contract(f'{child_second_name} {child_first_name} {child_third_name_kekw}',
                                  g.user_id, f'Child Life {session["price"]}', str(real_price), end_date, connection)
            session['contract_id'] = status
            connection.close()


            return render_template('payment.html', real_price=real_price)
      except:
          pass


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
      status = create_contract(g.user_id, f'Life {session["price"]}', str(real_price), end_date, connection)
      session['contract_id'] = status
      connection.close()



      return render_template('payment.html', real_price=real_price)


@app.route('/contracts/auto_insurance/<price>', methods=['GET', 'POST'])
def car_form(price):
   print(price)
   cars = ["Audi", "Mazda", "Volkswagen", "BMW", "Mercedes", "Chevrolet", "Renault", "Peugeot", "Fiat","Ford", "Honda",
           "Hyundai", "Toyota", "Nissan", "Daewoo", "Mitsubishi", "Porsche", "Ferrari",
           "Lamborghini", "Bugatti", "Dodge", "Chrysler", "Rolls-Royce", "Cadillac", "Cherry", "Citroen",
           "Dacia", "Geely", "Hummer", "Infiniti", "Jaguar", "Jeep", "Kia", "Lexus", "Mercedes-Benz",
           "Land Rover", "Range Rover", "Lotus", "Lincoln", "Maserati", "Maybach", "Opel", "Seat", "Subaru",
           "Skoda", "Tesla", "Volvo", "VAZ", "ZAZ", "UAZ", "Moskvich"
           ]
   cars.sort()
   if request.method == 'GET':
      return render_template('contracts/car_insurance_form.html', price=price, cars=cars)
   if request.method == 'POST':
      connection = psycopg2.connect(
         app.config['SQLALCHEMY_DATABASE_URI']
         )
      connection.autocommit = True

      session['price'] = request.form['tariff']

      session['email_user'] = request.form['email']

      if session['price'] == 'beginner':
         real_price = 80
      elif session['price'] == 'plusplus':
         real_price = 150
      elif session['price'] == 'pro':
         real_price = 220
      else:
         raise Exception

      session['real_price'] = real_price

      second_name = request.form['second_name']
      first_name = request.form['first_name']
      third_name_kekw = request.form['third_name_kekw']

      city = request.form['city']
      town = request.form['town']
      street = request.form['street']


      brand = request.form['car']
      model = request.form['model']
      year_of_issue = request.form['year_of_issue']
      reg_num = request.form['reg_num']

      end_date = request.form['end_date']
      print(end_date)

      session['contract_text'] = f"""
      Dear {second_name} {first_name} {third_name_kekw},

      This e-mail is generated automatically and is sent to inform you about the terms of
      your {session['price']}-level insurance agreement. Those are the following:
      The insurance covers an automobile of {brand} brand; model: {model}; 
      Issue year: {year_of_issue}; Registration number: {reg_num};

      We may contact you via mail to:
      {city},{town},{street}
      It`s price will be {real_price} uah a day;

      With kind regards,
      CumDickCompany
      """
      status = create_contract(g.user_id, f'Auto - {session["price"]} {brand} {model}', str(real_price), str(end_date), connection)
      print(g.user_id, f'Auto - {session["price"]} {brand} {model}', str(real_price), str(end_date))
      session['contract_id'] = status
      connection.close()

      return render_template('payment.html', real_price=session['real_price'])

@app.route('/contracts/household_insurance/<price>', methods=['GET', 'POST']) # Household
def new_contract(price):
   """
   if g.user_id == None:
      print('Спершу увійдіть')
      return redirect(url_for('login'))
   """
   if request.method == 'GET':
      return render_template('contracts/flat_form.html', price=price)
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

      end_date = request.form['begin_date']

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
      status = create_contract(g.user_id, f'Household - {price} at {town}, {street}', str(real_price), end_date, connection)
      session['contract_id'] = status
      connection.close()

      return render_template('payment.html', real_price=real_price)



@app.route('/contracts/property_insurance/<price>', methods=['GET', 'POST'])
def property_insurance(price):
   if request.method == 'GET':
      return render_template('contracts/property_insurance.html', price=session['price'])
   if request.method == 'POST':
      connection = psycopg2.connect(
         app.config['SQLALCHEMY_DATABASE_URI']
         )
      connection.autocommit = True


      session['price'] = request.form['tarif']

      session['email_user'] = request.form['email']

      thing_price = request.form['r_price']

      thing_name = request.form['thing_name']

      session['real_price'] = int(thing_price)/100
      real_price = session['real_price']

      second_name = request.form['second_name']
      first_name = request.form['first_name']
      third_name_kekw = request.form['third_name_kekw']

      end_date = request.form['begin_date']

      session['contract_text'] = f"""
      Dear {second_name} {first_name} {third_name_kekw},

      This e-mail is generated automatically and is sent to inform you about the terms of
      your {session['price']}-level insurance agreement. Those are the following:
      The insurance covers a valuable to the customer thing: {thing_name} 
      and it's evaluated price is: {thing_price}
      Therefore, it`s price will be {session['real_price']} uah a day;

      With kind regards,
      CumDickCompany
      """
      status = create_contract(g.user_id, 'Valuables '+str(session['price']), str(real_price), end_date, connection)
      session['contract_id'] = status
      connection.close()

      return render_template('payment.html', real_price=real_price)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
   if request.method == 'GET':
      return render_template('contact.html')
   else:

      text2 = "Question by: "+request.form['name']+ '\n'+request.form['text']+'\nR.S.V.P to ' +request.form['email']
      send_email('8889344@ukr.net', text=text2)
      return render_template('contact.html')

@app.route('/users/me/update_me', methods=['GET', 'POST'])
def update_me():
   connection = psycopg2.connect(
      app.config['SQLALCHEMY_DATABASE_URI']
   )
   connection.autocommit = True
   if request.method == 'GET':
      (customer_id, full_name, age, email, passw, login, bank, role) = get_customer_info(g.user_id, connection)[0][1:-1].split(',')
      g.email = email
      g.fname = full_name

      contracts = get_contract_by_cust(customer_id, connection)
      connection.close()

      g.ins_house = []
      g.ins_life = []
      g.ins_valuables = []
      g.ins_auto = []

      if contracts != []:
         for real_tup in contracts:
            if 'Household' in real_tup[3]:
               g.ins_house.append(str(real_tup[3]) + ' until ' + str(real_tup[5]))
            elif 'Life' in real_tup[3]:
               g.ins_life.append(str(real_tup[3]) + ' until ' + str(real_tup[5]))
            elif 'Valuables' in real_tup[3]:
               g.ins_valuables.append(str(real_tup[3]) + ' until ' + str(real_tup[5]))
            elif 'Auto' in real_tup[3]:
               g.ins_auto.append(str(real_tup[3]) + ' until ' + str(real_tup[5]))

      else:
         g.ins_house = ['Не укладено жодного']
         g.ins_life = ['Не укладено жодного']
         g.ins_valuables = ['Не укладено жодного']
         g.ins_auto = ['Не укладено жодного']

      if g.ins_house == []:
         g.ins_house = ['Не укладено жодного']
      if g.ins_life == []:
         g.ins_life = ['Не укладено жодного']
      if g.ins_valuables == []:
         g.ins_valuables = ['Не укладено жодного']
      if g.ins_auto == []:
         g.ins_auto = ['Не укладено жодного']


      return render_template('users/edit_profile_page.html')
   else:
      (customer_id, full_name, age, email, passw, login, bank, role) = get_customer_info(g.user_id, connection)[0][
                                                                       1:-1].split(',')
      contracts = get_contract_by_cust(customer_id, connection)

      g.ins_house = []
      g.ins_life = []
      g.ins_valuables = []
      g.ins_auto = []

      if contracts != []:
         for real_tup in contracts:
            if 'Household' in real_tup[3]:
               g.ins_house.append(str(real_tup[3]) + ' until ' + str(real_tup[5]))
            elif 'Life' in real_tup[3]:
               g.ins_life.append(str(real_tup[3]) + ' until ' + str(real_tup[5]))
            elif 'Valuables' in real_tup[3]:
               g.ins_valuables.append(str(real_tup[3]) + ' until ' + str(real_tup[5]))
            elif 'Auto' in real_tup[3]:
               g.ins_auto.append(str(real_tup[3]) + ' until ' + str(real_tup[5]))

      else:
         g.ins_house = ['Не укладено жодного']
         g.ins_life = ['Не укладено жодного']
         g.ins_valuables = ['Не укладено жодного']
         g.ins_auto = ['Не укладено жодного']

      if g.ins_house == []:
         g.ins_house = ['Не укладено жодного']
      if g.ins_life == []:
         g.ins_life = ['Не укладено жодного']
      if g.ins_valuables == []:
         g.ins_valuables = ['Не укладено жодного']
      if g.ins_auto == []:
         g.ins_auto = ['Не укладено жодного']


      u_id = session['user_id']
      log_u = session['nickname']
      email_u = request.form['email']
      f_name = request.form['fname']

      birth = request.form['birthdate']
      print(birth)
      year = int(birth[:4])
      month = int(birth[5:7])
      day = int(birth[8:])

      print(birth)

      now = datetime.datetime.now()
      n_year = now.year
      n_month = now.month
      n_day = now.day

      age_u = int(n_year -  year)


      if n_month < month or (n_month == month and n_day < day):
         age_u -=1

      (customer_id, full_name, age, email, passw, login, bank, role) = get_customer_info(u_id, connection)[0][
                                                                       1:-1].split(',')

      status = update_customer(u_id, log_u, email_u, age_u, f_name, bank, connection)

      connection.close()
      return render_template('users/profile_page.html', full_name = f_name, age = age_u, email=email_u)

@app.route('/users/me/my_cabinet',methods=['GET'])
def my_cabinet():
   connection = psycopg2.connect(
      app.config['SQLALCHEMY_DATABASE_URI']
      )
   connection.autocommit = True

   (customer_id, full_name, age, email, passw, login, bank, role) = get_customer_info(g.user_id,connection)[0][1:-1].split(',')

   contracts = get_contract_by_cust(customer_id, connection)

   child_contracts = get_child_contract_by_cust12(customer_id, connection)
   print(child_contracts)

   connection.close()



   g.ins_house = []
   g.ins_life = []
   g.ins_valuables = []
   g.ins_auto = []
   g.ins_childs = []

   print(contracts)

   if contracts != []:
      for real_tup in contracts:
         if 'Household' in real_tup[3]:
            g.ins_house.append(str(real_tup[3])+' until '+str(real_tup[5]))
         elif 'Life' in real_tup[3]:
            g.ins_life.append(str(real_tup[3]) + ' until ' + str(real_tup[5]))
         elif 'Valuables' in real_tup[3]:
            g.ins_valuables.append(str(real_tup[3]) + ' until ' + str(real_tup[5]))
         elif 'Auto' in real_tup[3]:
            g.ins_auto.append(str(real_tup[3]) + ' until ' + str(real_tup[5]))

      if child_contracts != []:
         for real_tup in child_contracts:
            if 'Child' in real_tup[4]:
               g.ins_childs.append(str(real_tup[4]) +" "+ str(real_tup[2]) + ' until ' +str(real_tup[6]))


   else:
      g.ins_house = ['Не укладено жодного']
      g.ins_life = ['Не укладено жодного']
      g.ins_valuables = ['Не укладено жодного']
      g.ins_auto = ['Не укладено жодного']
      g.ins_childs = ['Не укладено жодного']

   if g.ins_house == []:
      g.ins_house = ['Не укладено жодного']
   if g.ins_life == []:
      g.ins_life = ['Не укладено жодного']
   if g.ins_valuables == []:
      g.ins_valuables = ['Не укладено жодного']
   if g.ins_auto == []:
      g.ins_auto = ['Не укладено жодного']
   if g.ins_childs == []:
      g.ins_childs = ['Не укладено жодного']

   return render_template('users/profile_page.html', full_name = full_name, age = age, email=email)


def send_email(email, text = 'For some reason this text was automatically sent to you. Contact us to fix this bug, please.'):
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






@app.route('/users/login', methods=['GET', 'POST'])
def login():
   if request.method == 'GET':
      return render_template('users/sign_in.html')

   elif request.method == 'POST':
      session.pop('user_id', None)
      session.pop('nickname', None)

      connection = psycopg2.connect(
         app.config['SQLALCHEMY_DATABASE_URI']
         )
      connection.autocommit = True

      login_name = request.form['login']
      password = to_sha(request.form['pass'])

      exit_code = login_user(login_name, password, connection)


      if exit_code != -1:
         session['user_id'] = exit_code
         session['nickname'] = login_name

         (customer_id, full_name, age, email, passw, login, bank, role) = get_customer_info(session['user_id'], connection)[0][
                                                                        1:-1].split(',')

         session['role'] = role

         connection.close()
         return redirect(url_for("mainpage"))
      else:
         flash('Користувача з таким логіном і паролем не знайдено')
         return render_template('users/sign_in.html')


@app.route('/users/register', methods = ['GET', 'POST'])
def register():
   if request.method == 'POST':
      connection = psycopg2.connect(
         app.config['SQLALCHEMY_DATABASE_URI']
         )
      connection.autocommit = True

      name = request.form['name']
      login = request.form['login']
      password1 = to_sha(request.form['pass1'])
      password2 = to_sha(request.form['pass2'])
      email = request.form['email']

      birth = request.form['date']
      print(birth)
      year = int(birth[:4])
      month = int(birth[5:7])
      day = int(birth[8:])


      now = datetime.datetime.now()
      n_year = now.year
      n_month = now.month
      n_day = now.day

      age = n_year -  year
      if n_month < month or (n_month == month and n_day < day):
         age -=1



      card = request.form['card']
      if password1 == password2:
         status = registration(login, password1, email, age, name, card,connection)
         flash(status)
         connection.close()
         if 'помилка' in status.lower():
            return render_template('users/registration.html')
         return render_template('mainpage.html')
      else:
         connection.close()
         flash('Введені паролі не співпадають')
         return render_template('users/registration.html')
   if request.method == 'GET' and g.user_id == None:
      return render_template('users/registration.html')
   else:
      redirect(url_for('mainpage'))



@app.route('/users/logout')
def logout():
   session.pop('user_id', None)
   session.pop('nickname', None)
   g.nickname = None
   g.user_id = None

   return render_template('mainpage.html')


if __name__ == '__main__':
   app.run(debug=True)
