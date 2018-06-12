# -*- coding: utf-8 -*-
# © 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import operator
from openerp import api, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def line_get_convert(self, line, part, date):
        return dict(
            super(AccountInvoice, self).line_get_convert(line, part, date),
            invoice_line_ids=line.get('invoice_line_ids', []),
        )

    @api.multi
    def group_lines(self, iml, line):
        """When grouping lines, aggregate links to invoice lines too"""
        self.ensure_one()
        if not self.journal_id.group_invoice_lines:
            return line
        result = super(AccountInvoice, self).group_lines(iml, line)[:]
        for dummy, dummy, move_line_data in result:
            invoice_lines = self.env['account.invoice.line'].browse(map(
                operator.itemgetter('id'),
                self.env['account.move.line'].resolve_2many_commands(
                    'invoice_line_ids',
                    move_line_data.get('invoice_line_ids', []),
                    ['id'],
                ),
            ))
            if not invoice_lines:
                continue
            move_line_data['invoice_line_ids'] += [
                (4, other_invoice_line.id)
                for other_invoice_line
                in self.invoice_line.filtered(
                    lambda x, invoice_lines=invoice_lines:
                    not x & invoice_lines and
                    self.inv_line_characteristic_hashcode(
                        x.read(load='_classic_write')[0]
                    ) == self.inv_line_characteristic_hashcode(
                        invoice_lines.read(load='_classic_write')[0]
                    )
                )
            ]
        return result
