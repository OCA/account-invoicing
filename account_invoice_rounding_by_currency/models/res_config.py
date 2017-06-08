# -*- coding: utf-8 -*-
# Copyright 2015 Alessio Gerace <alessio.gerace@agilebg.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def _default_company(self):
        return self.env.user.company_id.id

    company_id = fields.Many2one(
        'res.company', 'Company', required=True, default=_default_company)
    currency_rounding_rules = fields.One2many(
        related='company_id.currency_rounding_rules',
        string='Rounding Rule',
        domain=[('type', '<>', 'view')])

    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        res = super(AccountConfigSettings, self
                    ).onchange_company_id(cr, uid, ids,
                                          company_id, context=context)
        company = self.pool.get('res.company').browse(cr, uid, company_id,
                                                      context=context)
        res['value']['currency_rounding_rules'] = \
            company.currency_rounding_rules
        return res
