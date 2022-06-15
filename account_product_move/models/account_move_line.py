# Copyright 2022 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _create_extra_moves(self):
        move_model = self.env["account.move"]
        for line in self:
            product_move = line.product_id.product_tmpl_id.product_move_id
            if not product_move or product_move.state != "complete":
                continue
            vals = {
                "type": "entry",
                "ref": line.move_id.name,
                "journal_id": product_move.journal_id.id,
                "date": line.move_id.invoice_date,
                "invoice_move_id": line.move_id.id,
            }
            extra_move = move_model.create(vals)
            line._create_extra_move_lines(extra_move)
            extra_move.action_post()

    def _create_extra_move_lines(self, extra_move):
        """Create extra move lines for product move."""
        self.ensure_one()
        product_move = self.product_id.product_tmpl_id.product_move_id
        for product_move_line in product_move.line_ids:
            if self.move_id.type == "out_invoice":
                credit = product_move_line.credit
                debit = product_move_line.debit
            else:
                credit = product_move_line.debit
                debit = product_move_line.credit
            quantity = self.quantity
            extra_move_line = self.with_context(check_move_validity=False).create(
                {
                    "move_id": extra_move.id,
                    "account_id": product_move_line.account_id.id,
                    "currency_id": product_move_line.currency_id.id,
                    "amount_currency": product_move_line.amount_currency * quantity,
                    "credit": credit * quantity,
                    "debit": debit * quantity,
                }
            )
            extra_move_line._onchange_currency()
