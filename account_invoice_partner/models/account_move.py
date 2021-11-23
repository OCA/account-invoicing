# Copyright 2013-2017 Therp BV (<http://therp.nl>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        """
        Replace the selected partner with the preferred invoice contact
        """
        partner_invoice = self.partner_id
        if self.partner_id:
            addr_ids = self.partner_id.address_get(adr_pref=["invoice"])
            partner_invoice = self.env["res.partner"].browse(addr_ids["invoice"])
        result = super()._onchange_partner_id()
        if partner_invoice != self.partner_id:
            self.partner_id = partner_invoice
        return result
