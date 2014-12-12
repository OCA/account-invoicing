# -*- encoding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Savoir-faire Linux
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


class AccountInvoice(orm.Model):
    _inherit = "account.invoice"

    def create(self, cr, uid, values, context=None):
        if "partner_id" in values and not values.get("section_id"):
            part = self.pool["res.partner"].browse(
                cr, uid, values["partner_id"], context=context)
            if part.section_id:
                values["section_id"] = part.section_id.id

        return super(AccountInvoice, self).create(cr, uid, values,
                                                  context=context)

    def onchange_partner_id(self, cr, uid, ids, type, partner_id,
                            date_invoice=False, payment_term=False,
                            partner_bank_id=False, company_id=False,
                            context=None):
        # Original call doesn't handle context, do not pass it
        res = super(AccountInvoice, self).onchange_partner_id(
            cr, uid, ids, type, partner_id,
            date_invoice=date_invoice, payment_term=payment_term,
            partner_bank_id=partner_bank_id, company_id=company_id)

        part = self.pool["res.partner"].browse(cr, uid, partner_id,
                                               context=context)
        values = res.setdefault("value", {})
        if part.section_id:
            values["section_id"] = part.section_id.id
        else:
            values["section_id"] = False

        return res
