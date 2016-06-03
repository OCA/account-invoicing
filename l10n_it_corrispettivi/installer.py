# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv
from openerp import fields


class CorrispettiviConfigData(osv.osv_memory):
    _name = 'corrispettivi.config.data'
    _inherit = 'res.config'

    default_credit_account_id = fields.Many2one(
        'account.account', 'Default credit account',
        domain=[('type', '!=', 'view')],
        required=True, help='If doubtful, use income account')
    default_debit_account_id = fields.Many2one(
        'account.account', 'Default debit account',
        domain=[('type', '!=', 'view')],
        required=True, help='If doubtful, use income account')

    def execute(self, cr, uid, ids, context=None):
        for o in self.browse(cr, uid, ids, context=context):
            seq_id = self.env['ir.sequence'].create(cr, uid, {
                'name': 'Sezionale Corrispettivi',
                'padding': 3,
                'prefix': 'COJ/%(year)s/',
            })
            journal_id = self.env['account.journal'].create(cr, uid, {
                'code': 'COJ',
                'name': 'Sezionale Corrispettivi',
                'type': 'sale',
                'corrispettivi': True,
                'sequence_id': seq_id,
                'default_credit_account_id': o.default_credit_account_id.id,
                'default_debit_account_id': o.default_debit_account_id.id,
            })
            partner_id = self.env['res.partner'].create(cr, uid, {
                'name': 'Corrispettivi',
                'ref': 'COJ',
                'customer': False,
                'supplier': False,
                'corrispettivi': True,
            })
