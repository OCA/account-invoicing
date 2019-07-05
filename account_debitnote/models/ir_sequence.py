# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, api, _
from odoo.exceptions import UserError


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    @api.multi
    def next_by_id(self):
        invoice = self._context.get('ctx_invoice', False)
        if invoice:
            journal = invoice.journal_id
            if invoice.debit_invoice_id and \
                    invoice.type in ['out_invoice', 'in_invoice'] and \
                    journal.debitnote_sequence:
                if not journal.debitnote_sequence_id:
                    raise UserError(
                        _('Please define a sequence for the debit notes'))
                self = journal.debitnote_sequence_id
        return super().next_by_id()
