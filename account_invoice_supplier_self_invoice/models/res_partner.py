# -*- coding: utf-8 -*-
# © 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    self_invoice = fields.Boolean(
        string='Approves self invoice',
        default=False,
        help='When checked, all invoices will generate a self-invoice '
             'on validation'
    )
    self_invoice_sequence_id = fields.Many2one(
        comodel_name='ir.sequence',
        string='Self invoice sequence',
        ondelete='restrict'
    )
    self_invoice_report_footer = fields.Text(
        string='Self invoice footer',
        help='Footer text displayed at the bottom of the self invoice reports.'
    )

    def set_self_invoice(self):
        for record in self:
            record.self_invoice = not record.self_invoice
            if record.self_invoice_sequence_id:
                continue
            if record.self_invoice:
                record.self_invoice_sequence_id = \
                    self.env['ir.sequence'].create({
                        'name': record.name + ' Self invoice sequence',
                        'implementation': 'no_gap',
                        'number_increment': 1,
                        'padding': 4,
                        'prefix': 'CBINV/%(range_year)s/',
                        'use_date_range': True,
                        'number_next': 1
                    })
