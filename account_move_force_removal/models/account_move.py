# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def unlink(self):
        return super(AccountMove, self.with_context(force_delete=True)).unlink()
