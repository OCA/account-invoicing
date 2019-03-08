# Copyright 2019 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from odoo.addons.account.models.account_invoice import TYPE2REFUND


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    @api.returns('self')
    def refund_partial(self, date_invoice=None, date=None, description=None,
                       journal_id=None, lines_id=None):
        new_invoices = self.browse()
        for invoice in self:
            # create the new invoice
            values = self._prepare_refund_partial(invoice,
                                                  date_invoice=date_invoice,
                                                  date=date,
                                                  description=description,
                                                  journal_id=journal_id,
                                                  lines_id=lines_id)
            refund_invoice = self.create(values)
            refund_invoice.compute_taxes()
            invoice_type = {'out_invoice': 'customer invoices credit note',
                            'in_invoice': 'vendor bill credit note'}
            message = _("This %s has been created from: "
                        "<a href=# data-oe-model=account.invoice "
                        "data-oe-id=%d>%s</a>") % (invoice_type[invoice.type],
                                                   invoice.id, invoice.number)
            refund_invoice.message_post(body=message)
            new_invoices += refund_invoice
        return new_invoices

    @api.model
    def _prepare_refund_partial(self, invoice, date_invoice=None,
                                date=None, description=None, journal_id=None,
                                lines_id=None):
        values = {}
        for field in self._get_refund_copy_fields():
            if invoice._fields[field].type == 'many2one':
                values[field] = invoice[field].id
            else:
                values[field] = invoice[field] or False

        values['invoice_line_ids'] = self._refund_cleanup_lines(lines_id)
        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
        elif invoice['type'] == 'in_invoice':
            journal = self.env['account.journal'].search(
                [('type', '=', 'purchase')], limit=1)
        else:
            journal = self.env['account.journal'].search(
                [('type', '=', 'sale')], limit=1)
        values['journal_id'] = journal.id

        values['type'] = TYPE2REFUND[invoice['type']]
        values['date_invoice'] = date_invoice or fields.Date.context_today(
            invoice)
        values['state'] = 'draft'
        values['number'] = False
        values['origin'] = invoice.number
        values['payment_term_id'] = False
        values['refund_invoice_id'] = invoice.id

        if date:
            values['date'] = date
        if description:
            values['name'] = description
        return values
