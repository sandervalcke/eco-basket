import sys
import os
sys.path.append(os.path.join(sys.path[0], '..', '..'))

from bread import database
from bread.application import db


def mark_all_payed():
    print("Marking all order items payed")
    for order_item in database.DbOrderItem.query.all():
        order_item.payed = True
    print("Done!")
    return


if __name__ == '__main__':
    mark_all_payed()
    db.session.commit()
