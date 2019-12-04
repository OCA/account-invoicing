# Copyright 2018 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, SUPERUSER_ID, tools


def pre_init_hook(cr):
    if not tools.config.options.get('without_demo', False):
        env = api.Environment(cr, SUPERUSER_ID, {})
        env['ir.module.module'].search([
            ('name', 'in', ['purchase_stock', 'sale_stock']),
            ('state', '!=', 'installed'),
        ]).write({'state': 'to install'})
