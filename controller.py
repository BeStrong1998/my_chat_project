
from flask import render_template, request, redirect, url_for
from flask_login import current_user, login_user, logout_user, login_required
from flask_socketio import send

from app import socketio
from app import app, db
from business_logic.check_fata import check_auth_data
from models import User


@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('login')
        password = request.form.get('password')
        print(email, username, password)

        if check_auth_data(login, password):
            # Создание данных с проверкой
            user = User(email=email, login=username, password=password)

            # Формируем сессии для последующего добавления в БД
            db.session.add(user)

            # Сохранение в базу данных всех сформированных сессий одним комитом
            db.session.commit()

    return render_template('base.html')


@app.route('/login', methods=['GET', 'POST'])
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
@login_required
def logout():
    logout_user()
    return redirect(url_for('/'))


# Обработчик сообщений от клиентов
@socketio.on('message')
def handle_message(msg):
    print('Message:', msg)
    # Отправляем сообщение всем подключённым клиентам
    send(msg, broadcast=True)