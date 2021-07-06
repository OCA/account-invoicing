# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

from odoo.tools import float_compare


@openupgrade.migrate()
def migrate(env, version):
    """Fill existing global discount entries with the source global discount
    and missing tax links.
    """
    lines = env["account.move.line"].search([("global_discount_item", "=", True)])
    for line in lines:
        discount = line.move_id.invoice_global_discount_ids.filtered(
            lambda x: x.account_id == line.account_id
            and x.account_analytic_id == line.analytic_account_id
            and (
                not float_compare(
                    x.discount_amount,
                    line.debit,
                    precision_rounding=line.move_id.currency_id.rounding,
                )
                or not float_compare(
                    x.discount_amount,
                    -line.credit,
                    precision_rounding=line.move_id.currency_id.rounding,
                )
            )
            and x not in line.move_id.line_ids.mapped("invoice_global_discount_id")
        )[:1]
        if discount:
            for tax in line.tax_ids - discount.tax_ids:
                env.cr.execute(
                    "DELETE FROM account_move_line_account_tax_rel "
                    "WHERE account_move_line_id = %s AND account_tax_id = %s ",
                    (line.id, tax.id),
                )
            for tax in discount.tax_ids - line.tax_ids:
                env.cr.execute(
                    "INSERT INTO account_move_line_account_tax_rel "
                    "(account_move_line_id, account_tax_id) VALUES (%s, %s)",
                    (line.id, tax.id),
                )
            # Fill it for existing lines, although this is not working with new ones
            line.invoice_global_discount_id = discount.id
