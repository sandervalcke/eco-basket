from collections import namedtuple
from flask_security import Security, SQLAlchemyUserDatastore
from flask_principal import RoleNeed, Permission
from bread.extentions import db
from bread.database import User, Role
from flask_wtf.csrf import CsrfProtect, generate_csrf
from flask_security import utils


def get_csrf_token():
    return generate_csrf()


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security()

csrf = CsrfProtect()


security_roles = namedtuple('Roles', ['admin', 'liaison', 'treasurer'])(
    'admin', 'liaison', 'treasurer'
)

class CurrentUser(object):
    @staticmethod
    def has_role(role):
        return CurrentUser.has_all_roles((role,))

    @staticmethod
    def has_all_roles(roles):
        # Uses g.identity
        perms = [Permission(RoleNeed(role)) for role in roles]
        for perm in perms:
            if not perm.can():
                return False
        return True

    @staticmethod
    def has_any_role_permission(*roles):
        # this ORs roles together
        return Permission(*[RoleNeed(role) for role in roles])

    @staticmethod
    def has_any_role(*roles):
        return CurrentUser.has_any_role_permission(*roles).can()

    @staticmethod
    def check_any_role(*roles):
        if CurrentUser.has_any_role_permission(*roles).can():
            return True
        else:
            utils.do_flash(*utils.get_message('UNAUTHORIZED'))
            return False
