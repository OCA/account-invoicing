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

    def _compute_amount(self):
        # Avoid recomputation of amount fields when we are only changing the
        # invoice's due date
        if self.env.context.get("bypass_compute_amount"):
            return
        return super()._compute_amount()

    def onchange(self, values, field_name, field_onchange):
        obj = self
        if field_name == "invoice_date_due" and self.state == "posted":
            # A change in the invoice date due would trigger a recompute of the
            # amount fields. We want to avoid that to prevent inconsistencies with
            # the payment state.
            obj = self.with_context(bypass_compute_amount=True)
        return super(AccountMove, obj).onchange(values, field_name, field_onchange)

    def write(self, vals):
        res = super().write(vals)
        # Propagate due date to move lines
        # that correspont to the receivable/payable account
        if "invoice_date_due" in vals:
            payment_term_lines = self.filtered(
                lambda r: r.state == "posted"
            ).line_ids.filtered(
                lambda line: line.account_id.user_type_id.type
                in ("receivable", "payable")
            )
            payment_term_lines.date_maturity = vals["invoice_date_due"]
        return res
