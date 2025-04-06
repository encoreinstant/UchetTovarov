from flask import Flask, render_template, redirect, url_for, request, session, flash
import psycopg2  # Подключаем PostgreSQL через psycopg2
import psycopg2.extras
import hashlib  # Библиотека для хеширования
from werkzeug.security import generate_password_hash, check_password_hash


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
def run():
    return redirect(url_for('main'))  # Перенаправляем на /main

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/index')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM Equipment;')
    equipment = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', equipment=equipment)


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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
        except psycopg2.Error as e:
            flash("Ошибка регистрации. Возможно, пользователь уже существует.", "error")
            return redirect(url_for('register'))
        finally:
            cur.close()
            conn.close()

        flash("Регистрация успешна! Теперь войдите в свой аккаунт.", "success")
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        
        cur.close()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            flash("Вход выполнен успешно!", "success")
            return redirect(url_for('arenda'))  # Страница после входа
        else:
            flash("Неправильное имя пользователя или пароль", "error")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Вы вышли из аккаунта.", "info")
    return redirect(url_for('login'))

@app.route('/arenda')
def arenda():
    if 'user_id' not in session:
        flash("Сначала войдите в систему.", "error")
        return redirect(url_for('login'))
    
    return render_template('arenda.html')



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
