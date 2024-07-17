# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    invoice_section_grouping = fields.Selection(
        selection_add=[("delivery_picking", "Group by delivery picking")],
        ondelete={"delivery_picking": "set default"},
    )
