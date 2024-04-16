# Copyright 2024 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoice_warn_option = fields.Many2one(
        comodel_name="warn.option",
    )

    @api.onchange("invoice_warn_option")
    def _onchange_invoice_warn_option(self):
        if self.invoice_warn != "no-message" and self.invoice_warn_option:
            self.invoice_warn_msg = self.invoice_warn_option.name
