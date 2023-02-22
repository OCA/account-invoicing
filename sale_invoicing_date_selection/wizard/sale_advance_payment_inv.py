# Copyright 2022 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    invoice_date = fields.Date()

    def create_invoices(self):
        """
        Add date to crate all invoices into user context
        """
        ctx = self.env.context.copy()
        if self.invoice_date:
            ctx.update(
                {
                    "default_invoice_date": self.invoice_date,
                    "default_date": self.invoice_date,
                }
            )
        return super(SaleAdvancePaymentInv, self.with_context(**ctx)).create_invoices()
