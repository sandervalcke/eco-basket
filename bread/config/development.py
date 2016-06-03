import os
import logging
from bread.config.base import Config, get_db_connection_string


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    TESTING = False

    SECURITY_PASSWORD_SALT = os.environ['BREAD_TEST_SECURITY_SALT']

    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + '/home/adversus/Programming/bread/bread.db'
    SQLALCHEMY_DATABASE_URI = get_db_connection_string('BREAD_TEST')

    C_SQLALCHEMY_ENGINE_LOG_LEVEL = logging.INFO
