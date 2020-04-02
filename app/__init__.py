from flask import Flask, jsonify
from waitress import serve

import logging
import traceback

# Создаем экземпляр класса Flask
app = Flask(__name__, static_url_path='')

# Create logger
logger = logging.getLogger()

# Create exception route
@app.errorhandler(code_or_exception=500)
def handle_http_exception(error):
    error_dict = {
        'code': error.code,
        'description': error.description,
        'stack_trace': traceback.format_exc()
    }
    log_msg = f"HTTPException {error_dict['code']}, Description: {error_dict['description']}, Stack trace: {error_dict['stack_trace']}"
    logger.log(msg=log_msg, level=40)
    if error.code == 500:
        response = jsonify(error.name + '. ' + str(error.original_exception))
    else:
        response = jsonify(error_dict)
    return response

# Загружаем блок с маршрутизацией
# Экземпляр приложения Flask называется app и входит в пакет app
from app import routes


# Запуск production server с помощью waitress
serve(app, host='0.0.0.0', port=8080)