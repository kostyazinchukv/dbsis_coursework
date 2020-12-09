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


def update_customer_role(customer_login, new_role, connection):
    'Повертає кортеж з (customer_id, Імя, е-mail, password, login, карта банку, role)'
    cursor = connection.cursor()

    cursor.execute(f"""

                    UPDATE CUSTOMERS SET customer_role = '{new_role}'
                    WHERE customer_login = '{customer_login}'

                    """)

    return 'Updated successfully'

def get_customer_by_login(customer_log, connection):
    'Повертає кортеж з (customer_id, Імя, е-mail, password, login, карта банку, role)'
    cursor = connection.cursor()

    cursor.execute(f"""	
    SELECT CUSTOMERS.CUSTOMER_NAME, CUSTOMERS.BANK_CARD,
                    CONTRACTS.CONTRACT_TYPE, CONTRACTS.CONTRACT_DATE, CONTRACTS.CONTRACT_END_DATE, CUSTOMERS.CUSTOMER_ROLE,
                        CONTRACTS.CONTRACT_IS_PAID
	FROM CUSTOMERS JOIN CONTRACTS ON customers.customer_id = contracts.fk_customer_id
	WHERE customers.customer_login = '{customer_log}';""")


    result = cursor.fetchall()

    return result



def get_children_by_login(customer_log, connection):
    'Повертає кортеж з (customer_id, Імя, е-mail, password, login, карта банку, role)'
    cursor = connection.cursor()

    cursor.execute(f"""	
        SELECT CHILDREN_CONTRACTS.CHILD_NAME, CHILDREN_CONTRACTS.CONTRACT_DATE, CHILDREN_CONTRACTS.CONTRACT_END_DATE,
					CHILDREN_CONTRACTS.CONTRACT_IS_PAID,CHILDREN_CONTRACTS.CONTRACT_TYPE
        FROM CUSTOMERS JOIN CHILDREN_CONTRACTS ON customers.customer_id = CHILDREN_CONTRACTS.fk_customer_id
        WHERE customers.customer_login = '{customer_log}';""")



    result = cursor.fetchall()

    return result



def get_customer_i_by_login(customer_log, connection):
    'Повертає кортеж з (customer_id, Імя, е-mail, password, login, карта банку, role)'
    cursor = connection.cursor()

    cursor.execute(f"""	
    SELECT CUSTOMERS.CUSTOMER_NAME, CUSTOMERS.BANK_CARD, CUSTOMERS.CUSTOMER_ROLE
	FROM CUSTOMERS
	WHERE customers.customer_login = '{customer_log}';""")


    result = cursor.fetchall()[0]

    return result


def update_customer(c_id,customer_login_v,customer_email_v, customer_age_v,customer_name_v,bank_card_v, connection):
    'Повертає статус у вигляді текстового рядка'
    cursor = connection.cursor()

    cursor.callproc('update_customer', (c_id,customer_login_v,customer_email_v,customer_age_v,customer_name_v,bank_card_v))

    status = cursor.fetchone()[0]

    return status


def update_payment_status(contract_id):
    'Повертає статус у вигляді текстового рядка'
    connection = psycopg2.connect(
        host="localhost",
        database="project",
        user="postgres",
        password="postgresql")


    connection.autocommit = True
    cursor = connection.cursor()

    cursor.execute(f"""	
            UPDATE CONTRACTS
            SET contract_is_paid = true
            WHERE contract_id = {contract_id}""")

    connection.close()

    return 'Payment successful'


def update_child_payment_status(contract_id):
    'Повертає статус у вигляді текстового рядка'
    connection = psycopg2.connect(
        host="localhost",
        database="project",
        user="postgres",
        password="postgresql")


    connection.autocommit = True
    cursor = connection.cursor()

    cursor.execute(f"""	
        UPDATE children_contracts
        SET contract_is_paid = true
        WHERE child_id = {contract_id}""")

    connection.close()

    return 'Payment successful'


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

    #print(get_customer_by_login("Vlados Herasymenko",connection))

    #print(update_role('fullmaster1', "Full Master", connection))

    #print(get_contract_by_cust(19,connection))
    #print(create_contract(2, 'SS', 14.88, '2020-10-22'))

    #print(get_contract_by_date(datetime.date(2020, 10, 22)))

    # print(login('admin_log','123456'))

    
