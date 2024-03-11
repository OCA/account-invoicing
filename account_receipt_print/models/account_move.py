# Copyright 2024 Sergio Zanchetta - PNLUG APS
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_show_amount_in_words(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("account_receipt_print.show_amount_in_words")
            or False
        )
