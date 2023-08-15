import os
import models


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in \
        ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    BOT_MAIL_SUBJECT_PREFIX = '[LearnSociety]'
    BOT_MAIL_SENDER = 'LearnSociety Admin <LearnSociety@noreply.com>'
    BOT_ADMIN = os.environ.get('BOT_ADMIN')
    LANGUAGES = ['en', 'es', 'ru', 'zh', 'fr', 'de', 'it', 'ja', 'ko', 'uk']
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app): pass


"""
    The following code is used to set the database URI for the application.
    The URI is set based on the environment variable DATABASE_URL. If the
    environment variable is not set, then the URI is set to a local SQLite
    database.
"""


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('STORAGE_TYPE') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    Redis_URL = os.environ.get('STORAGE_TYPE2') or \
        'redis://localhost:6379/0'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite://'
    Redis_URL = os.environ.get('STORAGE_TYPE2') or \
        'redis://localhost:6379/0'
    os.environ["MYSQL_TEST_DB"] = "BotSchedule_test_DB"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
