# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools import config


class AccountInvoice(models.Model):
    _inherit = "account.move"

    @api.constrains("ref")
    def _check_duplicate_supplier_reference(self):
        """ Do nothing instead of checking if the reference number already exists. """
        if config["test_enable"] and not self.env.context.get("test_no_refuse_ref"):
            super()._check_duplicate_supplier_reference()
