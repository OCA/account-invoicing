# -*- coding: utf-8 -*-
# Copyright 2019 Digital5 S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.tools import float_is_zero


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        """
        after the creation of the lines, delete the zero qty lines
        if the journal is marked as such
        """
        res = super(AccountInvoice, self).purchase_order_change()
        if self.journal_id and self.journal_id.avoid_zero_lines:
            self.invoice_line_ids -= self.invoice_line_ids.filtered(
                lambda x: float_is_zero(
                    x.quantity, precision_rounding=x.uom_id.rounding,
                )
            )
        return res
