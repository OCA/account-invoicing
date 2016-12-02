# -*- coding: utf-8 -*-
# © 2012-2016 SYLEAM Info Services (<http://www.syleam.fr/>)
# © 2015-2016 Akretion (http://www.akretion.com)
# @author: Sébastien LANGE <sebastien.lange@syleam.fr>
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def inv_line_characteristic_hashcode(self, invoice_line):
        """Inherit the native method that generate hashcodes for grouping.
        When grouping per account, we remove the product_id from
        the hashcode.
        WARNING: I suppose that the other methods that inherit this
        method add data on the end of the hashcode, not at the beginning.
        This is the case of github/OCA/account-closing/
        account_cutoff_prepaid/account.py"""
        res = super(AccountInvoice, self).inv_line_characteristic_hashcode(
            invoice_line)
        if self.journal_id.group_method == 'account':
            hash_list = res.split('-')
            # remove product_id from hashcode
            hash_list.pop(2)
            res = '-'.join(hash_list)
        return res

    @api.model
    def line_get_convert(self, line, part):
        res = super(AccountInvoice, self).line_get_convert(line, part)
        if (
                self.journal_id.group_invoice_lines and
                self.journal_id.group_method == 'account'):
            res['name'] = '/'
            res['product_id'] = False
        return res
