# -*- coding: utf-8 -*-
#    Author: Alexandre Fayolle
#    Copyright 2013 Camptocamp SA
#    Author: Damien Crier
#    Copyright 2015 Camptocamp SA
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from openerp import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    sequence = fields.Integer(help="Gives the sequence of this line when "
                              "displaying the account invoice.", store=True)

    sequence2 = fields.Integer(help="Shows the sequence of this line in "
                               "the invoice.",
                               related='sequence', readonly=True)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends('invoice_line_ids')
    def compute_max_line_sequence(self):
        """Allow to know the highest sequence
        entered in invoice lines.
        Web add 1 to this value for the next sequence
        This value is given to the context of the o2m field
        in the view. So when we create new invoice lines,
        the sequence is automatically max_sequence + 1
        """
        self.max_line_sequence = (
            max(self.mapped('invoice_line_ids.sequence') or [0]) + 1)

    max_line_sequence = fields.Integer(string='Max sequence in lines',
                                       compute='compute_max_line_sequence')
