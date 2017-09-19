# -*- coding: utf-8 -*-
# © 2017 Elico Corp (https://www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'base.kanban.abstract']
    _order = 'date_due asc'

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = default or {}
        stage = self.stage_id.search([], order="sequence asc", limit=1)
        default.update({'stage_id': stage.id})
        return super(AccountInvoice, self).copy(default=default)
