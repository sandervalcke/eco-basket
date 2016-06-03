from flask.ext.security import Security, SQLAlchemyUserDatastore
from bread.extentions import db
from bread.database import User, Role
from flask_wtf.csrf import CsrfProtect, generate_csrf


def get_csrf_token():
    return generate_csrf()


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security()

csrf = CsrfProtect()
