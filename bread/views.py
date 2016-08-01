from collections import namedtuple, defaultdict

from flask import render_template, request, flash, redirect, url_for
from flask.ext.security import login_required, roles_required, logout_user, current_user
from sqlalchemy.sql import func

from bread.application import app, db
from bread import database
from bread.forms import AddOrderItemForm


@app.context_processor
def utilty_processor():
    """
    Provide helper functions that can be used in the jinja templates
    """
    def format_time(time):
        if time:
            return time.strftime("%d-%m-%Y %H:%M:%S")
        else:
            return ""

    def format_date(time):
        if time:
            return time.strftime("%d-%m-%Y")
        else:
            return ""

    def format_currency(currency):
        return "{:.1f}".format(currency)

    return dict(format_time=format_time,
                format_date=format_date,
                format_currency=format_currency)


@app.context_processor
def inject_variables():
    menu_items = [('/myorders', 'my_orders', 'My Orders'),
                  ('/allorders', 'all_orders', 'All Orders')]

    if current_user.is_authenticated:
        menu_items.append(('/logout', 'logout', 'Logout'))
    else:
        menu_items.append(('/login', 'login', 'Login'))

    return dict(menu_items=menu_items)


@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/myorders', methods=['GET', 'POST'])
@login_required
def my_orders():
    def create_form(producer_id=None, order_id=None, mint=False):
        """
        :param mint If true, the form does not use existing request POST form data, if it exists.
         if False then the form will contain the request POST data.
        """
        form_kwargs = {}
        if order_id is not None:
            form_kwargs['order_id'] = order_id
        if mint:
            form_kwargs['formdata'] = None

        # Update the cache
        if producer_id is not None and producer_id not in producer_items:
            producer_items[producer_id] = database.DbItem.query.filter_by(producer_id=producer_id).all()

        order_item_form = AddOrderItemForm(**form_kwargs)
        order_item_form.item.choices = [(str(item.id), "{} (€ {})".format(item.name, item.price))
                                        for item in producer_items[producer_id]]
        return order_item_form

    def get_form(order_id, producer_id=None):
        """
        Create a mint form if the order_id is not that of the POSTed form, otherwise gives
        the existing and validated (-> contains validation errors) form.
        """
        if 'order_id' not in request.form or order_id != int(request.form['order_id']):
            return create_form(order_id=order_id, producer_id=producer_id, mint=True)
        else:
            return posted_order_item_form

    # Cache the list of items of a producer. Key: producer ID. Value: items
    producer_items = defaultdict(list)
    posted_order_item_form = create_form()

    if posted_order_item_form.is_submitted():
        if 'add_item' in request.form:
            # Have add_item -> form submitted to try to add an item.
            if posted_order_item_form.validate_on_submit():
                # TODO if already item like this ordered: add to existing order?
                order_item = database.DbOrderItem(
                    order_id=int(posted_order_item_form.order_id.data),
                    user_id=current_user.id,
                    item_id=int(posted_order_item_form.item.data),
                    quantity=posted_order_item_form.quantity.data
                )

                db.session.add(order_item)
                db.session.commit()
        else:
            # Request to delete an item from an order. Find out which one.
            for form_item in request.form:
                if form_item.startswith('delete_item_'):
                    to_remove_id = int(form_item[12:])
                    order_item = database.DbOrderItem.query.get(to_remove_id)
                    # Must get info before deleting object
                    flash_message = 'Removed {} from order {}'.format(order_item.item.name, order_item.order.name)
                    db.session.delete(order_item)
                    db.session.commit()
                    flash(flash_message)

    orders_list = (database.DbOrder.query
                   .order_by(database.DbOrder.delivery_date_utc.desc()).all())
    order_items = database.DbOrderItem.query.filter(database.DbOrderItem.user_id == current_user.id).all()

    # Link customer's orders to the order lists
    class OrderData(object):
        def __init__(self, order=None, items = [], form=None, quantity=0, price=0):
            self.order = order
            self.form = form
            self.items = items
            self.quantity = quantity
            self.price = price

    order_data = {order.id: OrderData(order=order, items=[],
                                      form=get_form(producer_id=order.producer_id, order_id=order.id))
                                      for order in orders_list}

    for item in order_items:
        order_data[item.order_id].items.append(item)

    # Add some computed stuff, must do because items for this user only
    for _, data in order_data.items():
        data.quantity = database.DbOrder.compute_quantity(data.items)
        data.price = database.DbOrder.compute_price(data.items)

    return render_template(
        'my_orders.html',
        order_data_list=sorted(order_data.values(),
                               key=lambda x: x.order.delivery_date_utc, reverse=True)
    )


@app.route('/orders/<int:id>', methods=['GET'])
@login_required
def single_order(id):
    order = database.DbOrder.query.get(id)

    if order is None:
        flash('Order {} not found'.format(id))
        # Dummy empty object for view code
        order = database.DbOrder()
        grouped_items = []
    else:
        # DbOrderItem first in select to make joins work implicitly
        # select from DB instead of doing the sum on the order.order_items: choice
        # to put load on DB, not on app.
        grouped_items = (db.session.query(func.sum(database.DbOrderItem.quantity).label('quantity'),
                                          database.DbItem.name)
                         .join(database.DbOrder).filter(database.DbOrder.id == order.id)
                         .join(database.DbItem)
                         .group_by(database.DbItem.name)
                         .order_by(database.DbItem.name)
                         .all()
                         )

    return render_template(
        'order.html',
        order=order,
        grouped_items=grouped_items
    )


@app.route('/allorders', methods=['GET'])
@login_required
def all_orders():
    orders = database.DbOrder.query.order_by(database.DbOrder.delivery_date_utc.desc()).all()

    return render_template(
        'all_orders.html',
        orders=orders
    )


@app.route('/test')
def test():
    return render_template('test.html')


# @app.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('index'))
#
#
# { % if current_user.is_authenticated %}
# { % ('/logout', 'logout', 'Logout') %}
# { % else %}
# { % ('/login', 'login', 'Login') %}
# { % endif %}