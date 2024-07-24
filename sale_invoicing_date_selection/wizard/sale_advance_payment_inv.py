# Copyright 2022 Sergio Teruel <sergio.teruel@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    invoice_date = fields.Date()

    def _create_invoices(self, sale_orders):
        if self.advance_payment_method == "delivered" and self.invoice_date:
            ctx = self.env.context.copy()
            ctx.update(
                {
                    "default_invoice_date": self.invoice_date,
                }
            )
            return sale_orders.with_context(**ctx)._create_invoices(
                final=self.deduct_down_payments, grouped=not self.consolidated_billing
            )
        return super()._create_invoices(sale_orders)

    def _prepare_invoice_values(self, order, so_line):
        """Redefine function to take into account invoices
        created when advanced payment method is not delivered"""
        res = super()._prepare_invoice_values(order, so_line)
        if self.invoice_date:
            res["invoice_date"] = self.invoice_date
            res["date"] = self.invoice_date
        return res
