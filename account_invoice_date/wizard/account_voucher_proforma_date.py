# © 2022 Thomas Rehn (initOS GmbH)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AccountVoucherProformaDate(models.TransientModel):
    _name = "account.voucher.proforma.date"
    _description = "Account Voucher Proforma Date"

    date = fields.Date(
        string="Date of invoice", required=True, default=fields.Date.context_today
    )
    invoice_type = fields.Char()

    @api.model
    def default_get(self, default_fields):
        res = super(AccountVoucherProformaDate, self).default_get(default_fields)
        invoice_id = self.env.context.get("active_id")
        invoice = self.env["account.move"].browse(invoice_id)
        if invoice:
            res["invoice_type"] = invoice.move_type
        return res

    def action_post(self):
        invoice_id = False
        if self.env.context.get("active_model") == "account.move":
            invoice_id = self.env.context.get("active_id")
        assert invoice_id, "Could not determine invoice to open"
        invoice = self.env["account.move"].browse(invoice_id)
        invoice.invoice_date = self.date
        invoice.action_post()
