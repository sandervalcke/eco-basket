from collections import namedtuple, defaultdict

from flask import render_template, request, flash, redirect, url_for
from flask_security import login_required, roles_required, roles_accepted, logout_user, current_user
from sqlalchemy.sql import func

from bread.application import app, db
from bread import database
from bread.security import CurrentUser, security_roles
from bread.forms import (AddOrderItemForm, CreateOrderForm, CreateItemForm,
                         CreateProducerForm, CsrfTokenForm, UpdateOrderForm)


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

    def get_role_label(role):
        if role.name == 'admin':
            return 'label-danger'
        elif role.name == 'treasurer':
            return 'label-info'
        elif role.name == 'liason':
            return 'label-warning'
        else:
            return 'label-default'

    def format_currency(currency):
        return "{:.2f}".format(currency)

    return dict(format_time=format_time,
                format_date=format_date,
                format_currency=format_currency,
                role_label=get_role_label)


@app.context_processor
def inject_variables():
    menu_items = [('/myorders', 'my_orders', 'My Orders'),
                  ('/allorders', 'all_orders', 'All Orders'),
                  ('/producers', 'producers', 'Producers')]

    if CurrentUser.has_role('admin'):
        menu_items.append(('/users', 'users', 'Users'))

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
        if producer_id is not None:
            form_kwargs['producer_id'] = producer_id
            if producer_id not in producer_items:
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
    posted_order_item_form = create_form(producer_id=request.form.get('producer_id', None))

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
                   .order_by(database.DbOrder.close_date_utc.desc()).all())
    order_items = database.DbOrderItem.query.filter(database.DbOrderItem.user_id == current_user.id).all()

    # Link customer's orders to the order lists
    class OrderData(object):
        def __init__(self, order=None, items=[], form=None, quantity=0, price=0):
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
                               key=lambda x: x.order.close_date_utc, reverse=True)
    )


@app.route('/orders/<int:id>', methods=['GET', 'POST'])
@login_required
def single_order(id):
    order = database.DbOrder.query.get(id)
    order_items = (database.DbOrderItem.query
                   .join(database.User)
                   .join(database.DbItem)
                   .filter(database.DbOrderItem.order_id==order.id)
                   .order_by(database.User.first_name, database.DbItem.name).all())
    form = CsrfTokenForm()

    if form.validate_on_submit():
        if CurrentUser.check_any_role(security_roles.admin,
                                      security_roles.treasurer):
            # If mark_payed is pressed it is in request.form, otherwise mark_unpayed
            # was pressed
            payed = 'mark_payed' in request.form

            for input_name in request.form:
                if input_name.startswith('item_'):
                    input_id = int(input_name[5:])
                    order_item = database.DbOrderItem.query.get(input_id)
                    if order_item is not None:
                        order_item.payed = payed

            db.session.commit()

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
        order_items=order_items,
        grouped_items=grouped_items,
        form=form
    )


@app.route('/orders/<int:id>/edit', methods=['GET', 'POST'])
def edit_order(id):
    order = database.DbOrder.query.get(id)

    if order.is_closed:
        flash('This is order has been closed')

    form = UpdateOrderForm()

    # The ON clause of an SQL join is evaluated BEFORE the join, the WHERE clause AFTER the
    # join. That's why we need to put the DbOrderItem filters in the ON clause, otherwise
    # we throw away item records that don't have an order attached.
    items = (db.session.query(database.DbItem.id,
                              database.DbItem.name,
                              database.DbItem.producer_id,
                              database.DbItem.price,
                              func.coalesce(database.DbOrderItem.quantity, 0).label('quantity'),
                              database.DbOrderItem.user_id,
                              database.DbOrderItem.order_id)
             .outerjoin(database.DbOrderItem,
                        (database.DbItem.id == database.DbOrderItem.item_id)
                        & (database.DbOrderItem.order_id == order.id)
                        & (database.DbOrderItem.user_id == current_user.id))
             .filter(database.DbItem.producer_id == order.producer_id)
             .all()
             )

    if form.is_submitted():
        if not order.is_closed:
            # We already flash at the top if the order is closed, not flashing again

            # Remove existing, we will save brand new ones
            (database.DbOrderItem.query
             .filter_by(order_id=order.id)
             .filter_by(user_id=current_user.id).delete())

            for quantity, item in zip(form.quantities, items):
                # The order of the quantities matches that of the order of the items
                order_item = database.DbOrderItem(order_id=order.id,
                                                  user_id=current_user.id,
                                                  item_id=item.id,
                                                  quantity=quantity.data)
                db.session.add(order_item)
            db.session.commit()
            return redirect(url_for('my_orders'))
    else:
        for item in items:
            form.quantities.append_entry(data=item.quantity)

    return render_template('order_edit.html',
                           order=order,
                           items_zip=zip(items, form.quantities),
                           form=form)


@app.route('/allorders', methods=['GET'])
@login_required
def all_orders():
    orders = database.DbOrder.query.order_by(database.DbOrder.close_date_utc.desc()).all()

    return render_template(
        'all_orders.html',
        orders=orders
    )


@app.route('/producers', methods=['GET'])
@login_required
def producers():
    producer_list = database.DbProducer.query.all()
    return render_template('producers.html',
                           producers=producer_list)


@app.route('/producers/<int:id>', methods=['GET'])
@login_required
def producerpage(id):
    producer = database.DbProducer.query.get(id)
    items = database.DbItem.query.filter_by(producer_id=id).all()
    orders = database.DbOrder.query\
                    .filter_by(producer_id=id)\
                    .order_by(database.DbOrder.close_date_utc.desc()).all()

    return render_template('producer.html',
                           producer=producer,
                           items=items,
                           orders=orders)


@app.route('/producers/<int:id>/orders/new', methods=['GET', 'POST'])
@roles_accepted('admin', 'liaison')
def producer_new_order(id):
    producer = database.DbProducer.query.get(id)
    items = database.DbItem.query.filter_by(producer_id=id).all()

    form = CreateOrderForm()

    if form.validate_on_submit():
        order = database.DbOrder(name=form.name.data,
                                 producer=producer,
                                 delivery_date_utc=form.delivery_date.data,
                                 close_date_utc=form.closed_date.data)
        db.session.add(order)

        db.session.commit()
        return redirect(url_for('producerpage', id=id))

    return render_template('create_order.html',
                           producer=producer,
                           items=items,
                           form=form)


@app.route('/producers/<int:id>/items/new', methods=['GET', 'POST'])
@roles_accepted('admin', 'liaison')
def producer_new_item(id):
    producer = database.DbProducer.query.get(id)
    form = CreateItemForm()

    if form.validate_on_submit():
        item = database.DbItem(name=form.name.data,
                               description=form.description.data,
                               price=form.price.data,
                               producer=producer)
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('producerpage', id=id))

    return render_template('item_create.html',
                           form=form,
                           producer=producer)


@app.route('/producers/new', methods=['GET', 'POST'])
@roles_accepted('admin', 'liaison')
def producer_new():
    form = CreateProducerForm()

    if form.validate_on_submit():
        producer = database.DbProducer(name=form.name.data,
                                       description=form.description.data)
        db.session.add(producer)
        db.session.commit()
        return redirect(url_for('producers'))

    return render_template('producer_create.html',
                           form=form)


@app.route('/users', methods=['GET'])
@roles_required('admin')
def users():
    users = database.User.query.all()

    return render_template('users.html',
                           users=users)


# @app.route('/test')
# def test():
#     return render_template('test.html')


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