from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..db import get_db_connection

equipment_bp = Blueprint('equipment', __name__)

@equipment_bp.route('/arenda')
@equipment_bp.route('/arenda/<int:page>')
def arenda(page=1):
    if 'user_id' not in session:
        flash("Пожалуйста, войдите в систему.", "error")
        return redirect(url_for('auth.login'))

    user_role = session.get('role', 'user')
    items_per_page = 5  # Количество элементов на странице

    conn = get_db_connection()
    cur = conn.cursor()
    
    # Получаем общее количество записей
    cur.execute("SELECT COUNT(*) FROM equipment")
    total_items = cur.fetchone()[0]
    
    # Получаем записи для текущей страницы
    offset = (page - 1) * items_per_page
    cur.execute("SELECT * FROM equipment ORDER BY id LIMIT %s OFFSET %s", (items_per_page, offset))
    equipment_list = cur.fetchall()
    
    cur.close()
    conn.close()

    equipment_list = [
        {'id': row[0], 'type': row[1], 'title': row[2], 'description': row[3]}
        for row in equipment_list
    ]

    total_pages = (total_items + items_per_page - 1) // items_per_page

    return render_template('arenda.html', 
                         equipment=equipment_list, 
                         role=user_role,
                         current_page=page,
                         total_pages=total_pages)

@equipment_bp.route('/add_equipment', methods=['GET', 'POST'])
def add_equipment():
    if 'user_id' not in session or session.get('role') != 'admin':
        #flash("Доступ запрещен.", "error")
        return redirect(url_for('equipment.arenda'))

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
        return redirect(url_for('equipment.arenda'))

    return render_template('add_equipment.html')

@equipment_bp.route('/edit_equipment/<int:id>', methods=['GET', 'POST'])
def edit_equipment(id):
    if 'user_id' not in session:
        flash("Пожалуйста, войдите в систему.", "error")
        return redirect(url_for('auth.login'))
    
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        type_ = request.form['type']
        title = request.form['title']
        description = request.form.get('description', '')

        cur.execute(
            "UPDATE equipment SET type = %s, title = %s, description = %s WHERE id = %s",
            (type_, title, description, id)
        )
        conn.commit()
        cur.close()
        conn.close()

        flash("Снаряжение успешно обновлено.", "success")
        return redirect(url_for('equipment.arenda'))

    # GET-запрос: загружаем данные для редактирования
    cur.execute("SELECT type, title, description FROM equipment WHERE id = %s", (id,))
    equipment = cur.fetchone()
    cur.close()
    conn.close()

    equipment_data = {
        'id': id,
        'type': equipment[0],
        'title': equipment[1],
        'description': equipment[2] if equipment[2] else ''
    }
    return render_template('edit_equipment.html', equipment=equipment_data)



@equipment_bp.route('/delete_equipment/<int:equipment_id>', methods=['POST'])
def delete_equipment(equipment_id):
    if 'user_id' not in session:
        flash("Пожалуйста, войдите в систему.", "error")
        return redirect(url_for('auth.login'))

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Удаляем запись по id
        cur.execute("DELETE FROM equipment WHERE id = %s", (equipment_id,))
        conn.commit()
        
        cur.close()
        conn.close()
        
        flash("Снаряжение успешно удалено!", "success")
    except Exception as e:
        flash(f"Ошибка при удалении: {str(e)}", "error")
    
    return redirect(url_for('equipment.arenda'))