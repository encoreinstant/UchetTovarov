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

# Создание таблицы
cur.execute('DROP TABLE IF EXISTS Jokes;')
cur.execute('CREATE TABLE Jokes (id serial PRIMARY KEY,'
            'title varchar (150) NOT NULL,'
            'author varchar (50) NOT NULL,'
            'jokeText text,'
            'date_added date DEFAULT CURRENT_TIMESTAMP);'
            )

# Вставка строки

cur.execute('INSERT INTO Jokes (title, author, jokeText)'
            'VALUES (%s, %s, %s)',
            ('О числах Фибоначчи',
             'Студент ПМИ',
             'Эта шутка про числа Фибоначчи даже хуже, чем предыдущие две вместе взятые')
            )

# Вставка строки

cur.execute('INSERT INTO Jokes (title, author, jokeText)'
            'VALUES (%s, %s, %s)',
            ('Физики шутят',
             'Неизвестный',
             'Не можете найти работу? Умножьте время на мощность!')
            )

# Сохранение операции
conn.commit()

# Закрытие соединения
cur.close()
conn.close()