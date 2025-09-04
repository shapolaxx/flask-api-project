from flask import jsonify, request
from . import db
from .models import User


def hello():
    return jsonify({"message": "Hello World!"})

def get_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "username": u.username, "email": u.email} for u in users])

def create_user():
    data = request.get_json()
    new_user = User(username=data['username'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"id": new_user.id, "username": new_user.username, "email": new_user.email}), 201"// Тест CI/CD пайплайна" 
"// Тест CI/CD пайплайна" 
"// Тест CI/CD пайплайна" 
"# Тест CI/CD пайплайна" 
"# Тест CI/CD пайплайна" 
