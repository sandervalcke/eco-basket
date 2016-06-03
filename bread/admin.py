from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

import bread.database as database
from bread.application import app, db


admin = Admin(app, name='Bread admin', template_mode='bootstrap3')


class ChildView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False


admin.add_view(ChildView(database.User, db.session))
admin.add_view(ChildView(database.Role, db.session))
admin.add_view(ChildView(database.DbProducer, db.session))
admin.add_view(ChildView(database.DbOrder, db.session))
admin.add_view(ChildView(database.DbItem, db.session))
admin.add_view(ChildView(database.DbOrderItem, db.session))
