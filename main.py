from app import socketio

from controller import app


if __name__ == '__main__':
    # Запуск сервера с поддержкой вебсокетов с информацией об ошибках если имеются
    socketio.run(app, debug=True)