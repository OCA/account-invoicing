# Copyright 2019 Alessandro Camilli - Openforce
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        inv = self._context.get('invoice', False)

        if inv and not inv.amount_untaxed:
            # Account partner must no exist
            partner_account_exists = False
            for line in vals['line_ids']:
                if inv.account_id.id == line[2]['account_id']:
                    partner_account_exists = True
            if not partner_account_exists:
                # Add line partner
                company_currency = inv.company_id.currency_id
                diff_currency = inv.currency_id != company_currency
                partner = self.env['res.partner']._find_accounting_partner(
                    inv.partner_id)
                name = inv.name or '/'
                part_vals = {
                    'type': 'dest',
                    'name': name,
                    'price': 0.0,
                    'partner_id': partner.id,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': 0.0,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                }
                vals['line_ids'].append((0, 0, part_vals))
        am = super().create(vals)
        # Set move type
        if inv:
            if inv.type == 'in_invoice':
                am.move_type = 'payable'
            elif inv.type == 'in_refund':
                am.move_type = 'payable_refund'
            elif inv.type == 'out_invoice':
                am.move_type = 'receivable'
            elif inv.type == 'out_refund':
                am.move_type = 'receivable_refund'
        return am
