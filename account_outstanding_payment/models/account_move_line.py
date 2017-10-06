# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def remove_move_reconcile(
            self,
            move_ids=None,
            opening_reconciliation=False):
        return self._remove_move_reconcile(move_ids, opening_reconciliation)
