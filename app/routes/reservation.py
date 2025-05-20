from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..db import get_db_connection

reservation_bp = Blueprint('reservation', __name__)

@reservation_bp.route('/reserve', methods=['GET', 'POST'])
def reserve():
    if 'user_id' not in session:
        flash("Сначала войдите в систему", "error")
        return redirect(url_for('auth.login'))

    # Для GET-запроса извлекаем equipment_id из query-параметров URL
    equipment_id = request.args.get('equipment_id')

    # Для POST-запроса извлекаем equipment_id из формы
    if request.method == 'POST':
        equipment_id = request.form.get('equipment_id')

    # Проверяем, что equipment_id передан и является числом
    if not equipment_id or not equipment_id.isdigit():
        flash("Неверный ID снаряжения.", "error")
        return redirect(url_for('equipment.arenda'))

    conn = get_db_connection()
    cur = conn.cursor()

    # Загружаем данные об оборудовании
    cur.execute("SELECT id, title FROM equipment WHERE id = %s", (equipment_id,))
    equipment = cur.fetchone()

    # Проверяем, что снаряжение найдено
    if not equipment:
        flash("Снаряжение не найдено.", "error")
        cur.close()
        conn.close()
        return redirect(url_for('equipment.arenda'))

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
                (reservation_goal, reservation_date, date_take_equipment, equipment_id, user_id, reserve_status_id) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (reservation_goal, reservation_date, date_take_equipment, equipment[0], user_id, 1))

            conn.commit()
            flash("Снаряжение успешно забронировано!", "success")
        else:
            flash("Не удалось найти данные пользователя", "error")

        cur.close()
        conn.close()
        return redirect(url_for('equipment.arenda'))

    cur.close()
    conn.close()
    return render_template('reserve.html', equipment={'id': equipment[0], 'title': equipment[1]})

@reservation_bp.route('/view_reservations', methods=['GET', 'POST'])
def view_reservations():
    if 'user_id' not in session:
        flash("Пожалуйста, войдите в систему.", "error")
        return redirect(url_for('auth.login'))

    conn = get_db_connection()
    cur = conn.cursor()

    # Обработка POST-запроса для изменения статуса бронирования
    if request.method == 'POST':
        

        reservation_id = request.form.get('reservation_id')
        action = request.form.get('action')

        # Проверяем, что reservation_id и action переданы
        if not reservation_id or not reservation_id.isdigit():
            flash("Неверный ID бронирования.", "error")
            cur.close()
            conn.close()
            return redirect(url_for('reservation.view_reservations'))

        if action not in ['approve', 'reject', 'delete']:
            flash("Неверное действие.", "error")
            cur.close()
            conn.close()
            return redirect(url_for('reservation.view_reservations'))

        # Проверяем, существует ли бронирование
        cur.execute("SELECT id FROM reservations WHERE id = %s", (reservation_id,))
        reservation = cur.fetchone()
        if not reservation:
            flash("Бронирование не найдено.", "error")
            cur.close()
            conn.close()
            return redirect(url_for('reservation.view_reservations'))
        
         # Если действие — удаление
        if action == 'delete':
            # Проверяем права: админ может удалять всё, пользователь — только свои брони
            #if session.get('role') != 'admin' and reservation[0] != session['user_id']:
            #     flash("У вас нет прав для удаления этого бронирования.", "error")
            #     cur.close()
            #     conn.close()
            #     return redirect(url_for('reservation.view_reservations'))

            # Удаляем бронирование
            cur.execute("DELETE FROM reservations WHERE id = %s", (reservation_id,))
            conn.commit()
            flash("Бронирование успешно удалено.", "success")
            cur.close()
            conn.close()
            return redirect(url_for('reservation.view_reservations'))

        # Обновляем статус бронирования
        new_status = 2 if action == 'approve' else 3
        new_status_text = 'Одобрено' if action == 'approve' else 'Отклонено'
        cur.execute("UPDATE reservations SET reserve_status_id = %s WHERE id = %s", (new_status, reservation_id))
        conn.commit()

        flash(f"Бронирование {new_status_text.lower()}.", "success" if action == 'approve' else "error")

        cur.close()
        conn.close()
        return redirect(url_for('reservation.view_reservations'))

    # Обработка GET-запроса для отображения списка бронирований
    if session.get('role') == 'admin':
        # Для админа показываем все бронирования
        cur.execute("""
            SELECT r.id, u.username, u.name, u.study_group, u.telegram, r.reservation_goal, 
                   r.reservation_date, r.date_take_equipment, r_statuses.name, e.title, et.name
            FROM reservations r
            JOIN equipment e ON r.equipment_id = e.id
            JOIN equipment_types et ON e.type_id = et.id
            JOIN users u ON r.user_id = u.id
            JOIN reserve_statuses r_statuses ON r.reserve_status_id = r_statuses.id
            ORDER BY r.reservation_date DESC
        """)
    else:
        # Для пользователя только его бронирования
        cur.execute("""
            SELECT r.id, u.username, u.name, u.study_group, u.telegram, r.reservation_goal, 
                   r.reservation_date, r.date_take_equipment, r_statuses.name, e.title, et.name
            FROM reservations r
            JOIN equipment e ON r.equipment_id = e.id
            JOIN equipment_types et ON e.type_id = et.id
            JOIN users u ON r.user_id = u.id
            JOIN reserve_statuses r_statuses ON r.reserve_status_id = r_statuses.id
            WHERE u.username = %s
            ORDER BY r.reservation_date DESC
        """, (session.get('username'),))
    
    reservations = cur.fetchall()
    cur.close()
    conn.close()

    # Преобразуем результат в список словарей для удобства в шаблоне
    reservations_list = [
        {
            'id': row[0],
            'username': row[1],
            'name': row[2],
            'study_group': row[3],
            'telegram': row[4],
            'reservation_goal': row[5],
            'reservation_date': row[6],
            'date_take_equipment': row[7],
            'reserve_status': row[8],
            'equipment_title': row[9],
            'equipment_type': row[10],
        }
        for row in reservations
    ]

    return render_template('view_reservations.html', reservations=reservations_list, role=session.get('role'))
