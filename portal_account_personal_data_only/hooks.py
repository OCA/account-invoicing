# Copyright 2019 Tecnativa - David Vidal
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def post_init_hook(env):
    """Archive the ir.rules we want to override"""
    env.ref("account.account_invoice_rule_portal").active = False
    env.ref("account.account_invoice_line_rule_portal").active = False


def uninstall_hook(env):
    """Unarchive the overriden ir.rules"""
    env.ref("account.account_invoice_rule_portal").active = True
    env.ref("account.account_invoice_line_rule_portal").active = True
