# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# © 2017 Odoo SA <https://www.odoo.com>
# © 2017 OCA <https://odoo-community.org>
# License LGPL-3 (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from openerp import fields, models, api


class AccountConfigSettings(models.Model):
    _inherit = 'account.config.settings'

    reconciliation_writeoff_account = fields.Many2one('account.account',
                                                      'Write-Off account',
                                                      required=True)

    @api.model
    def get_reconciliation_writeoff_account(self):
        ir_values_obj = self.env['ir.values']
        return {'reconciliation_writeoff_account': ir_values_obj.get_default(
            'account.config.settings', 'reconciliation_writeoff_account')}

    @api.multi
    def set_reconciliation_writeoff_account(self):
        for record in self:
            ir_values_obj = self.env['ir.values']
            ir_values_obj.set_default('account.config.settings',
                                      'reconciliation_writeoff_account',
                                      record.
                                      reconciliation_writeoff_account.id)
