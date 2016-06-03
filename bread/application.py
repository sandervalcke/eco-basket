import os
from flask import Flask

from bread.extentions import db
from bread.security import csrf, user_datastore, security


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])


def setup_application():
    db.init_app(app)
    db.app = app

    security_state = security.init_app(
        app,
        datastore=user_datastore,
        # register_blueprint=False
    )
    # security_state.unauthorized_handler(unauthorized_callback)
    # security_state.login_manager.unauthorized_handler(user_not_logged_in_callback)

    csrf.init_app(app)

setup_application()
