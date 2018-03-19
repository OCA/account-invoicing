# -*- coding: utf-8 -*-
# © 2012-2016 SYLEAM Info Services (<http://www.syleam.fr/>)
# © 2015-2016 Akretion (http://www.akretion.com)
# @author: Sébastien LANGE <sebastien.lange@syleam.fr>
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def line_get_convert(self, line, part):
        res = super(AccountInvoice, self).line_get_convert(line, part)
        if line.get('invoice_id'):
            inv = self.browse(line['invoice_id'])
            jrl = inv.journal_id
            if jrl.group_invoice_lines and jrl.group_method == 'account':
                res['name'] = '/'
                res['product_id'] = False
        return res
