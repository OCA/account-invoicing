# -*- coding: utf-8 -*-
# © 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp import api, SUPERUSER_ID


def post_init_hook(cr, pool):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for line in env['account.invoice.line'].search([]):
        line.write({
            'move_line_ids': [
                (4, move_line.id)
                for move_line in line._find_move_line()
            ],
        })
