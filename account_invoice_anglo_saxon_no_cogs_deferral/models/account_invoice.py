# Copyright 2015-2019 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _anglo_saxon_reconcile_valuation(self, product=False):
        """ Ignore customer invoices. """
        supplier_invoices = self.filtered(
            lambda i: i.type in ['in_invoice', 'in_refund'])
        return super(AccountInvoice, supplier_invoices
                     )._anglo_saxon_reconcile_valuation(product=product)

    @api.model
    def _anglo_saxon_sale_move_lines(self, i_line):
        # We override the standard method to invalidate it
        super(AccountInvoice, self)._anglo_saxon_sale_move_lines(
            i_line)
        return []
