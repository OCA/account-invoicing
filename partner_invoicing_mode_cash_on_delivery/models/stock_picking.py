# Copyright 2018 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    cash_on_delivery_invoice_ids = fields.Many2many(
        "account.move", string="COD Invoices", copy=False, readonly=True
    )

    def _invoice_at_shipping(self):
        """
        This will take this picking into account for invoice creation (at shipping)
        when sale order has Cash On Delivery set and even if the partner is not
        using that mode (at shipping).
        """
        self.ensure_one()
        res = super()._invoice_at_shipping()
        res = res or self.sale_id.payment_mode_id.cash_on_delivery
        return res

    def _invoicing_at_shipping_validation(self, invoices):
        # COD invoices will be validated automatically
        cod_invoices_to_validate = invoices.filtered(
            lambda invoice: invoice.payment_mode_id.cash_on_delivery
            and invoice.payment_mode_id.auto_validate_invoice_cash_on_delivery
        )
        # Non-COD invoices need to check in the call of `super`
        invoices_to_validate = invoices.filtered(
            lambda invoice: not invoice.payment_mode_id.cash_on_delivery
        )
        res = super()._invoicing_at_shipping_validation(invoices_to_validate)
        if cod_invoices_to_validate:
            res |= cod_invoices_to_validate
        return res

    def _invoicing_at_shipping(self):
        self.ensure_one()
        res = super()._invoicing_at_shipping()
        if not isinstance(res, str):
            cod_invoices = res.filtered(
                lambda inv: inv.payment_mode_id.cash_on_delivery
            )
            self.cash_on_delivery_invoice_ids = cod_invoices
        return res
