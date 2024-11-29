from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_user, logout_user, login_required

app = Flask(__name__)

# Настройка базы данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///database.db'
db = SQLAlchemy(app)

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


@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        print(email, username, password)

        # Создание данных
        user = User(email=email, login=username, password=password)
        # Формируем сессии для последующего добавления в БД
        db.session.add(user)
        # Сохранение в базу данных всех сформированных сессий одним комитом
        db.session.commit()

    return render_template('base.html')


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Чтение данных
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            print(f'Успешная авторизация! {user.email}, {user.password}')
            return render_template('index.html')
        print('Ошибка авторизации!')

    return render_template('base.html')


@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/')
def logout():
    logout_user()
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run()