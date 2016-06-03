from sqlalchemy import Table, Column

from alembic import op
import sqlalchemy as sa


def create_non_null_column_with_values(table_name, column_name, column_type, default_value):
    """
    Create a new column in the database. The column is non-nullable and does not have
    a default value. Because creating such a column is not directly possible (existing
    records must be assigned a value), we create the column nullable, then assign
    default_value to existing records and then set the column to non-nullable.

    :param table_name: e.g. 'users'
    :param column_name:
    :param column_type: e.g. sa.String(length=80)
    :param default_value:
    :return:
    """
    table = Table(table_name, sa.MetaData(), Column(column_name))

    op.add_column(table_name, sa.Column(column_name, column_type, nullable=True))

    argdict = {}
    argdict[column_name] = default_value
    op.execute(table.update().values(**argdict))

    op.alter_column(table_name, column_name, existing_type=column_type,
                    nullable=False)


def make_non_nullable(table_name, column_name, existing_type, default_value):
    """
    First set all the values in a column to a default value, then make it non-nullable
    """
    table = Table(table_name, sa.MetaData(), Column(column_name))

    values = {column_name: default_value}
    op.execute(table.update().values(**values))
    
    op.alter_column(table_name, column_name,
               existing_type=existing_type,nullable=False)
