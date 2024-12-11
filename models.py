from datetime import datetime
from flask_login import UserMixin
from app import db, app, manager



# Создание и описание модели для подтверждения email
class EmailConfirm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    code = db.Column(db.String(33), unique=True, nullable=False)


# Создание и описание моделей класса User со своими параметрами
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(48), unique=True)
    login = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(64))
    email_confirm = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class DataMessage(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)

    # Связь с моделью User через ForeignKey
    user = db.relationship('User', backref=db.backref('messages', lazy=True))



# Создание БД, добавить всё
with app.app_context():
    db.create_all()


# Загрузка пользователя из БД
@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)