# Copyright (C) 2022-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    _UPDATE_CHECK_FIELDS = [
        "product_id",
        "account_id",
        "name",
        "quantity",
        "price_unit",
        "invoice_line_tax_ids",
        "discount",
        "price_subtotal",
    ]

    @api.multi
    def write(self, vals):
        if any(key in vals for key in self._UPDATE_CHECK_FIELDS):
            self._update_check()
        return super().write(vals)

    @api.multi
    def _update_check(self):
        if self.filtered(lambda x: x.invoice_id.state != "draft"):
            raise ValidationError(
                _(
                    "You cannot do this modification on non draft invoice lines."
                )
            )
