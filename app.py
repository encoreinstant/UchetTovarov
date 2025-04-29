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
        name = request.form['name']
        study_group = request.form['study_group']
        telegram = request.form['telegram']
        
        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        cur = conn.cursor()
        
        try:
            cur.execute("INSERT INTO users (username, password, name, study_group, telegram) VALUES (%s, %s, %s, %s, %s)", (username, hashed_password, name, study_group, telegram))
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
        
        # Получаем id, пароль и роль пользователя
        cur.execute("SELECT id, password, role FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        
        cur.close()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['role'] = user[2]  # сохраняем роль
            flash("Вход выполнен успешно!", "success")
            return redirect(url_for('arenda'))
        else:
            flash("Неверное имя пользователя или пароль.", "error")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Вы вышли из аккаунта.", "info")
    return redirect(url_for('main'))

@app.route('/arenda')
def arenda():
    if 'user_id' not in session:
        flash("Пожалуйста, войдите в систему.", "error")
        return redirect(url_for('login'))

    user_role = session.get('role', 'user')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM equipment")
    equipment_list = cur.fetchall()
    cur.close()
    conn.close()

    # Преобразуем в список словарей (если используешь render_template напрямую)
    equipment_list = [
        {'id': row[0], 'type': row[1], 'title': row[2], 'description': row[3]}
        for row in equipment_list
    ]

    return render_template('arenda.html', equipment=equipment_list, role=user_role)

@app.route('/add_equipment', methods=['GET', 'POST'])
def add_equipment():
    if request.method == 'POST':
        type_ = request.form['type']
        title = request.form['title']
        description = request.form.get('description', '')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO equipment (type, title, description) 
            VALUES (%s, %s, %s)
        """, (type_, title, description))
        conn.commit()
        cur.close()
        conn.close()

        flash("Снаряжение успешно добавлено.", "success")
        return redirect(url_for('arenda'))

    return render_template('add_equipment.html')


@app.route('/view_reservations')
def view_reservations():
    # Здесь будет отображение списка броней
    return "Список всех броней"

@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if 'user_id' not in session:
        flash("Сначала войдите в систему", "error")
        return redirect(url_for('login'))

    equipment_id = request.args.get('equipment_id')

    conn = get_db_connection()
    cur = conn.cursor()

    equipment = None
    if equipment_id:
        cur.execute("SELECT id, name FROM equipment WHERE id = %s", (equipment_id,))
        equipment = cur.fetchone()

    if request.method == 'POST':
        reservation_goal = request.form['reservation_goal']
        reservation_date = request.form['reservation_date']
        date_take_equipment = request.form['date_take_equipment']

        user_id = session['user_id']
        cur.execute("SELECT username, name, study_group, telegram FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()

        if user:
            username, name, study_group, telegram = user

            # Вставка брони
            cur.execute("""
                INSERT INTO reservations 
                (username, name, study_group, telegram, reservation_goal, reservation_date, date_take_equipment) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (username, name, study_group, telegram, reservation_goal, reservation_date, date_take_equipment))

            conn.commit()
            flash("Снаряжение успешно забронировано!", "success")
        else:
            flash("Не удалось найти данные пользователя", "error")

        cur.close()
        conn.close()

        return redirect(url_for('arenda'))

    cur.close()
    conn.close()
    return render_template('reserve.html', equipment={'id': equipment[0], 'name': equipment[1]} if equipment else None)


@app.route('/edit_equipment')
def edit_equipment():
    # Здесь будет изменение снаряжения
    return "Изменение снаряжения"

@app.route('/delete_equipment')
def delete_equipment():
    # Здесь будет удаление снаряжения
    return "Удаление снаряжения"

if __name__ == '__main__':
    app.run(debug=True)
