import os
import sys
import logging


def get_secret_key(filepath='.secret_key'):
    """If the file does not exist, print instructions
    to create it from a shell with a random key,
    then exit.

    """
    filename = os.path.join(filepath)
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except IOError:
        print('Error: No secret key. Create it with:')
        print('head -c 64 /dev/urandom >', filename)
        sys.exit(1)


def get_db_connection_string(prefix):
    """
    For all database types:
    DBTYPE - mssql/postgresql
    USER
    PWD
    SERVER

    MSSQL:

    Postgresql
    DATABASE

    :param prefix: Prefix for the environment variables, e.g. prefix
     MMP_TEST will give MMP_TEST_USER, ...
    :return: The full connection string
    """
    def get_envvar_key(name):
        return '{}_{}'.format(prefix, name)

    def get_envvar(name, throw=True):
        """
        Throws if throw is true. Otherwise returns None in case of an error.
        """
        envvar = os.environ.get(get_envvar_key(name))
        if throw and not envvar:
            raise Exception("Environment variable '{}' not set".format(get_envvar_key(name)))
        return envvar

    def get_mssql_connection():
        # adding charset=utf8 causes problems with 'manage.py db migrate' of alembic
        return "{}://{}:{}@{}".format(
            "mssql+pymssql",
            get_envvar('USER'),
            get_envvar('PWD'),
            get_envvar('SERVER'))

    def get_postgresql_connection():
        return "postgresql://{}:{}@{}/{}".format(
            get_envvar('USER'),
            get_envvar('PWD'),
            get_envvar('SERVER'),
            get_envvar('DATABASE'))

    dbtypes = dict(
        mssql      = get_mssql_connection,
        postgresql = get_postgresql_connection
    )

    dbtype = get_envvar('DBTYPE', throw=False)

    if not dbtype in dbtypes:
        raise Exception("Unknown database type '{}'. Please set '{}'. Possible values: {}"
                        .format(dbtype, get_envvar_key('DBTYPE'), ", ".join(dbtypes.keys())))

    return dbtypes[dbtype]()


class Config(object):
    """
    Derived classes must be in their own files: variables defined at class level are
    evaluated at import -> environment variables for that config must exist, even if we
    are not using it
    """
    DEBUG = False

#    TESTING = False
    # Use the SQLAlchemy event system instead of the flask_sqlalchemy event system
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    C_SQLALCHEMY_ENGINE_LOG_LEVEL = logging.ERROR

    # Used for encrypting cookies
    SECRET_KEY = get_secret_key('.secret_key')

    # Security options
    SECURITY_PASSWORD_HASH = 'bcrypt'
    # In seconds
    SECURITY_TOKEN_MAX_AGE = 3600 * 8
