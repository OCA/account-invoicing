# Copyright 2022 Marco Colombo (Associazione PNLUG - Gruppo Odoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models
from odoo.exceptions import UserError

RECEIPTS_TYPE = ("out_receipt", "in_receipt")


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _is_receipt_report(self, report_ref):
        return self._get_report(report_ref).report_name in (
            "account_receipt_print.report_receipt"
        )

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):

        invoices = self.env["account.move"].browse(res_ids)

        if self._is_receipt_report(report_ref):
            if (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("account.display_name_in_footer")
            ):
                data = data and dict(data) or {}
                data.update({"display_name_in_footer": True})
            if any(x.move_type not in RECEIPTS_TYPE for x in invoices):
                raise UserError(_("Only receipts could be printed."))

        if self._is_invoice_report(report_ref):
            if any(x.move_type in RECEIPTS_TYPE for x in invoices):
                raise UserError(_("Only invoices could be printed."))

        return super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)
