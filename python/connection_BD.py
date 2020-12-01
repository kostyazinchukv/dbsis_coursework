import psycopg2
import datetime
import hashlib

def registration(login, password, email, age, name, card, connection):
    'Повертає статус у вигляді текстового рядка'
    cursor = connection.cursor()
    
    cursor.callproc('register_customer', (login, password, email, age, name, card))
    
    status = cursor.fetchone()[0]
    
    return status

def login_user(login_or_email, password, connection):
    'Повертає id користувача'
    cursor = connection.cursor()
    
    cursor.callproc('login_customer', (login_or_email, password))
    
    c_id = cursor.fetchall()[0][0]
    
    return c_id


def create_child_contract(child_name, fk_customer_id, contract_type, contract_price, contract_end_date, connection):
    'Повертає статус у вигляді текстового рядка'
    cursor = connection.cursor()
    
    cursor.callproc('create_child_contract', (child_name, fk_customer_id, contract_type, contract_price, contract_end_date))
    
    status = cursor.fetchone()[0]
    
    return status


def create_contract(fk_customer_id, contract_type, contract_price, contract_end_date, connection):
    'Повертає статус у вигляді текстового рядка'
    cursor = connection.cursor()
    
    cursor.callproc('create_contract', (fk_customer_id, contract_type, contract_price, contract_end_date))
    
    status = cursor.fetchone()[0]
    
    return status


def get_customer_info(customer_id, connection):
    'Повертає кортеж з (customer_id, Імя, е-mail, password, login, карта банку, role)'
    cursor = connection.cursor()

    cursor.execute(f"SELECT get_customer_info({customer_id})")

    
    result = cursor.fetchall()[0]
    
    return result

def update_customer(c_id,customer_login_v,customer_email_v, customer_age_v,customer_name_v,bank_card_v, connection):
    'Повертає статус у вигляді текстового рядка'
    cursor = connection.cursor()

    cursor.callproc('update_customer', (c_id,customer_login_v,customer_email_v,customer_age_v,customer_name_v,bank_card_v))

    status = cursor.fetchone()[0]

    return status


def get_contract_by_cust(customer_id, connection):
    'Повертає кортеж з (contract_id, customer_id, дата укладання, тип контракту, ціна на день, кінцева дата терміну дії)'
    cursor = connection.cursor()

    cursor.execute(f"select * from contracts where contracts.fk_customer_id = {customer_id}")
    
    result = cursor.fetchall()
    
    return result


# Я хз як ввести дату, кста, в цьому пакеті ))0)00
def get_contract_by_date(create_date, connection):
    'Повертає кортеж з (contract_id, customer_id, дата укладання, тип контракту, ціна на день, кінцева дата терміну дії)'
    cursor = connection.cursor()
    
    cursor.callproc('get_contract_by_date', (create_date))
    
    result = cursor.fetchall()
    
    return result



def get_child_contract_by_cust(customer_id, connection):
    'Повертає кортеж з (child_id, customer_id, Імя дитини, дата укладання, тип контракту, ціна на день, кінцева дата терміну дії)'
    cursor = connection.cursor()
    
    cursor.callproc('get_child_contract_by_cust', (customer_id))
    
    result = cursor.fetchall()
    
    return result


# Я хз як ввести дату, кста, в цьому пакеті ))0)00
def get_child_contract_by_date(create_date):
    'Повертає кортеж з (child_id, customer_id, Імя дитини, дата укладання, тип контракту, ціна на день, кінцева дата терміну дії)'
    cursor = connection.cursor()
    
    cursor.callproc('get_child_contract_by_date', (create_date))
    
    result = cursor.fetchall()
    
    return result




if __name__ == '__main__':
    connection = psycopg2.connect(
        host="localhost",
        database="project",
        user="postgres",
        password="postgresql")


    connection.autocommit = True

    print(get_contract_by_cust(19,connection))
    #print(create_contract(2, 'SS', 14.88, '2020-10-22'))

    #print(get_contract_by_date(datetime.date(2020, 10, 22)))

    # print(login('admin_log','123456'))

    
