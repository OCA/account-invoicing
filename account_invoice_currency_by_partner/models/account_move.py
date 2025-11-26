# Copyright 2025 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends("partner_id")
    def _compute_currency_id(self):
        res = super()._compute_currency_id()
        _self = self.filtered(
            lambda x: x.partner_id.vendor_currency_id
            or x.partner_id.customer_currency_id
        )
        for invoice in _self:
            if (
                invoice.move_type in ["in_invoice", "in_refund"]
                and invoice.partner_id.vendor_currency_id
            ):
                invoice.currency_id = invoice.partner_id.vendor_currency_id
            elif (
                invoice.move_type in ["out_invoice", "out_refund"]
                and invoice.partner_id.customer_currency_id
            ):
                invoice.currency_id = invoice.partner_id.customer_currency_id
        return res
