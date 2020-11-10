# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def action_invoice_open(self):
        sale = self.env['sale.order'].search(
            [('name', '=', self.origin)],
            limit=1)
        sale._check_require_po_doc()
        return super(AccountInvoice, self).action_invoice_open()
