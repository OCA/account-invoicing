# Copyright 2019 Digital5 S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api
from odoo.tools import float_is_zero


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.model
    def create(self, vals):
        if vals.get("invoice_id", False):
            invoice = self.env["account.invoice"].browse(vals["invoice_id"])
            avoid_zero_lines = (
                invoice.journal_id and invoice.journal_id.avoid_zero_lines
            )
            if avoid_zero_lines:
                if vals.get("uom_id", False):
                    uom_id = vals["uom_id"]
                else:
                    uom_id = self.env["product.template"]._get_default_uom_id()
                uom = self.env["product.uom"].browse(uom_id)
                if float_is_zero(
                    vals["quantity"], precision_rounding=uom.rounding
                ):
                    return self.env["account.invoice.line"]
        return super().create(vals)
