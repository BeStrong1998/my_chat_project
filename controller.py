import string
import random

from flask import render_template, request, redirect, url_for, session
from flask_login import logout_user, login_required, login_user, current_user
from flask_socketio import send

from mail import send_email
from app import app, db, socketio
from business_logic.check_fata import check_auth_data
from models import User, EmailConfirm, Message


@app.route('/email-confirm/<code>')
# Функция для подтверждения email
def email_confirm(code):
    # Проверяем, существует ли подтверждение с таким кодом в БД
    user_confirm = EmailConfirm.query.filter_by(code=code).first()
    # Если подтверждение существует, то удаляем его из БД
    # и меняем статус email_confirm у пользователя в БД
    if user_confirm:
        # Ищем пользователя в БД по логину,
        # соответствующему логину в подтверждении
        user = User.query.filter_by(login=user_confirm.login).first()
        # Если пользователь найден, то меняем его статус email_confirm на True
        user.email_confirm = True
        # Добавляем пользователя в БД
        db.session.add(user)
        # Удаляем пользователя из БД
        db.session.delete(user_confirm)
        # Сохраняем изменения в БД
        db.session.commit()
    # Отправляем подтверждение на указанный email
    return redirect(url_for('register'))


@app.route('/', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
# Функция регистрации нового пользователя
def register():
    # Если это POST-запрос, значит была нажата кнопка "Регистрация"
    if request.method == 'POST':
        # Получаем данные из формы регистрации
        email = request.form.get('email')
        username = request.form.get('login')
        password = request.form.get('password')
        print(email, username, password)

        # Проверяем корректность введенных данных
        if check_auth_data(username, password):
            # Создаем нового пользователя
            user = User(email=email, login=username, password=password)
            # Создаем код подтверждения email, состоящий
            # из 32 символов (латинских букв и цифр)
            code = ''.join(
                [random.choice(string.ascii_letters + string.digits) for i in
                 range(32)])
            # Создаем новую запись в таблице EmailConfirm
            # с указанным кодом и логином
            user_confirm = EmailConfirm(login=username, code=code)
            # print(f'Успешная регистрация! {user.email}, {user.password}')

            # Формируем сессии для последующего добавления в БД
            db.session.add(user)
            # Сохранение в базу данных всех сформированных сессий одним комитом
            db.session.add(user_confirm)
            # Сохранение в базу данных всех сформированных сессий одним комитом
            db.session.commit()

            # Отправляем письмо c ссылкой для подтверждения почты
            message = (f'Ссылка для подтверждения '
                       f'почты: http://127.0.0.1:5000/email-confirm/{code}')
            # Отправляем письмо c ссылкой на сервер
            send_email(message, email, 'Подтверждение почты')
            print(f'Успешная регистрация! {user.email}, {user.password}')
        else:
            print('Неверные данные при регистрации!')

    return render_template('base.html')


@app.route('/login', methods=['POST'])
# Функция авторизации пользователя
def login():
    # Проверка наличия введённых данных авторизации
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Чтение данных
        user = User.query.filter_by(email=email, password=password).first()

        # Проверка наличия пользователя в БД и наличие соответствующих паролей
        if user and user.email_confirm:
            print(f'Успешная авторизация! {user.email}, {user.password}')
            # Выполняем логин пользователя
            login_user(user)
            # В случае успешной авторизации перенаправляем на главную страницу
            return redirect(url_for('index'))

        # Если данные неверны, выводим сообщение "Ошибка авторизации"
        print('Ошибка авторизации!')
        # Если данные неверны, перенаправляем на страницу регистрации
        return redirect(url_for('register'))


# Обработчик главной страницы, показывает список всех пользователей
# и возвращает страницу с формой отправки сообщений
@app.route('/index', methods=['GET', 'POST'])
@login_required
# Функция главной страницы, показывает список всех пользователей
# и возвращает страницу с формой отправки сообщений
def index():
    # Получаем идентификатор пользователя из сессии
    user_id = request.args.get('user_id')
    print(user_id)

    # Если передан идентификатор пользователя, сохраняем его в сессии
    if user_id:
        # Получаем информацию о конкретном пользователе
        session['user_id'] = user_id

    # Получение всех сообщений для отображения истории
    messages = Message.query.order_by(Message.timestamp.asc()).all()
    return render_template('index.html', messages=messages)


# Обработчик выхода из учётной записи и перенаправления на главную страницу
@app.route('/logout')
@login_required
# Функция выхода из учётной записи и перенаправления на страницу регистрации
def logout():
    # Выход из учётной записи и перенаправление на страницу регистрации
    # session.pop('login', None)
    logout_user()
    return redirect(url_for('register'))


# Обработчик сообщений от клиентов
@socketio.on('message')
# Функция обработки сообщений от клиентов
def handle_message(msg):
    # Получаем текущего пользователя с его сообщением
    print({current_user.login: {'Message': msg}})

    # Получаем текущего пользователя с его идентификатором
    user = User.query.get(int(session['user_id']))
    print({'Кому отправленно сообщение': user.login})

    # Создаем новое сообщение с текстом и отправителем из текущего пользователя
    new_message = Message(content=msg, sender=current_user.login,
                          recipient=user.login)

    # Добавляем новое сообщение в БД
    db.session.add(new_message)
    # Сохраняем изменения в БД
    db.session.commit()

    # Отправляем сообщение всем подключённым клиентам
    send(msg, broadcast=True)


@app.route('/chat/<username>')
def chat(username):
    # Получаем текущего пользователя
    now_user = current_user.login

    # Получаем пользователя с указанным именем из БД
    user = User.query.filter_by(login=username).first()
    if now_user == user:
        # Если текущий пользователь и пользователь с указанным именем
        # совпадают, перенаправляем его на страницу чата
        return redirect(url_for('index'))
    # Если пользователь существует, отправляем его страницу чата
    if user:
        return render_template('index.html')
    # Если пользователь не существует, перенаправляем его на страницу чата
    # с текущим пользователем
    else:
        return redirect(url_for('index', username=username))


@app.route('/users')
# Отображение списка всех пользователей
def list_users():
    # Получаем всех пользователей из базы данных
    users = User.query.all()  # Получаем всех пользователей из базы данных
    # Отправляем страницу со списком всех пользователей и полученными данными
    return render_template('users.html', users=users)


@app.route('/user/<id>')
# Отображение информации о конкретном пользователе
def user_info(id):
    # Получаем пользователя из базы данных по его ID
    user = User.query.get(id)
    # Отправляем страницу с информацией о пользователе и полученными данными
    return render_template('user_info.html', user=user)


# Перенаправляем на страницу регистрации при неправильной авторизации
@app.after_request
# Функция перенаправления на страницу регистрации при неправильной авторизации
def redirect_to_sign(response):
    # Если клиент авторизован, перенаправлять его не нужно
    if response.status_code == 401:
        return redirect(url_for('register'))
    return response


# Роут для тестирования
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    users = User.query.all()
    return render_template('admin.html', persons=users)
