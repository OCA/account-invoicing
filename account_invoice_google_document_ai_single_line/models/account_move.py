from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("quick_edit_total_amount", "partner_id")
    def _onchange_quick_edit_total_amount(self):
        """Inherit method for remove tax from the invoice without tax."""
        res = super(AccountMove, self)._onchange_quick_edit_total_amount()
        if not self.env.context.get("without_tax", False):
            return res
        price_unit = self.invoice_line_ids[:1].price_unit + self.amount_tax
        self.invoice_line_ids.write({"tax_ids": False, "price_unit": price_unit})
