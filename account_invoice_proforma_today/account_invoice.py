# -*- coding: utf-8 -*-
# © initOS GmbH 2016
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
            data = {'date_invoice': date.today().
                    strftime(DEFAULT_SERVER_DATE_FORMAT),
                    }
            self.write(cr, uid, ids_to_change, data)
        return super(account_invoice, self).\
            action_date_assign(cr, uid, ids, *args)
