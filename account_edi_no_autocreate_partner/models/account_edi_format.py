# Copyright 2025 ACSOPNE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountEdiFormat(models.Model):

    _inherit = "account.edi.format"

    def _retrieve_partner(
        self, name=None, phone=None, mail=None, vat=None, domain=None
    ):
        partner = super()._retrieve_partner(
            name=name, phone=phone, mail=mail, vat=vat, domain=domain
        )
        if not partner:
            partner = self.env.ref(
                "account_edi_no_autocreate_partner.partner_not_found"
            )
        return partner
