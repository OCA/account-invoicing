# Copyright 2022 Marco Colombo (Associazione PNLUG - Gruppo Odoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError

RECEIPTS_TYPE = ("out_receipt", "in_receipt")


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf(self, res_ids=None, data=None):
        if self.model == "account.move" and res_ids:
            invoice_reports = (
                self.env.ref("account.account_invoices"),
                self.env.ref("account.account_invoices_without_payment"),
            )
            receipt_reports = (self.env.ref("account_receipt_print.account_receipts"),)

            receipts = (
                self.env["account.move"]
                .browse(res_ids)
                .filtered(lambda m: m.move_type in RECEIPTS_TYPE)
            )

            if self in invoice_reports and receipts:
                raise UserError(_("Only invoices could be printed."))

            if self in receipt_reports and not receipts:
                raise UserError(_("Only receipts could be printed."))

        return super()._render_qweb_pdf(res_ids=res_ids, data=data)
