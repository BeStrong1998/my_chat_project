from app import socketio

# from controller import app
from errors import app

if __name__ == '__main__':
    # Запуск сервера SocketIO с использованием приложения Flask
    socketio.run(app)
