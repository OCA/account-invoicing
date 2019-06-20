# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def _check_duplicate_supplier_reference(self):
        # Do nothing instead of checking if the reference number already
        # exists.
        pass
