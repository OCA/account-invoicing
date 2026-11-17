# Copyright 2026 Tecnativa - Andrii Kompaniiets
# License AGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = ["product.name.visibility.mixin", "account.move.line"]
