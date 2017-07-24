# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class AccountInvoiceSplitLine(models.TransientModel):
    _inherit = 'account.invoice.split.line'

    @api.multi
    def _get_invoice_line_values(self):
        """
        Link new invoice line to sale line
        """
        self.ensure_one()
        values = super(AccountInvoiceSplitLine, self).\
            _get_invoice_line_values()
        values['sale_line_ids'] = [
            (4, line.id) for line in self.origin_invoice_line_id.sale_line_ids]
        return values
