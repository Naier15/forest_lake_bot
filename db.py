import psycopg2
from psycopg2 import Error
from config import user, password, database, host, port


def init():
    try:
        connection = psycopg2.connect(user=user, password=password, host=host, port=port)
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute(f'CREATE DATABASE {database};')
            cursor.execute(f"ALTER DATABASE {database} SET TIMEZONE TO 'asia/vladivostok';")

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL: ", error)
    finally:
        if connection:
            connection.close()

def create():
    try:
        connection = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute("""CREATE TABLE IF NOT EXISTS writers (
                                id SERIAL PRIMARY KEY,
                                user_id INTEGER NOT NULL UNIQUE
                            );"""
            )
            cursor.execute("""CREATE TABLE IF NOT EXISTS workers (
                                id SERIAL PRIMARY KEY,
                                user_id INTEGER NOT NULL UNIQUE
                            );"""
            )
            cursor.execute("""CREATE TABLE IF NOT EXISTS buildings (
	                            id SERIAL PRIMARY KEY, 
	                            building INTEGER NOT NULL UNIQUE, 
	                            stage INTEGER NOT NULL
                            );"""
            )
            cursor.execute("""CREATE TABLE IF NOT EXISTS data (
                            	id SERIAL PRIMARY KEY,
                            	photo BYTEA NOT NULL,
                            	building INTEGER REFERENCES buildings(building) ON DELETE CASCADE,
                            	stage INTEGER NOT NULL,
                            	comment TEXT DEFAULT '',
                            	date VARCHAR(15) DEFAULT to_char(now(), 'dd.mm.yyyy')
                            );"""
            )
            cursor.execute("""CREATE TABLE IF NOT EXISTS docs (
	                            id SERIAL PRIMARY KEY, 
	                            document BYTEA NOT NULL,
	                            building INTEGER REFERENCES buildings(building) ON DELETE CASCADE,
	                            stage INTEGER NOT NULL
                            );"""
            )
            print("created table successfully")

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            connection.close()

def select(command, args=()):
    try:
        connection = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute(command, args)
            print("Execute successfully")
            return cursor.fetchall()

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            connection.close()

def execute(command, args=()):
    try:
        connection = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute(command, args)
            print("Execute successfully")

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            connection.close()