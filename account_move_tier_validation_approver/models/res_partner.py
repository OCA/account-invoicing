# Copyright 2021 ForgeFlow, S.L.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    approver_id = fields.Many2one("res.users", string="Approver of Vendor Bills")
