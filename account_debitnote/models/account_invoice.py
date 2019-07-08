from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    is_debitnote = fields.Boolean(
        compute="_compute_is_debitnote",
        string='Debit Note',
        store=True,
    )
    debit_invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='invoice(debit)',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.model
    def _debitnote_cleanup_lines(self, lines):
        """
            Convert records to dict of values suitable
            for one2many line creation
            :param list(browse_record) lines: records to convert
            :return: list of command tuple for one2many line creation
             [(0, 0, dict of valueis), ...]
        """
        result = []
        for line in lines:
            values = {}
            for name, field in line._fields.items():
                if name in ['id', 'create_uid', 'create_date',
                            'write_uid', 'write_date']:
                    continue
                elif field.type == 'many2one':
                    values[name] = line[name].id
                elif field.type not in ['many2many', 'one2many']:
                    values[name] = line[name]
                elif name == 'invoice_line_tax_ids':
                    values[name] = [(6, 0, line[name].ids)]
                elif name == 'analytic_tag_ids':
                    values[name] = [(6, 0, line[name].ids)]
            result.append((0, 0, values))
        return result

    @api.model
    def _prepare_debitnote(self, invoice, date_invoice=None,
                           date=None, description=None, journal_id=None):
        """
            Prepare the dict of values to create the new debit note
            from the invoice.
            This method may be overridden to implement custom debit note
            generation (making sure to call super() to establish a clean
            extension chain).

            :param integer invoice_id: id of the invoice to create debit note
            :param dict invoice: read of the invoice to create debit note
            :param string date: debit note creation date from the wizard
            :param integer period_id: force account.period from the wizard
            :param string description: description of
             the debit note from the wizard
            :param integer journal_id: account.journal from the wizard
            :return: dict of value to create() the debit note
        """
        values = {}
        type_list = ['out_invoice', 'in_invoice']

        if invoice.type not in type_list:
            raise ValidationError('Can not create Debit Note')

        for field in ['name', 'reference', 'comment', 'date_due', 'partner_id',
                      'company_id', 'account_id', 'currency_id',
                      'payment_term_id', 'user_id', 'fiscal_position_id']:
            if invoice._fields[field].type == 'many2one':
                values[field] = invoice[field].id
            else:
                values[field] = invoice[field] or False

        values['invoice_line_ids'] = self._debitnote_cleanup_lines(
                (invoice.invoice_line_ids))
        tax_lines = filter(lambda l: l['manual'], invoice.tax_line_ids)
        tax_lines = self._debitnote_cleanup_lines(tax_lines)

        if journal_id:
            debitnote_journal = self.env['account.journal'].browse(
                (journal_id))
        elif invoice['type'] == 'in_invoice':
            debitnote_journal = self.env['account.journal'].search(
                [('type', '=', 'purchase_debitnote')], limit=1)
        else:
            debitnote_journal = self.env['account.journal'].search(
                [('type', '=', 'sale_debitnote')], limit=1)

        values['journal_id'] = debitnote_journal.id
        values['type'] = invoice['type']
        values['date_invoice'] = date_invoice or fields.Date.context_today(
                (invoice))
        values['state'] = 'draft'
        values['number'] = False
        values['origin'] = invoice.number
        values['payment_term_id'] = False
        values['debit_invoice_id'] = invoice.id

        if date:
            values['date'] = date
        if description:
            values['name'] = description
        return values

        @api.multi
        @api.depends('journal_id', 'journal_id.type')
        def _compute_is_debitnote(self):
            for invoice in self:
                if invoice.journal_id and invoice.journal_id.type in (
                        'sale_debitnote', 'purchase_debitnote'):
                    invoice.is_debitnote = True
                else:
                    invoice.is_debitnote = False

    @api.multi
    @api.returns('self')
    def debitnote(self, date_invoice=None, date=None,
                  description=None, journal_id=None):
        new_invoice = []
        for invoice in self:
            invoice = self._prepare_debitnote(
                invoice,
                date_invoice=date_invoice,
                date=date,
                description=description,
                journal_id=journal_id
            )
            new_invoice = self.create(invoice)
        return new_invoice
