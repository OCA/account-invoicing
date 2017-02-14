# -*- coding: utf-8 -*-
# © 2012-2016 SYLEAM Info Services (<http://www.syleam.fr/>)
# © 2015-2016 Akretion (http://www.akretion.com)
# @author: Sébastien LANGE <sebastien.lange@syleam.fr>
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    group_method = fields.Selection([
        ('product', 'By Product'),
        ('account', 'By Account')
        ], string='Group by', default='account',
        help="If you select 'By Product', the account move lines generated "
        "when you validate an invoice will be "
        "grouped by product, account, analytic account and tax code. "
        "If you select 'By Account', they will be grouped by account, "
        "analytic account and tax code, without taking into account "
        "the product.")
