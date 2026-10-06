# Copyright 2023 Camptocamp SA
# Copyright 2023 Michael Tietz (MT Software) <mtietz@mt-software.de>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models
from odoo.orm.domains import Domain


class AccountMove(models.Model):
    _inherit = "account.move"

    def cron_send_email_invoice(self):
        # The partner's invoice sending method is company dependent
        for company in self.env["res.company"].search([]):  # pylint: disable=no-search-all
            moves = self.with_company(company)
            for invoice in moves.search(moves._email_invoice_to_send_domain()):
                description = f"Send invoice {invoice.name} by email"
                invoice.with_delay(
                    description=description
                )._execute_invoice_sent_wizard()

    def _prepare_invoice_sent_wizard_vals(self):
        return {
            "sending_method_checkboxes": {
                "email": {"checked": True, "label": "by Email"}
            }
        }

    def _execute_invoice_sent_wizard(self, options=None):
        self.ensure_one()
        if self.is_move_sent:
            return self.env._("This invoice has already been sent.")
        partner = self.commercial_partner_id.with_company(self.company_id)
        if partner.invoice_sending_method != "email":
            return self.env._("This invoice should not be sent by mail")
        res = self.action_invoice_sent()
        wiz_ctx = res["context"] or {}
        wiz_ctx["active_model"] = self._name
        wiz_ctx["active_ids"] = self.ids
        wiz = (
            self.env["account.move.send.wizard"]
            .with_context(**wiz_ctx)
            .create(self._prepare_invoice_sent_wizard_vals())
        )
        return wiz.action_send_and_print()

    @api.model
    def _email_invoice_to_send_domain(self) -> Domain:
        return Domain(
            [
                ("company_id", "=", self.env.company.id),
                ("move_type", "in", ("out_invoice", "out_refund")),
                ("state", "=", "posted"),
                ("is_move_sent", "=", False),
                ("commercial_partner_id.invoice_sending_method", "=", "email"),
                ("payment_state", "=", "not_paid"),
            ]
        )
