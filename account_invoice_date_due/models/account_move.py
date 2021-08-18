# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    # Show invoice date due even when payment term is defined
    invoice_date_due_payment_term = fields.Date(
        related="invoice_date_due", string="Due Date Payment Term"
    )

    @api.onchange("invoice_date_due_payment_term")
    def _onchange_invoice_date_due_payment_term(self):
        """Propagate from Payment term due date to original field"""
        if self.invoice_date_due_payment_term:
            self.invoice_date_due = self.invoice_date_due_payment_term

    def write(self, vals):
        res = super().write(vals)
        # Propagate due date to move lines
        # that correspont to the receivable/payable account
        if "invoice_date_due" in vals:
            for record in self.filtered(lambda r: r.state == "posted"):
                payment_term_lines = record.line_ids.filtered(
                    lambda line: line.account_id.user_type_id.type
                    in ("receivable", "payable")
                )
                payment_term_lines.write({"date_maturity": vals["invoice_date_due"]})
        return res
