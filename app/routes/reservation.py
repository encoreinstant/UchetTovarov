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

        if action not in ['approve', 'reject', 'delete', 'confirm_delivery', 'confirm_return', 'confirm_no_return']:
            flash("Неверное действие.", "error")
            cur.close()
            conn.close()
            return redirect(url_for('reservation.view_reservations'))

        # Проверяем, существует ли бронирование
        cur.execute("SELECT id FROM reservations WHERE id = %s", (reservation_id,))
        reservation = cur.fetchone()
        if not reservation:
            cur.execute("SELECT id FROM reservations_history WHERE id = %s", (reservation_id,))
            reservation = cur.fetchone()
            if not reservation:
                flash("Бронирование не найдено.", "error")
                cur.close()
                conn.close()
                return redirect(url_for('reservation.view_reservations'))
        
         # Если действие — удаление
        if action == 'delete':

            # Удаляем бронирование
            cur.execute("DELETE FROM reservations WHERE id = %s", (reservation_id,))
            cur.execute("DELETE FROM reservations_history WHERE id = %s", (reservation_id,))
            conn.commit()
            flash("Бронирование успешно удалено.", "success")
            cur.close()
            conn.close()
            return redirect(url_for('reservation.view_reservations'))

        if action == 'confirm_delivery':
            new_status = 4
            new_status_text = 'Выдано'
            cur.execute("UPDATE reservations SET reserve_status_id = %s WHERE id = %s", (new_status, reservation_id))
            cur.execute("""UPDATE equipment SET amount = amount - 1 
                WHERE id = (
                SELECT equipment_id
                FROM reservations
                WHERE id = %s)""", (reservation_id,))
            conn.commit()

            flash(f"Снаряжение {new_status_text.lower()}.", "success")

        if action == 'confirm_return':
            new_status = 5
            new_status_text = 'Возвращено'
            cur.execute("UPDATE reservations SET reserve_status_id = %s WHERE id = %s", (new_status, reservation_id))
            cur.execute("""UPDATE equipment SET amount = amount + 1 
                WHERE id = (
                SELECT equipment_id
                FROM reservations
                WHERE id = %s)""", (reservation_id,))
            
            conn.commit()

            flash(f"Снаряжение {new_status_text.lower()}.", "success")
        
        if action == 'confirm_no_return':
            new_status = 6
            new_status_text = 'Не возвращено'
            cur.execute("UPDATE reservations SET reserve_status_id = %s WHERE id = %s", (new_status, reservation_id))
            
            conn.commit()

            flash(f"Снаряжение {new_status_text.lower()}.", "error")

        if action == 'approve':
            new_status = 2
            new_status_text = 'Одобрено'
            cur.execute("UPDATE reservations SET reserve_status_id = %s WHERE id = %s", (new_status, reservation_id))
            conn.commit()

            flash(f"Бронирование {new_status_text.lower()}.", "success")


        if action == 'reject':
            new_status = 3
            new_status_text = 'Отклонено'
            cur.execute("UPDATE reservations SET reserve_status_id = %s WHERE id = %s", (new_status, reservation_id))
            conn.commit()

            flash(f"Бронирование {new_status_text.lower()}.", "error")

        cur.close()
        conn.close()
        return redirect(url_for('reservation.view_reservations'))

    # Получаем все записи с нужным статусом
    cur.execute("""
        SELECT * FROM reservations
        WHERE reserve_status_id IN (3, 5, 6)
    """)
    rows_to_move = cur.fetchall()

    # Получаем имена столбцов
    colnames = [desc[0] for desc in cur.description]

    # Формируем список плейсхолдеров под INSERT
    placeholders = ', '.join(['%s'] * len(colnames))
    columns = ', '.join(colnames)

    # Вставляем и удаляем записи
    for row in rows_to_move:
        # Вставка в reservations_history
        cur.execute(f"""
            INSERT INTO reservations_history ({columns})
            VALUES ({placeholders})
        """, row)

        # Удаление из reservations по id
        reservation_id = row[colnames.index('id')]
        cur.execute("""
            DELETE FROM reservations WHERE id = %s
        """, (reservation_id,))

    # Сохраняем изменения
    conn.commit()

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
        for row in reservations #if row[8] != 'Возвращено' and row[8] != 'Отклонено' and row[8] != 'Не возвращено'
    ]

    if session.get('role') == 'admin':
        # Для админа показываем все бронирования
        cur.execute("""
            SELECT r.id, u.username, u.name, u.study_group, u.telegram, r.reservation_goal, 
                   r.reservation_date, r.date_take_equipment, r_statuses.name, e.title, et.name
            FROM reservations_history r
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
            FROM reservations_history r
            JOIN equipment e ON r.equipment_id = e.id
            JOIN equipment_types et ON e.type_id = et.id
            JOIN users u ON r.user_id = u.id
            JOIN reserve_statuses r_statuses ON r.reserve_status_id = r_statuses.id
            WHERE u.username = %s
            ORDER BY r.reservation_date DESC
        """, (session.get('username'),))
    
    reservations_history = cur.fetchall()

    reservations_history_list = [
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
        for row in reservations_history #if row[8] == 'Возвращено' or row[8] == 'Отклонено' or row[8] == 'Не возвращено'
    ]

    cur.close()
    conn.close()

    return render_template('view_reservations.html', reservations=reservations_list, reservations_history=reservations_history_list, role=session.get('role'))
