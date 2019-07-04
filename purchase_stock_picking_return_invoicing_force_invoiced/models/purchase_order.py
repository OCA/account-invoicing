# Copyright 2019 Eficent Business and IT Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _check_invoice_status_to_invoice(self):
        res = super(PurchaseOrder, self)._check_invoice_status_to_invoice()
        if self.force_invoiced and self.invoice_status == 'invoiced':
            return False
        return res
