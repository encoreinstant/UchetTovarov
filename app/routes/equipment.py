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

    cur.execute("SELECT COUNT(*) FROM equipment WHERE amount != 0")
    total_items_without_zero_amount = cur.fetchone()[0]
    
    # Получаем записи для текущей страницы
    offset = (page - 1) * items_per_page
    #cur.execute("SELECT * FROM equipment ORDER BY id LIMIT %s OFFSET %s", (items_per_page, offset))
    cur.execute("""
    SELECT 
        equipment.id, 
        equipment.title, 
        equipment.description, 
        equipment_types.name AS type_name,
        equipment.amount
    FROM equipment
    JOIN equipment_types ON equipment.type_id = equipment_types.id
    WHERE equipment.amount != 0
    ORDER BY equipment.id
    LIMIT %s OFFSET %s
    """, (items_per_page, offset))
    equipment_list = cur.fetchall()
    
    cur.close()
    conn.close()

    equipment_list = [
    {'id': row[0], 'title': row[1], 'description': row[2], 'type': row[3], 'amount': row[4]}
    for row in equipment_list
    ]

    total_pages = (total_items_without_zero_amount + items_per_page - 1) // items_per_page

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
        amount = request.form['amount']

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id
            FROM equipment_types
            WHERE name = %s
                    
        """,(type_,)
        )
        type_id = cur.fetchone()

        cur.execute("""
            INSERT INTO equipment (title, description, type_id, amount) 
            VALUES (%s, %s, %s, %s)
        """, (title, description, type_id, amount))
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
        amount = request.form['amount']

        cur.execute("""
            SELECT id
            FROM equipment_types
            WHERE name = %s
                    
        """,(type_,)
        )
        type_id = cur.fetchone()

        cur.execute("""
            UPDATE equipment SET type_id = %s, title = %s, description = %s, amount = %s
           
            WHERE id = %s
                    
        """,(type_id, title, description, amount, id)
        )
        conn.commit()
        cur.close()
        conn.close()

        flash("Снаряжение успешно обновлено.", "success")
        return redirect(url_for('equipment.arenda'))

    # GET-запрос: загружаем данные для редактирования
    cur.execute("""
                SELECT t.name, e.title, e.description, e.amount
                FROM equipment e
                JOIN equipment_types t ON e.type_id = t.id
                WHERE e.id = %s                
                """, (id,))
    equipment = cur.fetchone()
    cur.close()
    conn.close()

    equipment_data = {
        'id': id,
        'type': equipment[0],
        'title': equipment[1],
        'description': equipment[2] if equipment[2] else '',
        'amount': equipment[3]
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