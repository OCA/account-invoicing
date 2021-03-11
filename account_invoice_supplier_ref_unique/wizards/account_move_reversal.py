# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveReversal(models.TransientModel):
    _inherit = "account.move.reversal"

    supplier_invoice_number = fields.Char(string="Vendor invoice number",)

    def _prepare_default_reversal(self, move):
        res = super()._prepare_default_reversal(move)
        res["supplier_invoice_number"] = self.supplier_invoice_number
        return res
