from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        if self.partner_id.default_purchase_journal_id:
            invoice_vals["journal_id"] = self.partner_id.default_purchase_journal_id.id
        return invoice_vals
