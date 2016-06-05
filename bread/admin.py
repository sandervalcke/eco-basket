from flask.ext import admin
from flask.ext.security import current_user, login_required
from flask_admin.contrib.sqla import ModelView
from flask.ext.admin import expose

import bread.database as database
from bread.application import app, db


# See https://github.com/mrjoes/flask-admin/blob/master/examples/auth/app.py
class MyAdminIndexView(admin.AdminIndexView):
    """
    Custom admin class to force a user to be authenticated.

    TODO force admin role
    """
    @expose('/')
    @login_required
    def index(self):
        return super(MyAdminIndexView, self).index()


admin = admin.Admin(app,
                    name='Bread admin',
                    index_view=MyAdminIndexView(),
                    template_mode='bootstrap3')


class ChildView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False


admin.add_view(ChildView(database.User, db.session))
admin.add_view(ChildView(database.Role, db.session))
admin.add_view(ChildView(database.DbProducer, db.session))
admin.add_view(ChildView(database.DbOrder, db.session))
admin.add_view(ChildView(database.DbItem, db.session))
admin.add_view(ChildView(database.DbOrderItem, db.session))
