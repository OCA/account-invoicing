# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
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
##############################################################################
from openerp.osv import orm


class accountInvoice(orm.Model):
    _inherit = 'account.invoice'

    def onchange_partner_id(
            self, cr, uid, ids, type, partner_id,
            date_invoice=False, payment_term=False,
            partner_bank_id=False, company_id=False):
        """
        When selecting a partner that is not of type 'invoice', replace
        the partner by an invoice contact if found.
        """
        if partner_id:
            partner_obj = self.pool.get('res.partner')
            partner = partner_obj.read(cr, uid, partner_id, ['type'])
            if partner['type'] != 'invoice':
                partner_ids = partner_obj.search(
                    cr, uid, [
                        ('type', '=', 'invoice'),
                        ('id', 'child_of', partner_id),
                        ])
                if partner_ids:
                    # Not calling super here on purpose, because
                    # we change the partner_id
                    res = self.onchange_partner_id(
                        cr, uid, ids, type, partner_ids[0],
                        date_invoice=date_invoice, payment_term=payment_term,
                        partner_bank_id=partner_bank_id, company_id=company_id)
                    if res and 'value' in res:
                        res['value']['partner_id'] = partner_ids[0]
                    return res
        return super(accountInvoice, self).onchange_partner_id(
            cr, uid, ids, type, partner_id,
            date_invoice=date_invoice, payment_term=payment_term,
            partner_bank_id=partner_bank_id, company_id=company_id)
