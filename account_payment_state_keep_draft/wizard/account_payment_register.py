# Copyright 2025 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, models

MAPPING_TYPE = {
    "inbound": "register_customer_payment_state",
    "outbound": "register_vendor_payment_state",
}


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    def _check_payment_draft(self):
        return bool(self.env.company[MAPPING_TYPE.get(self.payment_type)] == "draft")

    def _create_payments(self):
        if self._check_payment_draft():
            payments = super(
                AccountPaymentRegister, self.with_context(no_cash_basis=True)
            )._create_payments()
            to_draft = payments.filtered(lambda p: p.state != "draft")
            invoices_per_payment = {p: p.invoice_ids for p in to_draft}
            to_draft.action_draft()
            for payment, invoices in invoices_per_payment.items():
                payment.invoice_ids = [Command.link(inv.id) for inv in invoices]
            return payments
        return super()._create_payments()
