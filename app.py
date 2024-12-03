from flask_socketio import SocketIO

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import DATABASE_URL

app = Flask(__name__)

# Настройка базы данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
db = SQLAlchemy(app)

socketio = SocketIO(app)


# # Обработчик сообщений от клиентов
# @socketio.on('message')
# def handle_message(msg):
#     print('Message:', msg)
#     # Отправляем сообщение всем подключённым клиентам
#     send(msg, broadcast=True)
