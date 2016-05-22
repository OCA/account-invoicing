# -*- coding: utf-8 -*-
# © 2016 <OCA>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from openerp import models, api, _

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    @api.multi
    def compute_invoice_tax_lines(self):
        self.ensure_one()
        taxes_grouped = self.get_taxes_values()
        tax_lines = self.tax_line_ids.browse([])
        for tax in taxes_grouped.values():
            tax_lines += tax_lines.new(tax)

        self.tax_line_ids = tax_lines
            
        return []

    