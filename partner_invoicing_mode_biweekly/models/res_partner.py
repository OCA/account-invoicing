# Copyright 2026 PlanetaTIC - Marc Poch <mpoch@planetatic.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoicing_mode = fields.Selection(
        selection_add=[("biweekly", "Biweekly")],
        ondelete={"biweekly": "set default"},
    )
