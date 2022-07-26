# Copyright 2022 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    invoice_date = fields.Date(string="Invoice Date")

    def create_invoices(self):
        """
        Add date to crate all invoices into user context
        """
        return super(
            SaleAdvancePaymentInv,
            self.with_context(default_invoice_date=self.invoice_date),
        ).create_invoices()
