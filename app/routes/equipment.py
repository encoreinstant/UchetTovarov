from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..db import get_db_connection

equipment_bp = Blueprint('equipment', __name__)

@equipment_bp.route('/arenda')
def arenda():
    if 'user_id' not in session:
        flash("Пожалуйста, войдите в систему.", "error")
        return redirect(url_for('auth.login'))

    user_role = session.get('role', 'user')

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM equipment")
    equipment_list = cur.fetchall()
    cur.close()
    conn.close()

    equipment_list = [
        {'id': row[0], 'type': row[1], 'title': row[2], 'description': row[3]}
        for row in equipment_list
    ]

    return render_template('arenda.html', equipment=equipment_list, role=user_role)

@equipment_bp.route('/add_equipment', methods=['GET', 'POST'])
def add_equipment():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Доступ запрещен.", "error")
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
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Доступ запрещен.", "error")
        return redirect(url_for('equipment.arenda'))
    
    # Здесь добавь логику редактирования
    return "Редактирование снаряжения"

@equipment_bp.route('/delete_equipment/<int:id>')
def delete_equipment(id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Доступ запрещен.", "error")
        return redirect(url_for('equipment.arenda'))
    
    # Здесь добавь логику удаления
    return "Удаление снаряжения"