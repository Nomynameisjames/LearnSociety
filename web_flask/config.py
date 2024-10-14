import os, secrets
import models
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or secrets.token_hex(70)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_SSL = os.getenv("USE_SSL")
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER =  os.getenv("MAIL_USERNAME")
    MAIL_DEBUG = False
    
    BOT_MAIL_SUBJECT_PREFIX = '[LearnSociety]'
    BOT_MAIL_SENDER = 'LearnSociety Admin <LearnSociety@noreply.com>'
    BOT_ADMIN = os.getenv('BOT_ADMIN')
    LANGUAGES = ['en', 'es', 'ru', 'zh', 'fr', 'de', 'it', 'ja', 'ko', 'uk']
    SQLALCHEMY_TRACK_MODIFICATIONS = False


"""
    The following code is used to set the database URI for the application.
    The URI is set based on the environment variable DATABASE_URL. If the
    environment variable is not set, then the URI is set to a local SQLite
    database.
"""


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('STORAGE_TYPE') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    Redis_URL = os.getenv('STORAGE_TYPE2') or \
        'redis://localhost:6379/0'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL') or \
        'sqlite://'
    Redis_URL = os.getenv('STORAGE_TYPE2') or \
        'redis://localhost:6379/0'
    os.environ["MYSQL_TEST_DB"] = "BotSchedule_test_DB"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
