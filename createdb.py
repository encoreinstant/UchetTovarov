# import sqlite3

# # Создание или подключение к базе данных
# conn = sqlite3.connect('database.db')

# # Создание курсора
# c = conn.cursor()

# # Создание таблицы Content
# c.execute('''CREATE TABLE IF NOT EXISTS content (
#              id INTEGER PRIMARY KEY AUTOINCREMENT,
#              idblock TEXT,
#              short_title TEXT,
#              img TEXT,
#              altimg TEXT,
#              title TEXT,
#              contenttext TEXT,
#              author TEXT,
#              timestampdata DATETIME)''')

# # Создание таблицы Users
# c.execute('''CREATE TABLE IF NOT EXISTS users (
#              id INTEGER PRIMARY KEY AUTOINCREMENT,
#              username TEXT,
#              password TEXT)''')

# # Закрытие соединения с базой данных
# conn.close()

import os
import psycopg2

# Установка соединения с БД
# echo $env:POSTGRES_DB
# echo $env:USERNAME_DB
# echo $env:PASSWORD_DB

# conn = psycopg2.connect(host="localhost",
#                         database=os.environ['POSTGRES_DB'],
#                         user=os.environ['USERNAME_DB'],
#                         password=os.environ['PASSWORD_DB'])

# Установка соединения с БД
conn = psycopg2.connect(host="localhost",
                        database='flaskdb',
                        user='postgres',
                        password='root')

print("Подключение успешно!")
# Курсор - это объект, позволяющий взаимодействовать с БД
cur = conn.cursor()

# Создание таблицы Equipment
cur.execute('DROP TABLE IF EXISTS Equipment;')
cur.execute('CREATE TABLE Equipment ('
            'id serial PRIMARY KEY,'
            'type varchar(100) NOT NULL,'
            'title varchar(150) NOT NULL,'
            'description text,'
            'date_added date DEFAULT CURRENT_TIMESTAMP);'
            )


# Вставка строки в таблицу Equipment
cur.execute('INSERT INTO Equipment (type, title, description) '
            'VALUES (%s, %s, %s)',
            ('Палатка',
             'Nessen Bjorn 2',
             'Черная, 2-местная')
            )


# Вставка строки в таблицу Equipment
cur.execute('INSERT INTO Equipment (type, title, description) '
            'VALUES (%s, %s, %s)',
            ('Палатка',
             'Btrace Guard 3',
             'В черной сумке')
            )

# Сохранение операции
conn.commit()

# Закрытие соединения
cur.close()
conn.close()