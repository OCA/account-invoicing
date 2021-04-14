# Copyright 2021 Sergio Corato <https://github.com/sergiocorato>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountInvoiceRefund(models.TransientModel):
    _inherit = "account.invoice.refund"

    update_sale_order = fields.Boolean()

    @api.multi
    def compute_refund(self, mode='refund'):
        res = super().compute_refund(mode=mode)
        if res.get('domain', False):
            created_inv = self.env['account.invoice'].search(res['domain'])
            if not created_inv:
                return res
            for form in self:
                if form.update_sale_order:
                    for inv in created_inv:
                        for line in inv.invoice_line_ids:
                            if line.origin_line_ids:
                                line.sale_line_ids = line.origin_line_ids.sale_line_ids
        return res
