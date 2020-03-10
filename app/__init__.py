from flask import Flask
from waitress import serve


# Создаем экземпляр класса Flask
app = Flask(__name__, static_url_path='')


# Загружаем блок с маршрутизацией
# Экземпляр приложения Flask называется app и входит в пакет app
from app import routes


# Запуск production server с помощью waitress
serve(app, host='0.0.0.0', port=8080)