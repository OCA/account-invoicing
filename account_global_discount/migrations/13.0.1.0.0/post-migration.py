# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # _onchange_invoice_line_ids method is called to recalculate the
    # value of the base_before_global_discounts field in
    # account.move.line, to update the invoice_global_discount_ids
    # table table in account.move and to create the necessary discount
    # journal entries.
    domain = [
        ("type", "in", env["account.move"].get_invoice_types()),
        ("state", "=", "draft"),
        ("global_discount_ids", "!=", False),
    ]
    env["account.move"].search(domain)._onchange_invoice_line_ids()
