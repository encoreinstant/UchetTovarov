from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..db import get_db_connection

reservation_bp = Blueprint('reservation', __name__)

@reservation_bp.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if 'user_id' not in session:
        flash("Сначала войдите в систему", "error")
        return redirect(url_for('auth.login'))

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

            cur.execute("""
                INSERT INTO reservations 
                (username, name, study_group, telegram, reservation_goal, 
                reservation_date, date_take_equipment) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (username, name, study_group, telegram, reservation_goal, 
                 reservation_date, date_take_equipment))

            conn.commit()
            flash("Снаряжение успешно забронировано!", "success")
        else:
            flash("Не удалось найти данные пользователя", "error")

        cur.close()
        conn.close()
        return redirect(url_for('equipment.arenda'))

    cur.close()
    conn.close()
    return render_template('reserve.html', 
                         equipment={'id': equipment[0], 'name': equipment[1]} 
                         if equipment else None)

@reservation_bp.route('/view_reservations')
def view_reservations():
    if 'user_id' not in session:
        flash("Доступ запрещен.", "error")
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()
    
    if session.get('role') == 'admin':
        # Для админа показываем все бронирования
        cur.execute("SELECT * FROM reservations ORDER BY reservation_date DESC")
    else:
        # Для пользователя только его бронирования
        cur.execute("SELECT * FROM reservations WHERE username = %s ORDER BY reservation_date DESC", 
                   (session.get('username'),))
    
    reservations = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('view_reservations.html', reservations=reservations)