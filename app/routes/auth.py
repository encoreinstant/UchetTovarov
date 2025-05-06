from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from ..db import get_db_connection
import psycopg2

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
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
            cur.execute("INSERT INTO users (username, password, name, study_group, telegram) VALUES (%s, %s, %s, %s, %s)", 
                       (username, hashed_password, name, study_group, telegram))
            conn.commit()
            flash("Регистрация успешна! Теперь войдите в свой аккаунт.", "success")
            return redirect(url_for('auth.login'))
        except psycopg2.Error as e:
            flash("Ошибка регистрации. Возможно, пользователь уже существует.", "error")
            return redirect(url_for('auth.register'))
        finally:
            cur.close()
            conn.close()
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT id, password, role FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        
        cur.close()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            session['role'] = user[2]
            flash("Вход выполнен успешно!", "success")
            return redirect(url_for('equipment.arenda'))
        else:
            flash("Неверное имя пользователя или пароль.", "error")

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash("Вы вышли из аккаунта.", "info")
    return redirect(url_for('main.index'))