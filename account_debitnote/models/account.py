# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _


class AccountJournal(models.Model):
    _inherit = "account.journal"

    debitnote_sequence_id = fields.Many2one(
        comodel_name='ir.sequence',
        string='Debit Note Entry Sequence',
        help="""This field contains the information related to the numbering of
                the debit note entries of this journal.""",
        copy=False
    )
    debitnote_sequence_number_next = fields.Integer(
        string='Debit Notes: Next Number',
        help='The next sequence number will be used for the next debit note.',
        compute='_compute_debitnote_seq_number_next',
        inverse='_inverse_debitnote_seq_number_next',
    )
    debitnote_sequence = fields.Boolean(
        string='Dedicated Debit Note Sequence',
        help="""Check this box if you don't want to share the same sequence
                for invoices and debit notes made from this journal""",
        default=False,
    )

    @api.depends('debitnote_sequence_id.use_date_range',
                 'debitnote_sequence_id.number_next_actual')
    def _compute_debitnote_seq_number_next(self):
        """
            Compute 'sequence_number_next' according to the current sequence
            in use, an ir.sequence or an ir.sequence.date_range.
        """
        for journal in self:
            if journal.debitnote_sequence_id and journal.debitnote_sequence:
                sequence = journal.debitnote_sequence_id.\
                    _get_current_sequence()
                journal.debitnote_sequence_number_next = sequence.\
                    number_next_actual
            else:
                journal.debitnote_sequence_number_next = 1

    @api.multi
    def _inverse_debitnote_seq_number_next(self):
        """
            Inverse 'debitnote_sequence_number_next' to edit
            the current sequence next number.
        """
        for journal in self:
            if journal.debitnote_sequence_id and \
                    journal.debitnote_sequence and \
                    journal.debitnote_sequence_number_next:
                sequence = journal.debitnote_sequence_id.\
                    _get_current_sequence()
                sequence.number_next = journal.debitnote_sequence_number_next

    @api.multi
    def write(self, vals):
        # create the relevant debitnote sequence
        res = super().write(vals)
        if vals.get('debitnote_sequence'):
            for journal in self.filtered(((
                    lambda j: j.type in ('sale', 'purchase') and not
                    j.debitnote_sequence_id))):
                journal_vals = {
                    'name': journal.name,
                    'company_id': journal.company_id.id,
                    'code': journal.code,
                    'debitnote_sequence_number_next':
                        vals.get('debitnote_sequence_number_next',
                                 journal.debitnote_sequence_number_next),
                }
                journal.debitnote_sequence_id = self.sudo().\
                    _create_debitnote_sequence(journal_vals, debitnote=True).id
        return res

    @api.model
    def _get_debitnote_sequence_prefix(self, code, debitnote=False):
        prefix = code.upper()
        if debitnote:
            prefix = 'D' + prefix
        return prefix + '/%(range_year)s/'

    @api.model
    def _create_debitnote_sequence(self, vals, debitnote=False):
        """ Create new no_gap entry sequence for every new Journal"""
        prefix = self._get_debitnote_sequence_prefix(vals['code'], debitnote)
        seq_name = debitnote and vals['code'] + \
            _(': Debitnote') or vals['code']
        seq = {
            'name': _('%s Sequence') % seq_name,
            'implementation': 'no_gap',
            'prefix': prefix,
            'padding': 4,
            'number_increment': 1,
            'use_date_range': True,
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
        seq = self.env['ir.sequence'].create(seq)
        seq_date_range = seq._get_current_sequence()
        seq_date_range.number_next = debitnote and \
            vals.get('debitnote_sequence_number_next', 1) or \
            vals.get('sequence_number_next', 1)
        return seq

    @api.model
    def create(self, vals):
        if vals.get('type') in ('sale', 'purchase') and \
                vals.get('debitnote_sequence') and not \
                vals.get('debitnote_sequence_id'):
            vals.update({'debitnote_sequence_id':
                        self.sudo()._create_debitnote_sequence
                        (vals, debitnote=True).id})
        res = super().create(vals)

        return res
