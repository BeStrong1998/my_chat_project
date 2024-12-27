from flask_socketio import SocketIO
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from config import DATABASE_URL, SECRET_KEY, SQLALCHEMY_TRACK_MODIFICATIONS

# Создание экземпляра приложения Flask и настройка его основных параметров
# и подключения к базе данных
app = Flask(__name__)

# Настройка базы данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

# Задание секретного ключа для защиты сессий
app.config['SECRET_KEY'] = SECRET_KEY

# Настройка поддержки вебсокетов
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

# Инициализация базы данных
db = SQLAlchemy(app)

# Инициализация менеджера логина
manager = LoginManager(app)

# Загрузка и настройка модулей
socketio = SocketIO(app)
