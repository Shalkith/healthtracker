import sqlalchemy
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
load_dotenv()

def connect():
    '''
    create a .env file in the root directory of the project and add the following lines:
    DBUSER=your_database_username
    DBPASSWORD=your_database_password
    DBHOST=your_database_host
    DBPORT=your_database_port
    DB=your_db_name
    '''

    user = os.getenv('DBUSER')
    password = os.getenv('DBPASSWORD')
    host = os.getenv('DBHOST')
    port = os.getenv('DBPORT')
    db = os.getenv('DB')




    # connect to the # mariadb
    engine = create_engine('mysql+mysqlconnector://' + user + ':' + password + '@' + host + ':' + port + '/' + db)
    # run a test query
    #result = engine.execute("select * from health_log")
    connection = engine.connect()
    return connection 


def drop_tables(con):
    # drop the table if it exists
    con.execute(sqlalchemy.text("DROP TABLE IF EXISTS health_log"))
    con.execute(sqlalchemy.text("DROP TABLE IF EXISTS users"))
    con.execute(sqlalchemy.text("DROP TABLE IF EXISTS selections"))

    con.commit()




def create_tables(con):
    # create a table and load data into it if it doesnt already exist
    con.execute(sqlalchemy.text("CREATE TABLE if not exists health_log (date timestamp, recording text,user text)"))
    con.execute(sqlalchemy.text("CREATE TABLE if not exists users (id int  primary key AUTO_INCREMENT, name text)"))
    con.execute(sqlalchemy.text("CREATE TABLE if not exists selections (selection text)"))
    con.commit()


def create_sequences(con):
    # create a sequence
    con.execute(sqlalchemy.text("CREATE SEQUENCE if not exists user_id start 1"))
    con.commit()

def insert_data(con):
    # insert data into the table
    con.execute(sqlalchemy.text("INSERT INTO health_log VALUES ('2021-01-01', 'protien', 'test_user')"))
    con.execute(sqlalchemy.text("INSERT INTO users ( name) VALUES ('Michelle')"))
    con.execute(sqlalchemy.text("INSERT INTO users ( name) VALUES ('Paul')"))
    con.execute(sqlalchemy.text("INSERT INTO selections VALUES ('Protien')"))
    con.execute(sqlalchemy.text("INSERT INTO selections VALUES ('Carbs')"))
    con.execute(sqlalchemy.text("INSERT INTO selections VALUES ('Veggies')"))
    con.commit()

def insert_health_log(con, date, recording, user):
    # insert data into the table
    con.execute(sqlalchemy.text(f"INSERT INTO health_log VALUES ('{date}', '{recording}', '{user}')"))
    con.commit()

def insert_selection(con, selection):
    # insert data into the table
    con.execute(sqlalchemy.text(f"INSERT INTO selections VALUES ('{selection}')"))
    con.commit()

def insert_user(con, user):
    # insert data into the table
    con.execute(sqlalchemy.text(f"INSERT INTO users (name) VALUES ('{user}')"))
    con.commit()

def close_connection(con):
    # explicitly close the connection
    con.close()

    


def get_data(con,query):
    list = []
    result = con.execute(sqlalchemy.text(query))
    #turn to list 
    result = result.fetchall()
    for row in result:
        list.append(row)
    return list

    

def setup():
    
    con = connect()
    drop_tables(con)
    create_tables(con)
    create_sequences(con)

    insert_data(con)
    close_connection(con)

if __name__ == '__main__':
    #setup()
    query = 'select * from health_log'
    con = connect()
    print(get_data(con,query))
    close_connection(con)
    print('done')

        