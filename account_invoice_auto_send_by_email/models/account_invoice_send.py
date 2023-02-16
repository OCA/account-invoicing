# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import models


class AccountInvoiceSend(models.TransientModel):
    _inherit = "account.invoice.send"

    def _get_ui_options(self):
        return {
            "is_print": self.is_print,
            "is_email": self.is_email,
            "template_id": self.template_id.id,
            "composition_mode": "mass_mail",
        }
