# Copyright 2020 David Vidal
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from openupgradelib.openupgrade import migrate


@migrate()
def migrate(env, version):
    """Put all invoice users as global discount managers"""
    users = env.ref("account.group_account_invoice").users
    env.ref("base_global_discount.group_global_discount").users |= users
