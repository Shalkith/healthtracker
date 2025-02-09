#create a duckdb connection

import duckdb
import os


def connect():
    con = duckdb.connect("file.db")
    return con

def drop_tables(con):
    # drop the table if it exists
    con.sql("DROP TABLE IF EXISTS health_log")
    con.sql("DROP TABLE IF EXISTS users")
    con.sql("DROP TABLE IF EXISTS selections")

def create_tables(con):
    # create a table and load data into it if it doesnt already exist
    con.sql("CREATE TABLE if not exists health_log (date timestamp, recording text,user text)")
    con.sql("CREATE TABLE if not exists users (id int  primary key, name text)")
    con.sql("CREATE TABLE if not exists selections (selection text)")

def create_sequences(con):
    # create a sequence
    con.sql("CREATE SEQUENCE if not exists user_id start 1")
def insert_data(con):
    # insert data into the table
    con.sql("INSERT INTO health_log VALUES ('2021-01-01', 'protien', 'test_user')")
    con.sql("INSERT INTO users (id, name) VALUES (nextval('user_id'), 'Michelle')")
    con.sql("INSERT INTO selections VALUES ('Protien')")
    con.sql("INSERT INTO selections VALUES ('Carbs')")
    con.sql("INSERT INTO selections VALUES ('Veggies')")

def insert_health_log(con, date, recording, user):
    # insert data into the table
    con.sql(f"INSERT INTO health_log VALUES ('{date}', '{recording}', '{user}')")

def insert_selection(con, selection):
    # insert data into the table
    con.sql(f"INSERT INTO selections VALUES ('{selection}')")

def insert_user(con, user):
    # insert data into the table
    con.sql(f"INSERT INTO users (id, name) VALUES (nextval('user_id'), '{user}')")

def query_data(con):
    # query the table
    result = con.table("users").show()
    return result

def close_connection(con):
    # explicitly close the connection
    con.close()
def get_users(con):
    result = con.table("users").show()
    return result

def get_health_log(con):
    result = con.table("health_log").show()
    return result

def get_data(con,query):
    list = []
    result = con.execute(query)
    #turn to list 
    result = result.fetchdf()
    for index, row in result.iterrows():
        row_dict = row.to_dict()
        list.append(row_dict)
    #print(result)
    return list
    

def setup():
    
    con = connect()
    drop_tables(con)
    create_tables(con)
    create_sequences(con)

    insert_data(con)
    result = query_data(con)
    print(result)
    close_connection(con)

if __name__ == '__main__':
    #setup()
    query = 'select * from health_log'
    con = connect()
    print(get_data(con,query))
    close_connection(con)
    print('done')
