## my_chat_project
Платформа для общения

Ставим зависимости
```
pip3 install -r requirements.txt
```

Нужно создать файл config
```

DATABASE_URI = 'sqlite:///твоя БД'

# Почтовый адрес для проверки email
EMAIL_LOGIN = 'твоя почта'

# Пароль для почты (любой придумать самому)
EMAIL_PASSWORD = 'твои данные'

# Секретный ключ для защиты сессий
SECRET_KEY = "твои данные"
```

Запускаем проект командой
```
python3 main.py
```


