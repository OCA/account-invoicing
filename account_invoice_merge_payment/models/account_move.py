# Copyright 2015-2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):

    _inherit = "account.move"

    @api.model
    def _get_invoice_key_cols(self):
        return super()._get_invoice_key_cols() + ["payment_mode_id"]

    @api.model
    def _get_first_invoice_fields(self, invoice):
        res = super()._get_first_invoice_fields(invoice)
        res.update({"payment_mode_id": invoice.payment_mode_id.id})
        return res
