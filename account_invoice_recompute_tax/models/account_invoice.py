# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def button_reset_tax_line_ids(self):
        for invoice in self:
            invoice.tax_line_ids.unlink()
            invoice._onchange_invoice_line_ids()
