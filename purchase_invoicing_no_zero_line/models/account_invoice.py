# Copyright 2019 Digital5 S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api
from odoo.tools import float_is_zero


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        ctx = dict(
            self._context,
            avoid_zero_lines=self.journal_id and self.journal_id.avoid_zero_lines
        )
        return super(AccountInvoice, self.with_context(ctx)).purchase_order_change()


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.model
    def create(self, vals):
        if self._context.get("avoid_zero_lines"):
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
