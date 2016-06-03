import os
import logging

from bread.config.base import Config, get_db_connection_string


class HerokuConfig(Config):
    DEVELOPMENT = False
    DEBUG = False
    TESTING = False

    SECURITY_PASSWORD_SALT = os.environ['BREAD_SECURITY_SALT']

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    C_SQLALCHEMY_ENGINE_LOG_LEVEL = logging.WARNING
