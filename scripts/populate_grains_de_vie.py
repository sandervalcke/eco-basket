from bread import database
from bread.application import db
from datetime import datetime, timedelta


producer_name = 'Grains de Vie'

producer = database.DbProducer.query.filter_by(name=producer_name).first()
if producer is None:
    producer = database.DbProducer(name=producer_name)

    db.session.add(producer)

    db.session.add(database.DbItem(name='Froment nature 500g', price=2.20, producer=producer))
    db.session.add(database.DbItem(name='Froment nature 800g', price=3.20, producer=producer))
    db.session.add(database.DbItem(name='Froment bis multigraines 500g', price=2.50, producer=producer))
    db.session.add(database.DbItem(name='Froment bis multrigraines 800g', price=3.70, producer=producer))
    db.session.add(database.DbItem(name='Froment bis noix 500g', price=2.50, producer=producer))
    db.session.add(database.DbItem(name='Froment bis noix 800g', price=3.70, producer=producer))
    db.session.add(database.DbItem(name='Seigle bis 500g', price=2.20, producer=producer))
    db.session.add(database.DbItem(name='Seigle bis 800g', price=3.20, producer=producer))
    db.session.add(database.DbItem(name='Seigle noix-raisins 500g', price=2.50, producer=producer))
    db.session.add(database.DbItem(name='Seigle noix-raisins 800g', price=3.70, producer=producer))
    db.session.add(database.DbItem(name='Epeautre 500g', price=3.00, producer=producer))
    db.session.add(database.DbItem(name='Epeautre 800g', price=4.00, producer=producer))

database.DbOrderItem.query.delete()
database.DbOrder.query.delete()

start_date = datetime(year=2016, month=5, day=11, hour=18, minute=30)
for i in range(6):
    order_date = start_date + timedelta(days=i*14)
    closed_date = order_date - timedelta(days=1, hours=1, minutes=30)
    print("adding order {}".format(order_date))
    order = database.DbOrder(name="Gaspipa {}".format(i+1),
                             delivery_date_utc=order_date,
                             close_date_utc=closed_date,
                             producer=producer)

    db.session.add(order)

db.session.commit()
