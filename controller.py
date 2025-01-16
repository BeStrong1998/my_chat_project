import string
import random

from flask import render_template, request, redirect, url_for, session
from flask_login import logout_user, login_required, login_user, current_user
from flask_socketio import send
from flask.wrappers import Response

from mail import send_email
from app import app, db, socketio
from business_logic.check_fata import check_auth_data
from models import User, EmailConfirm, Message


@app.route('/email-confirm/<code>')
# Функция для подтверждения email
def email_confirm(code: int) -> Response or str:
    """
        Подтверждение email

        Проверяем, существует ли подтверждение в БД
        Если подтверждение существует, то удаляем его из БД
        и меняем статус email_confirm у пользователя в БД
        Если подтверждение не существует,
        то перенаправляем на страницу регистрации;

        Args:
            code: int (код подтверждения)

        Returns:
            str: шаблон страницы 500.html
            Response: перенаправление на страницу register
    """
    try:
        # Проверяем, существует ли подтверждение с таким кодом в БД
        user_confirm = EmailConfirm.query.filter_by(code=code).first()
        # Если подтверждение существует, то удаляем его из БД
        # и меняем статус email_confirm у пользователя в БД
        if user_confirm:
            # Ищем пользователя в БД по логину,
            # соответствующему логину в подтверждении
            user = User.query.filter_by(login=user_confirm.login).first()
            # Если пользователь найден, то меняем его статус email_confirm
            # на True
            user.email_confirm = True
            # Добавляем пользователя в БД
            db.session.add(user)
            # Удаляем пользователя из БД
            db.session.delete(user_confirm)
            # Сохраняем изменения в БД
            db.session.commit()
        # Отправляем подтверждение на указанный email
        return redirect(url_for('register'))
    except Exception as e:
        print(f'Ошибка при подтверждении email: {e}')
        return render_template('errors/500.html')


@app.route('/', methods=['GET', 'POST'])
@app.route('/register', methods=['GET', 'POST'])
# Функция регистрации нового пользователя
def register() -> str:
    """
       Страница регистрации

       Пользователь переходит на страницу регистрации, вводит данные,
       нажимает кнопку "Регистрация", и если данные корректны,
       регистрируется новый пользователь в БД;

       Returns:
           str: шаблон страницы 500.html или base.html
    """
    try:
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
                    [random.choice(string.ascii_letters + string.digits)
                     for i in range(32)])
                # Создаем новую запись в таблице EmailConfirm
                # с указанным кодом и логином
                user_confirm = EmailConfirm(login=username, code=code)
                # print(f'Успешная регистрация! {user.email}, {user.password}')

                # Формируем сессии для последующего добавления в БД
                db.session.add(user)
                # Сохранение в базу данных всех сформированных сессий одним
                # комитом
                db.session.add(user_confirm)
                # Сохранение в базу данных всех сформированных сессий одним
                # комитом
                db.session.commit()

                # Отправляем письмо с сылкой для подтверждения почты
                message = (f'Ссылка для подтверждения '
                           f'почты: http://127.0.0.1:5000/email-confirm/'
                           f'{code}')
                # Отправляем письмо c сылкой на сервер
                send_email(message, email, 'Подтверждение почты')
                print(f'Успешная регистрация! {user.email}, {user.password}')
            else:
                print('Неверные данные при регистрации!')

        return render_template('base.html')

    except Exception as e:
        print(f'Ошибка при регистрации: {e}')
        return render_template('errors/500.html')


@app.route('/login', methods=['POST'])
# Функция авторизации пользователя
def login() -> Response or str:
    """
       Страница авторизации

       Пользователь авторизуется, далее проверяет почту и пароль,
       если есть перенаправляет на главную страницу, если нет направляет на
       страницу регистрации;

       Returns:
           str: шаблон страницы index.html или register
    """
    try:
        # Проверка наличия введённых данных авторизации
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            # Чтение данных
            user = User.query.filter_by(email=email, password=password).first()

            # Проверка наличия пользователя в БД и наличие соответствующих
            # паролей
            if user and user.email_confirm:
                print(f'Успешная авторизация! {user.email}, {user.password}')
                # Выполняем логин пользователя
                login_user(user)
                # В случае успешной авторизации перенаправляем на главную
                # страницу
                return redirect(url_for('index'))
            # Если данные неверны, выводим сообщение "Ошибка авторизации"
            print('Ошибка авторизации!')
            # Если данные неверны, перенаправляем на страницу регистрации
            return redirect(url_for('register'))
    except Exception as e:
        print(f'Ошибка при авторизации: {e}')
        return render_template('errors/500.html')


