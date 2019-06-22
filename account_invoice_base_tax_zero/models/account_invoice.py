# Copyright 2019 Alessandro Camilli - Openforce
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def tax_line_move_line_get(self):
        res = super().tax_line_move_line_get()
        if self.tax_line_ids:
            res = []
            done_taxes = []
            for tax_line in sorted(
                    self.tax_line_ids, key=lambda x: -x.sequence):
                tax = tax_line.tax_id
                if tax.amount_type == "group":
                    for child_tax in tax.children_tax_ids:
                        done_taxes.append(child_tax.id)
                res.append({
                    'invoice_tax_line_id': tax_line.id,
                    'tax_line_id': tax_line.tax_id.id,
                    'type': 'tax',
                    'name': tax_line.name,
                    'price_unit': tax_line.amount_total,
                    'quantity': 1,
                    'price': tax_line.amount_total,
                    'account_id': tax_line.account_id.id,
                    'account_analytic_id': tax_line.account_analytic_id.id,
                    'invoice_id': self.id,
                    'tax_ids': [(6, 0, list(done_taxes))] \
                        if tax_line.tax_id.include_base_amount else []
                })
                done_taxes.append(tax.id)
        return res
