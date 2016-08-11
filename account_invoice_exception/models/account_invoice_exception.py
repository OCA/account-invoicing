# -*- coding: utf-8 -*-
# © 2016 Raphaël Valyi, Renato Lima, Guewen Baconnier, Sodexis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time

from openerp import api, models, fields
from openerp.exceptions import except_orm
from openerp.tools.safe_eval import safe_eval
from openerp.tools.translate import _


class AccountInvoiceException(models.Model):
    _name = 'account.invoice.exception'
    _description = "Account Invoice Exceptions"
    _order = 'active desc, sequence asc'

    name = fields.Char(
        'Exception Name',
        required=True,
        translate=True
    )
    description = fields.Text(
        'Description',
        translate=True
    )
    sequence = fields.Integer(
        string='Sequence',
        help="Gives the sequence order when applying the test"
    )
    model = fields.Selection(
        [('account.invoice', 'Invoice'),
         ('account.invoice.line', 'Invoice Line')],
        string='Apply on',
        required=True
    )
    active = fields.Boolean(
        string='Active'
    )
    code = fields.Text(
        'Python Code',
        help="Python code executed to check if the exception apply or "
             "not. The code must apply block = True to apply the "
             "exception.",
        default="""
# Python code. Use failed = True to block the invoice.
# You can use the following variables :
#  - self: ORM model of the record which is checked
#  - invoice or line: browse_record of the invoice or invoice line
#  - object: same as order or line, browse_record of the invoice or
#    invoice line
#  - pool: ORM model pool (i.e. self.pool)
#  - time: Python time module
#  - cr: database cursor
#  - uid: current user id
#  - context: current context
""")
    invoice_ids = fields.Many2many(
        'account.invoice',
        'account_invoice_exception_rel',
        'exception_id',
        'invoice_id',
        string='Invoices',
        readonly=True)
