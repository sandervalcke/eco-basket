from flask_wtf import Form
from wtforms import SelectField, IntegerField, HiddenField, validators
# BooleanField, TextField, PasswordField, validators


class AddOrderItemForm(Form):
    # Set the choices after instantiating. Is a list of id-name tuples.
    order_id = HiddenField('order_id')
    item = SelectField('Item')
    quantity = IntegerField('Quantity', (validators.NumberRange(min=1),))
