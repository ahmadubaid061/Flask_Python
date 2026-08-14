import os
from dotenv import load_dotenv

load_dotenv()  # reads .env once, here — not in __init__.py

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False