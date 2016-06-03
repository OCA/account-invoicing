# -*- coding: utf-8 -*-
#    Copyright (C) 2011 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>).
# © 2016 Lorenzo Battistini - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

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
            seq_id = self.pool['ir.sequence'].create(cr, uid, {
                'name': 'Sezionale Corrispettivi',
                'padding': 3,
                'prefix': 'COJ/%(year)s/',
            })
            self.pool['account.journal'].create(cr, uid, {
                'code': 'COJ',
                'name': 'Sezionale Corrispettivi',
                'type': 'sale',
                'corrispettivi': True,
                'sequence_id': seq_id,
                'default_credit_account_id': o.default_credit_account_id.id,
                'default_debit_account_id': o.default_debit_account_id.id,
            })
            self.pool['res.partner'].create(cr, uid, {
                'name': 'Corrispettivi',
                'ref': 'COJ',
                'customer': False,
                'supplier': False,
                'corrispettivi': True,
            })
