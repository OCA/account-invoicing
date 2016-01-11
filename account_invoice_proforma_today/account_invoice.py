# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2015 OpenERP s.a. (<http://openerp.com>).
#    Copyright (C) 2015 initOS GmbH (<http://www.initos.com>).
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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import date


class account_invoice(orm.Model):
    _inherit = 'account.invoice'

    def action_date_assign(self, cr, uid, ids, *args):
        ids_to_change = []
        for inv in self.browse(cr, uid, ids):
            if inv.state == "proforma2":
                ids_to_change.append(inv.id)
        if ids_to_change:
            data = {
                'date_invoice':
                    date.today().strftime(DEFAULT_SERVER_DATE_FORMAT),
            }
            self.write(cr, uid, ids_to_change, data)
        return super(account_invoice, self).action_date_assign(cr, uid, ids, *args)
