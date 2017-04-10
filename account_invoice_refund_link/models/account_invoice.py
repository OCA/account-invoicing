# -*- coding: utf-8 -*-
# Copyright 2004-2011 Pexego Sistemas Informáticos. (http://pexego.es)
# Copyright 2016 Antonio Espinosa <antonio.espinosa@tecnativa.com>
# Copyright 2014-2017 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    refund_reason = fields.Text(string="Refund reason")
    origin_invoice_ids = fields.Many2many(
        comodel_name='account.invoice', column1='refund_invoice_id',
        column2='original_invoice_id', relation='account_invoice_refunds_rel',
        string="Original invoice", readonly=True,
        help="Original invoice to which this refund invoice is referred to")
    refund_invoice_ids = fields.Many2many(
        comodel_name='account.invoice', column1='original_invoice_id',
        column2='refund_invoice_id', relation='account_invoice_refunds_rel',
        string="Refund invoices",  readonly=True,
        help="Refund invoices created from this invoice")

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None,
                        description=None, journal_id=None):
        """Add link in the refund to the origin invoice and origin lines."""
        res = super(AccountInvoice, self)._prepare_refund(
            invoice, date_invoice=date_invoice, date=date,
            description=description, journal_id=journal_id,
        )
        res['origin_invoice_ids'] = [(6, 0, invoice.ids)]
        res['refund_reason'] = description
        refund_lines_vals = res['invoice_line_ids']
        for i, line in enumerate(invoice.invoice_line_ids):
            if i + 1 > len(refund_lines_vals):  # pragma: no cover
                # Avoid error if someone manipulate the original method
                break
            refund_lines_vals[i][2]['origin_line_ids'] = [(6, 0, line.ids)]
        return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    origin_line_ids = fields.Many2many(
        comodel_name='account.invoice.line', column1='refund_line_id',
        column2='original_line_id', string="Original invoice line",
        relation='account_invoice_line_refunds_rel',
        help="Original invoice line to which this refund invoice line "
             "is referred to")
    refund_line_ids = fields.Many2many(
        comodel_name='account.invoice.line', column1='original_line_id',
        column2='refund_line_id', string="Refund invoice line",
        relation='account_invoice_line_refunds_rel',
        help="Refund invoice lines created from this invoice line")
