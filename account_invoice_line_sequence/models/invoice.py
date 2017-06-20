# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA - Damien Crier, Alexandre Fayolle
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    sequence = fields.Integer(help="Gives the sequence of this line when "
                              "displaying the account invoice.", store=True)

    sequence2 = fields.Integer(help="Shows the sequence of this line in the "
                               " invoice.", related='sequence', readonly=True)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    @api.depends('invoice_line_ids')
    def _compute_max_line_sequence(self):
        """Allow to know the highest sequence entered in invoice lines.
        Then we add 1 to this value for the next sequence.
        This value is given to the context of the o2m field in the view.
        So when we create new invoice lines, the sequence is automatically
        added as :  max_sequence + 1
        """
        for rec in self:
            rec.max_line_sequence =\
                (max(rec.mapped('invoice_line_ids.sequence') or [0]) + 1)

    max_line_sequence = fields.Integer(string='Max sequence in lines',
                                       compute='_compute_max_line_sequence')

    @api.multi
    def _reset_sequence(self):
        for rec in self:
            current_sequence = 1
            for line in rec.invoice_line_ids:
                line.write({'sequence': current_sequence})
                current_sequence += 1

    @api.multi
    def write(self, values):
        res = super(AccountInvoice, self).write(values)
        for rec in self:
            rec._reset_sequence()
        return res
