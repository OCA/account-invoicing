# -*- coding: utf-8 -*-
# © 2011 Domsense srl (<http://www.domsense.com>)
# © 2011-2016 Agile Business Group sagl (<http://www.agilebg.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    internal_number = fields.Char(
        'Force Number',
        help="Force invoice number. Use this field if you don't want to use "
             "the default numbering")


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, vals):
        invoice = self.env.context.get('invoice', False)
        if invoice and invoice.internal_number:
            vals['name'] = invoice.internal_number
        return super(AccountMove, self).create(vals)
