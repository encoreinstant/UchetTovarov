class Config:
    SECRET_KEY = '1234'  # В реальном проекте лучше использовать переменные окружения
    DB_NAME = 'flaskdb'
    DB_USER = 'zaobogdan'
    DB_PASSWORD = '10102005526'
    DB_HOST = 'localhost'
    #DB_HOST = 'amvera-krxxj-cnpg-flaskdb-rw'
    DB_PORT = '5432'

import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')


