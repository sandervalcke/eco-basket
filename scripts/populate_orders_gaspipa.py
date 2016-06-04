import csv
from bread import database
from bread.application import db
from datetime import datetime, timedelta


input_file = r"/home/adversus/Desktop/brood"

orders = database.DbOrder.query.order_by(database.DbOrder.delivery_date_utc).all()

with open(input_file) as f:
    reader = csv.DictReader(f, delimiter='\t',
                            fieldnames=('name',
                                        'bread1', 'quant1', 'total1',
                                        'bread2', 'quant2', 'total2',
                                        'bread3', 'quant3', 'total3',
                                        'bread4', 'quant4', 'total4',
                                        'bread5', 'quant5', 'total5',
                                        'bread6', 'quant6', 'total6'))
    for index, row in enumerate(reader):
        name = row['name']
        if name:
            user = database.User.query.filter_by(first_name=name).first()
            if not user:
                print("creating user {}".format(name))
                user = database.User(first_name=name,
                                     last_name='',
                                     email=name.replace(' ', '_'),
                                     password='test024',
                                     active=True)
                db.session.add(user)

            for index in range(1, 7):
                bread_name = 'bread' + str(index)
                quant_name = 'quant' + str(index)
                total_name = 'total' + str(index)
                order = orders[index-1]

                if not row[quant_name]:
                    continue

                try:
                    quantity = int(row[quant_name])
                except ValueError:
                    print('Bad quantity: {}'.format(row[quant_name]))
                    raise

                item = database.DbItem.query.filter_by(name=row[bread_name]).first()
                if not item:
                    print('{} not found'.format(row[bread_name]))

                order_item = database.DbOrderItem(
                    order=order, user=user, item=item, quantity=quantity
                )

                db.session.add(order_item)

            print(row['name'])

    db.session.commit()