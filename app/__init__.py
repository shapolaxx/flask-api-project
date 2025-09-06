from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    db.init_app(app)
    
    # Инициализируем Object Storage
    from .storage import init_storage
    init_storage(app)
    
    with app.app_context():
        from . import routes
        from . import file_routes
        db.create_all()
        
        # Основные маршруты
        app.add_url_rule('/', 'hello', routes.hello)
        app.add_url_rule('/users', 'get_users', routes.get_users, methods=['GET'])
        app.add_url_rule('/users', 'create_user', routes.create_user, methods=['POST'])
        
        # Маршруты для работы с файлами
        app.add_url_rule('/files/upload', 'upload_file', file_routes.upload_file, methods=['POST'])
        app.add_url_rule('/files/<filename>/download', 'download_file', file_routes.download_file, methods=['GET'])
        app.add_url_rule('/files/<filename>', 'delete_file', file_routes.delete_file, methods=['DELETE'])
        app.add_url_rule('/files', 'list_files', file_routes.list_files, methods=['GET'])
        app.add_url_rule('/files/<filename>/info', 'get_file_info', file_routes.get_file_info, methods=['GET'])
        
        # Health check для storage
        app.add_url_rule('/health/storage', 'storage_health', file_routes.storage_health, methods=['GET'])
    
    return app