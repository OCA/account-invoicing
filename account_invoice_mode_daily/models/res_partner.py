# Copyright 2022 manaTec GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    invoicing_mode = fields.Selection(
        selection_add=[("daily", "Daily")],
        ondelete={"daily": "set default"},
    )
