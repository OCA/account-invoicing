# Copyright 2017 Eficent Business and IT Consulting Services
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        """Remove lines with qty=0 if option selected making invoices."""
        res = super().purchase_order_change()
        if self._context.get('exclude_zero_qty', False):
            self.invoice_line_ids -= self.invoice_line_ids.filtered(
                lambda x: x.quantity == 0.0
            )
        return res
