# Copyright 2022 Marco Colombo (Associazione PNLUG - Gruppo Odoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, _
from odoo.exceptions import UserError

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_qweb_pdf(self, res_ids=None, data=None):
        if self.model == 'account.move' and res_ids:
            report_invoice = self.env.ref('account.account_invoices')
            report_invoice_wop = self.env.ref('account.account_invoices_without_payment')
            report_receipt = self.env.ref('account_receipt_print.account_receipts')

            moves = self.env['account.move'].browse(res_ids).filtered(lambda m: m.is_invoice(include_receipts=True))
            invoices = moves.filtered(lambda m: m.is_invoice(include_receipts=False))
            receipts = moves - invoices

            if self in (report_invoice, report_invoice_wop) and receipts:
                raise UserError(_("Only invoices could be printed."))

            if self in (report_receipt,) and invoices:
                raise UserError(_("Only receipts could be printed."))

        return super()._render_qweb_pdf(res_ids=res_ids, data=data)
