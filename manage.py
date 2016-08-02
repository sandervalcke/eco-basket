import os
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask_security.script import (CreateRoleCommand,
                                   AddRoleCommand, RemoveRoleCommand,
                                   ActivateUserCommand, DeactivateUserCommand)
from bread.application import app, db

app.config.from_object(os.environ['APP_SETTINGS'])

from bread.database import *

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

user_commands = Manager(usage="Manage users")
manager.add_command('user', user_commands)
user_commands.add_command('role_add', AddRoleCommand)
user_commands.add_command('role_remove', RemoveRoleCommand)
user_commands.add_command('activate', ActivateUserCommand)
user_commands.add_command('deactivate', DeactivateUserCommand)

role_commands = Manager(usage="Manage roles")
manager.add_command('role', role_commands)
role_commands.add_command('create', CreateRoleCommand)

if __name__ == '__main__':
    manager.run()
