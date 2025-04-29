import os
from flask import Flask
from .config import Config


def create_app():
    base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, 'templates'),
        static_folder=os.path.join(base_dir, 'static')
    )
    #app = Flask(__name__)
    
    # Загружаем конфигурацию
    app.config.from_object(Config)
    
    # Регистрируем blueprints
    from .routes.main import main_bp
    from .routes.auth import auth_bp
    from .routes.equipment import equipment_bp
    from .routes.reservation import reservation_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(equipment_bp)
    app.register_blueprint(reservation_bp)
    

    print("Текущая рабочая директория:", os.getcwd())
    print("Папка шаблонов Flask:", app.template_folder)

    return app