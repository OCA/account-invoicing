# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.model
    def default_get(self, default_fields):
        rec = super().default_get(default_fields)
        if self.env.context.get("active_model") != "account.move":
            return rec
        active_ids = self._context.get("active_ids")
        invoices = (
            self.env["account.move"]
            .browse(active_ids)
            .filtered(lambda move: move.is_invoice(include_receipts=True))
        )
        if invoices and invoices[0].alternate_payer_id:
            rec.update({"partner_id": invoices[0].alternate_payer_id.id})
        return rec


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def _prepare_payment_vals(self, invoices):
        res = super()._prepare_payment_vals(invoices)
        payer_id = (
            invoices[0].alternate_payer_id.id or invoices[0].commercial_partner_id.id
        )
        res["partner_id"] = payer_id
        return res
