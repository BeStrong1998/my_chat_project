 # Функция для проверки валидности логина и пароля
def check_auth_data(login: str, password: str):
    # Проверяем длину логина и пароля
    if not (3 < len(login) < 20) or not (4 < len(password) < 32):
        return False
    return True