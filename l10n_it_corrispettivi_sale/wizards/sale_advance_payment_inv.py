# Copyright 2019 Simone Rubino
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        invoice = super()._create_invoice(order, so_line, amount)
        if order.corrispettivi:
            invoice.journal_id = self.env['account.journal'].get_corr_journal()
        return invoice
