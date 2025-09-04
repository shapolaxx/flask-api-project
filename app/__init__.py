from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    db.init_app(app)
    
    with app.app_context():
        from . import routes
        db.create_all()
        
        # Добавьте эти строки для регистрации маршрутов
        app.add_url_rule('/', 'hello', routes.hello)
        app.add_url_rule('/users', 'get_users', routes.get_users, methods=['GET'])
        app.add_url_rule('/users', 'create_user', routes.create_user, methods=['POST'])
    
    return app