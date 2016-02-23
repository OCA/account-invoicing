# -*- coding: utf-8 -*-

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_account_deposit_customer = fields.Many2one(
        'account.account',
        string="Account Advance Customer",
        company_dependent=True,
        view_load=True,
        domain=[('type', '!=', 'view')],
        required=True,
        readonly=True,
        help="This account will be used instead of the "
        "default one as the advance account for the current partner")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
