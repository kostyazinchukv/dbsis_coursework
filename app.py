from flask import Flask,render_template,redirect,url_for,request
import smtplib
import psycopg2
from python.connection_BD import registration,login_user,get_customer_info

app = Flask(__name__)


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


@app.route('/new_contract')
def new_contract():

   global nickname
   return render_template('flat_form.html', name_c =nickname)


@app.route('/contact')
def contact():
    global nickname
    return render_template('contact.html', name_c=nickname)


@app.route('/my_cabinet')
def my_cabinet():
   global nickname
   return render_template('profile_page.html', name_c=nickname)


@app.route('/send')
def send_email():
   #global nickname
   #global user_id
   #em = get_customer_info(user_id)[2]
   msg = 'Test'
   server = smtplib.SMTP("smtp.gmail.com", 587)
   server.starttls()
   server.login("cumdickcompany@gmail.com", "CumDickCum")
   server.sendmail("cumdickcompany@gmail.com", '8889344@ukr.net', msg)
   return render_template('mainpage.html', name_c =nickname)


@app.route('/asswecan')
def form_health():
    return render_template('insurance_health_form.html', name_c=nickname)



@app.route('/login', methods=['GET', 'POST'])
def login():

   global user_id
   global nickname
   if request.method == 'GET':
      return render_template('sign_in.html', name_c =nickname)
   elif request.method == 'POST':
      connection = psycopg2.connect(
         host="localhost",
         database="project",
         user="postgres",
         password="postgresql")
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
         host="localhost",
         database="project",
         user="postgres",
         password="postgresql")
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

