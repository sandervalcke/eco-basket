from bread.application import db
from bread import database


database.DbOrderItem.query.delete()

db.session.commit()
