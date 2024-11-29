from datetime import datetime
from app import db, app


# Создание и описание моделей класса User со своими параметрами
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(48), unique=True)
    login = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Создание БД, добавить всё
with app.app_context():
    db.create_all()