# from flask import Flask, render_template, redirect, url_for, request, session
# import sqlite3  # подключаем Sqlite в наш проект
# import hashlib  # библиотека для хеширования

# app = Flask(__name__)
# app.secret_key = '1234'  # подствавьте свой секретный ключ
# # секретный ключ для хеширования данных сессии при авторизации

# # Устанавливаем соединение с Базой Данных
# def get_db_connection():
#     conn = sqlite3.connect('database.db')
#     conn.row_factory = sqlite3.Row
#     return conn


# @app.route('/')
# def home():
#     return render_template('landing.html')


# @app.route('/adm_login', methods=['GET', 'POST'])
# def admin_login():
#     error = None  # обнуляем переменную ошибок
#     if request.method == 'POST':
#         username = request.form['username']  # обрабатываем запрос с нашей формы который имеет атрибут name="username"
#         password = request.form['password']  # обрабатываем запрос с нашей формы который имеет атрибут name="password"
#         hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()  # шифруем пароль в sha-256

#         # устанавливаем соединение с БД
#         conn = get_db_connection()
#         # создаем запрос для поиска пользователя по username,
#         # если такой пользователь существует, то получаем все данные id, password
#         user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
#         # закрываем подключение БД
#         conn.close()

#         # теперь проверяем если данные сходятся формы с данными БД
#         if user and user['password'] == hashed_password:
#             # в случае успеха создаем сессию в которую записываем id пользователя
#             session['user_id'] = user['id']
#             # и делаем переадресацию пользователя на новую страницу -> в нашу адимнку
#             return redirect(url_for('admin_panel'))

#         else:
#             error = 'Неправильное имя пользователя или пароль'

#     return render_template('adm_login.html', error=error)


# @app.route('/logout')
# def logout():
#     # Удаление данных пользователя из сессии
#     session.clear()
#     # Перенаправление на главную страницу или страницу входа
#     return redirect(url_for('home'))


# @app.route('/admin_panel')
# def admin_panel():
#     # делаем доп проверку если сессия авторизации была создана
#     if 'user_id' not in session:
#         return redirect(url_for('admin_login'))
#     return render_template('admin_panel.html')

# @app.route('/about')
# def about():
#   return 'This is the about page'

# @app.route('/user/<username>')
# def show_user_profile(username):
#   return f'User {username}'


# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, redirect, url_for, request, session
import psycopg2  # Подключаем PostgreSQL через psycopg2
import psycopg2.extras
import hashlib  # Библиотека для хеширования


app = Flask(__name__)
app.secret_key = '1234'  # Подставьте свой секретный ключ

# Функция для подключения к базе данных PostgreSQL
def get_db_connection():
    conn = psycopg2.connect(
        dbname='flaskdb',  # Имя вашей базы данных
        user='postgres',   # Имя пользователя
        password='root',   # Пароль
        host='localhost',        # Хост (или IP-адрес сервера БД)
        port='5432'              # Порт PostgreSQL (по умолчанию 5432)
    )
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Jokes;')
    jokes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', jokes=jokes)


@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        jokeText = request.form['jokeText']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO jokes (title, author, jokeText)'
                    'VALUES (%s, %s, %s)',
                    (title, author, jokeText))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))

    return render_template('create.html')


# @app.route('/')
# def home():
#     return render_template('landing.html')

# @app.route('/adm_login', methods=['GET', 'POST'])
# def admin_login():
#     error = None  # Обнуляем переменную ошибок
#     if request.method == 'POST':
#         username = request.form['username']  # Получаем имя пользователя
#         password = request.form['password']  # Получаем пароль
#         hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()  # Хешируем пароль

#         conn = get_db_connection()
#         cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        
#         # Выполняем запрос на поиск пользователя
#         cur.execute('SELECT * FROM users WHERE username = %s', (username,))
#         user = cur.fetchone()
        
#         cur.close()
#         conn.close()

#         if user and user['password'] == hashed_password:
#             session['user_id'] = user['id']  # Создаём сессию
#             return redirect(url_for('admin_panel'))  # Переход в админку
#         else:
#             error = 'Неправильное имя пользователя или пароль'

#     return render_template('adm_login.html', error=error)

# @app.route('/logout')
# def logout():
#     session.clear()  # Очистка сессии
#     return redirect(url_for('home'))

# @app.route('/admin_panel')
# def admin_panel():
#     if 'user_id' not in session:
#         return redirect(url_for('admin_login'))
#     return render_template('admin_panel.html')

# @app.route('/about')
# def about():
#     return 'This is the about page'

# @app.route('/user/<username>')
# def show_user_profile(username):
#     return f'User {username}'

if __name__ == '__main__':
    app.run(debug=True)
