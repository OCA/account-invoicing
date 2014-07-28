# -*- encoding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp.osv import orm
from openerp.tools.translate import _


class AccountInvoice(orm.Model):
    _inherit = "account.invoice"

    def copy(self, cr, uid, ids, default=None, context=None):
        default = default or {}
        default.update({
            'supplier_invoice_number': '',
        })
        return super(AccountInvoice, self).copy(cr, uid, ids, default, context)

    def _check_unique_supplier_invoice_number_insensitive(self, cr, uid, ids,
                                                          context=None):
        # this function only works with one id
        if ids and len(ids) == 1:
            i_id = ids[0]
        else:
            raise orm.except_orm(
                _('Error'),
                'Cannot check unique supplier ref without id.')

        invoice = self.browse(cr, uid, i_id, context=context)
        invoice_partner = invoice.partner_id

        sr_ids = self.search(cr, uid,
                             [("partner_id", "=", invoice_partner.id)],
                             context=context)
        lst = [
            x.supplier_invoice_number.lower() for x in
            self.browse(cr, uid, sr_ids, context=context)
            if x.supplier_invoice_number and x.id not in ids
        ]
        if (invoice.supplier_invoice_number
                and invoice.supplier_invoice_number.lower() in lst):
            return False
        return True

    def _rec_message(self, cr, uid, ids, context=None):
        return _('The supplier invoice number must be unique \
                 for each supplier !')

    _constraints = [
        (_check_unique_supplier_invoice_number_insensitive,
         _rec_message,
         ['name'])
    ]
