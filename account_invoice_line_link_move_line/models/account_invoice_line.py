# -*- coding: utf-8 -*-
# © 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    move_line_ids = fields.Many2many(
        'account.move.line', relation='account_invoice_line_move_line_rel',
        column1='invoice_line_id', column2='move_line_id', auto_join=True,
        string='Accounting entries',
    )

    @api.model
    def move_line_get_item(self, line):
        """Add a link to the invoice line this move originates from"""
        return dict(
            super(AccountInvoiceLine, self).move_line_get_item(line),
            invoice_line_ids=[(4, line.id)],
        )

    @api.multi
    def _find_move_line(self):
        """Look up the move lines mapped to this invoice lines. Note that this
        addon exists to make code like this superfluous, but we use it during
        installation in order to set the link right for existing move lines.
        Override this and rerun the hook if you need custom code here."""
        result = self.env['account.move.line'].browse([])
        for this in self:
            move_line_data = this.move_line_get_item(this)
            move_line_data.pop('invoice_line_ids')
            # correct name difference between move and lin
            if 'account_analytic_id' in move_line_data.keys():
                move_line_data['analytic_account_id'] = move_line_data.pop(
                    'account_analytic_id'
                )

            sign = -1 if this.invoice_id.type in [
                'in_refund', 'out_invoice'
            ] else 1
            price = move_line_data['price'] * sign
            move_line_data.update(
                debit=price > 0 and price,
                credit=price < 0 and -price,
            )

            # clean non existing fields
            for key in move_line_data.keys():
                if key not in result._fields:
                    move_line_data.pop(key)
            result += this.invoice_id.move_id.line_id.filtered(
                lambda x, mld=move_line_data: mld == {
                    key: value
                    for key, value in x.read(
                        mld.keys(), load='_classic_write',
                    )[0].iteritems() if key != 'id'
                }
            )
        return result
