# Copyright 2025 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends("set_self_invoice")
    def _compute_is_invoice_to_transmit(self):
        res = super()._compute_is_invoice_to_transmit()
        for rec in self:
            if (
                rec.state == "posted"
                and rec.move_type in ("in_invoice", "in_refund")
                and rec.set_self_invoice
            ):
                rec.is_invoice_to_transmit = True
        return res

    def _get_transmit_invoice_by_email_template(self):
        res = super()._get_transmit_invoice_by_email_template()
        if self.move_type == "in_invoice":
            return self.env.ref(
                "account_invoice_supplier_self_invoice.email_template_self_invoice"
            )
        if self.move_type == "in_refund":
            return self.env.ref(
                "account_invoice_supplier_self_invoice.email_template_self_invoice"
            )
        return res
