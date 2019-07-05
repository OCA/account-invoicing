# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def post(self, invoice=False):
        self = self.with_context(ctx_invoice=invoice)
        return super().post(invoice=invoice)
