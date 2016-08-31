from flask_wtf import Form
from wtforms import (SelectField, IntegerField, HiddenField, validators, DateField, SubmitField,
                     StringField, FloatField, TextAreaField, FieldList)
# BooleanField, TextField, PasswordField, validators


class CsrfTokenForm(Form):
    """
    Use this to get easy handling of csrf
    """
    pass


class AddOrderItemForm(Form):
    # Set the choices after instantiating. Is a list of id-name tuples.
    order_id = HiddenField('order_id')
    producer_id = HiddenField('producer_id')
    item = SelectField('Item')
    quantity = IntegerField('Quantity', (validators.NumberRange(min=1),))


class CreateOrderForm(Form):
    name = StringField('Name:')
    closed_date = DateField('Closed date:', format='%d/%m/%Y')
    delivery_date = DateField('Delivery date:', (validators.optional(),), format='%d/%m/%Y')
    submit = SubmitField('Save')


class CreateItemForm(Form):
    name = StringField('Name:')
    description = TextAreaField('Description:')
    price = FloatField('Price:')
    submit = SubmitField('Save')


class CreateProducerForm(Form):
    name = StringField('Name:')
    description = TextAreaField('Description:')
    submit = SubmitField('Save')


class UpdateOrderForm(Form):
    submit = SubmitField('Save')
    quantities = FieldList(IntegerField('Quantity', (validators.NumberRange(min=0),)))
