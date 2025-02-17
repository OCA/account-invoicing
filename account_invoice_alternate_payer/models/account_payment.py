# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.model
    def default_get(self, default_fields):
        res = super().default_get(default_fields)
        if self.env.context.get("active_model") != "account.move":
            return res
        active_ids = self.env.context.get("active_ids")
        invoices = (
            self.env["account.move"]
            .browse(active_ids)
            .filtered(lambda move: move.is_invoice(include_receipts=True))
        )
        if invoices and invoices[0].alternate_payer_id:
            res.update({"partner_id": invoices[0].alternate_payer_id.id})
        return res
