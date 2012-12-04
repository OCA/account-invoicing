# -*- coding: utf-8 -*-
##############################################################################
#
#    account_group_invoice_lines module for OpenERP, Change method to group invoice lines in account
#    Copyright (C) 2012 SYLEAM Info Services (<http://www.syleam.fr/>)
#              Sebastien LANGE <sebastien.lange@syleam.fr>
#
#    This file is a part of account_group_invoice_lines
#
#    account_group_invoice_lines is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    account_group_invoice_lines is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv


class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    def inv_line_characteristic_hashcode(self, invoice, invoice_line):
        """Overridable hashcode generation for invoice lines. Lines having the same hashcode
        will be grouped together if the journal has the 'group line' option. Of course a module
        can add fields to invoice lines that would need to be tested too before merging lines
        or not."""
        return "%s-%s-%s-%s"%(
            invoice_line['account_id'],
            invoice_line.get('tax_code_id',"False"),
            invoice_line.get('analytic_account_id',"False"),
            invoice_line.get('date_maturity',"False"))

account_invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
