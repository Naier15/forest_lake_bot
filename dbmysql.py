import pymysql
from config import user, password, database, host


def init():
    try:
        connection = pymysql.connect(user=user, password=password, host=host, autocommit=True)

        with connection.cursor() as cursor:
            cursor.execute(f'CREATE DATABASE {database};')
            cursor.execute("""SET GLOBAL time_zone = '+10:00';""")

    except Exception as error:
        print("Ошибка при работе с MySql: ", error)
    finally:
        if connection:
            connection.close()

def create():
    try:
        connection = pymysql.connect(database=database, user=user, password=password, host=host, autocommit=True)

        with connection.cursor() as cursor:
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {database}.writers (
                                id SERIAL PRIMARY KEY,
                                user_id INTEGER NOT NULL UNIQUE
                            );"""
            )
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {database}.workers (
                                id SERIAL PRIMARY KEY,
                                user_id INTEGER NOT NULL UNIQUE
                            );"""
            )
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {database}.buildings (
	                            id SERIAL PRIMARY KEY, 
	                            building INTEGER NOT NULL UNIQUE, 
	                            stage INTEGER NOT NULL
                            );"""
            )
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {database}.data (
                            	id SERIAL PRIMARY KEY,
                            	photo MEDIUMBLOB NOT NULL,
                            	building INTEGER REFERENCES buildings(building) ON DELETE CASCADE,
                            	stage INTEGER NOT NULL,
                            	comment TEXT,
                            	date DATETIME DEFAULT NOW()
                            );"""
            )
            cursor.execute(f"""CREATE TABLE IF NOT EXISTS {database}.docs (
	                            id SERIAL PRIMARY KEY, 
	                            document MEDIUMBLOB NOT NULL,
	                            building INTEGER REFERENCES buildings(building) ON DELETE CASCADE,
	                            stage INTEGER NOT NULL
                            );"""
            )
            
            print("created table successfully")

    except Exception as error:
        print("Ошибка при работе с MySql", error)
    finally:
        if connection:
            connection.close()

def select(command, args=()):
    try:
        connection = pymysql.connect(database=database, user=user, password=password, host=host, autocommit=True)

        with connection.cursor() as cursor:
            cursor.execute(command, args)
            print("Execute successfully")
            return cursor.fetchall()

    except Exception as error:
        print("Ошибка при работе с MySql", error)
    finally:
        if connection:
            connection.close()

def execute(command, args=()):
    try:
        connection = pymysql.connect(database=database, user=user, password=password, host=host, autocommit=True)

        with connection.cursor() as cursor:
            cursor.execute(command, args)
            print("Execute successfully")

    except Exception as error:
        print("Ошибка при работе с MySql", error)
    finally:
        if connection:
            connection.close()