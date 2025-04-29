from flask import Blueprint, redirect, url_for, render_template
from ..db import get_db_connection

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return redirect(url_for('main.main_page'))

@main_bp.route('/main')
def main_page():
    return render_template('main.html')