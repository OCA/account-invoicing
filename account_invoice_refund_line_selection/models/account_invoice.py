# Copyright 2019 Creu Blanca
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models, _


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    @api.returns('self')
    def refund_partial(self, date_invoice=None, date=None, description=None,
                       journal_id=None, lines_id=None):
        new_invoices = self.browse()
        for invoice in self:
            # create the new invoice
            values = self._prepare_refund_partial(
                invoice, date_invoice=date_invoice, date=date,
                description=description, journal_id=journal_id,
                lines_id=lines_id
            )
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
        values = self._prepare_refund(
            invoice,
            date_invoice=date_invoice,
            date=date,
            description=description,
            journal_id=journal_id
        )
        values['invoice_line_ids'] = self._refund_cleanup_lines(lines_id)
        return values
