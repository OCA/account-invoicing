# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def get_taxes_values(self):
        prices = {}
        discount = {}
        for line in self.invoice_line_ids:
            prices[line.id] = line.price_unit
            discount[line.id] = line.discount
            line.price_unit *= (1 - (line.discount or 0.0) / 100.0)
            line.price_unit *= (1 - (line.discount2 or 0.0) / 100.0)
            line.price_unit *= (1 - (line.discount3 or 0.0) / 100.0)
            line['discount'] = 0.0
        tax_grouped = super(AccountInvoice, self).get_taxes_values()
        for line in self.invoice_line_ids:
            line['price_unit'] = prices[line.id]
            line['discount'] = discount[line.id]
        return tax_grouped
