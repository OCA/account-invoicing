# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    # Show invoice date due even when payment term is defined
    invoice_date_due_payment_term = fields.Date(
        related="invoice_date_due", string="Due Date Payment Term"
    )
    invoice_date_due = fields.Date(
        string="Due Date",
        compute="_compute_invoice_date_due",
        inverse="_inverse_invoice_date_due",
    )

    def _inverse_invoice_date_due(self):
        for invoice in self:
            if invoice.state == "posted":
                if self.env.user.id != SUPERUSER_ID and not self.env.user.has_group(
                    "account_invoice_date_due.allow_to_change_due_date"
                ):
                    raise UserError(_("You are not allowed to change the due date."))

    def button_draft(self):
        invoice_due_dates = {move.id: move.invoice_date_due for move in self}
        res = super().button_draft()
        for move in self.with_user(SUPERUSER_ID):  # bypass the group test
            move.invoice_date_due = invoice_due_dates[move.id]
        return res

    def _post(self, soft=True):
        invoice_due_dates = {move.id: move.invoice_date_due for move in self}
        res = super()._post(soft=soft)
        for move in self.with_user(SUPERUSER_ID):  # bypass the group test
            move.invoice_date_due = invoice_due_dates[move.id]
        return res

    @api.onchange("invoice_date_due_payment_term")
    def _onchange_invoice_date_due_payment_term(self):
        """Propagate from Payment term due date to original field"""
        if self.invoice_date_due_payment_term:
            self.invoice_date_due = self.invoice_date_due_payment_term

    def write(self, vals):
        res = super().write(vals)
        # Propagate due date to move lines
        # that correspont to the receivable/payable account
        if "invoice_date_due" in vals and self.state == "posted":
            payment_term_lines = self.line_ids.filtered(
                lambda line: line.account_id.account_type
                in ("asset_receivable", "liability_payable")
            )
            payment_term_lines.write({"date_maturity": vals["invoice_date_due"]})
        return res
