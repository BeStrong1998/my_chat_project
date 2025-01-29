"""Модуль с обработчиками шаблонов исключений """

from flask import render_template

from controller import app


@app.errorhandler(404)
def page_not_found(e):
    """
    Обработка ошибкок с кодом 404 (Not Found)

    Данная функция запускается при возникновении ошибки 404 и перенаправляет
    пользователя на страницу 404.html;

    Returns:
        str: шаблон страницы 404.html
    """
    return render_template('errors/404.html')


@app.errorhandler(500)
def page_not_found(e):
    """
    Обработка ошибкок с кодом 500 (Internal Server Error)

    Данная функция запускается при возникновении ошибки 500 - внутренняя ошибка
    сервера, и перенаправляет пользователя на страницу 500.html;

    Returns:
        str: шаблон страницы 500.html
    """
    return render_template('errors/500.html')
