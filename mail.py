import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import EMAIL_LOGIN, EMAIL_PASSWORD


# Функция создания сообщения с указанными адресатом и темой
def get_msg(to: str, subject: str):
    # Создаем объект MIMEMultipart для создания сообщения с разными частями
    msg = MIMEMultipart()

    # Задаем адресат адресата
    msg['From'] = EMAIL_LOGIN
    # Задаем получателя
    msg['To'] = to
    # Задаем тему сообщения
    msg['Subject'] = subject

    # Возвращаем созданное сообщение в виде MIMEMultipart
    # для дальнейшего использования или отправки
    return msg


# Функция отправки сообщения по указанному адресу и теме
def send_email(message: str, to: str, subject: str):
    # Вводим текст сообщения с клавиатуры (необязательно,
    # но удобно для проверки работы функции)
    # message = input('Введите сообщение: ')

    # Создаем сообщение с указанными адресатом и темой
    msg = get_msg(to, subject)
    # Добавляем текстовую часть сообщения во вложение
    msg.attach(MIMEText(message, 'plain'))
    # Отправляем сообщение на указанный адрес и порт
    server = smtplib.SMTP('smtp.mail.ru', 25)
    # Включаем режим отладки - если отчет не нужен,
    # строку можно закомментировать
    server.starttls()
    # Получаем доступ и отправляем сообщение
    server.login(EMAIL_LOGIN, EMAIL_PASSWORD)

    # Отправляем сообщение
    server.sendmail(EMAIL_LOGIN, msg['To'], msg.as_string())
    # Выходим из сервера SMTP (не обязательно,
    # но лучше всегда завершать работу)
    server.quit()