# Обработчик главной страницы, показывает список всех пользователей
# и возвращает страницу с формой отправки сообщений
@app.route('/index', methods=['GET', 'POST'])
@login_required
# Функция главной страницы, показывает список всех пользователей
# и возвращает страницу с формой отправки сообщений
def index() -> str:
    """
       Главная страница

       Авторизованный пользователь переходит на главную страницу
       index.html. Может перейти в контакты и отправить сообщение выбранному
       авторизованному пользователю. Все отправленные сообщения остаются в
       форме на главной странице и записываются в базу данных,
       так же как и кто, кому и когда отправил сообщение;

       Returns:
           str: шаблон страницы index.html
       """
    try:
        # Получаем идентификатор пользователя из сессии
        user_id = request.args.get('user_id')
        print(user_id)

        # Если передан идентификатор пользователя, сохраняем его в сессии
        if user_id:
            # Получаем информацию о конкретном пользователе
            session['user_id'] = user_id

        # Получение всех сообщений для отображения истории
        messages = Message.query.order_by(Message.timestamp.asc()).all()
        return render_template('index.html',
                               messages=messages)
    except Exception as e:
        print(f'Ошибка при получении и отображении сообщений: {e}')
        return render_template('errors/500.html')


# Обработчик выхода из учётной записи и перенаправления на главную страницу
@app.route('/logout')
@login_required
# Функция выхода из учётной записи и перенаправления на страницу регистрации
def logout() -> Response or str:
    """
       Разлогиниться

       Выход из учётной записи и перенаправление на страницу регистрации;

       Returns:
           str: шаблон страницы index.html
           Response: вызывает функцию register
   """
    try:
        # Выход из учётной записи и перенаправление на страницу регистрации
        logout_user()
        return redirect(url_for('register'))
    except Exception as e:
        print(f'Ошибка при выходе из учётной записи: {e}')
        return render_template('errors/500.html')


# Обработчик сообщений от клиентов
@socketio.on('message')
# Функция обработки сообщений от клиентов
def handle_message(msg: str) -> None or str:
    """
        Обработчик сообщений

        Получает текущего пользователя с его сообщением.
        Создаёт новое сообщение с текстом и отправителем из текущего
        пользователя. Сохраняет сообщение в БД. Отправляет сообщение всем
        подключённым клиентам.

        Args:
            msg: str (сообщение)

        Returns:
            str: шаблон страницы index.html
    """
    try:
        # Получаем текущего пользователя с его сообщением
        print({current_user.login: {'Message': msg}})

        # Получаем текущего пользователя с его идентификатором
        user = User.query.get(int(session['user_id']))
        print({'Кому отправлено сообщение': user.login})

        # Создаем новое сообщение с текстом и отправителем из текущего
        # пользователя
        new_message = Message(content=msg, sender=current_user.login,
                              recipient=user.login)

        # Добавляем новое сообщение в БД
        db.session.add(new_message)
        # Сохраняем изменения в БД
        db.session.commit()

        # Отправляем сообщение всем подключённым клиентам
        send(msg, broadcast=True)
    except Exception as e:
        print(f'Ошибка при обработке сообщения: {e}')
        return render_template('errors/404.html')


@app.route('/chat/<username>')
def chat(username: str) -> Response or str:
    """
        Переход на страницу пользователя

        Получает страницу выбранного авторизованного пользователя

        Args:
            username: str (сообщение)

        Returns:
            str: шаблон страницы index.html
    """
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
def list_users() -> str:
    """
        Получение пользователей

        Получение всех авторизованных пользователей из БД;

        Returns:
            str: шаблон страницы users.html
    """
    # Получаем всех пользователей из базы данных
    users = User.query.all()  # Получаем всех пользователей из базы данных
    # Отправляем страницу со списком всех пользователей и полученными данными
    return render_template('users.html', users=users)


# Перенаправляем на страницу регистрации при неправильной авторизации
@app.after_request
# Функция перенаправления на страницу регистрации при неправильной авторизации
def redirect_to_sign(response: Response) -> Response:
    """
        Обработка ошибки 401

        Returns:
            Response: вызывает функцию register
    """
    # Если клиент авторизован, перенаправлять его не нужно
    if response.status_code == 401:
        return redirect(url_for('register'))
    return response


# Админка
@app.route('/admin', methods=['GET', 'POST'])
def admin() -> str:
    """
        Админ панель

        Админ панель со всеми зарегистрированными пользователями;

        Returns:
            str: перенаправляем на admin панель
    """
    users = User.query.all()
    return render_template('admin.html', persons=users)