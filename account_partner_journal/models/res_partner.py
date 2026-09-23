# Copyright 2016-Today: La Louve (<http://www.lalouve.net/>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    default_purchase_journal_id = fields.Many2one(
        "account.journal",
        "Default Purchase Journal",
        compute="_compute_purchase_journal_id",
        readonly=False,
        store=True,
        company_dependent=True,
        recursive=True,
        domain="[('type', '=', 'purchase')]",
    )

    @api.depends("parent_id.default_purchase_journal_id")
    def _compute_purchase_journal_id(self):
        for partner in self:
            if partner.parent_id.default_purchase_journal_id:
                partner.default_purchase_journal_id = (
                    partner.parent_id.default_purchase_journal_id
                )
            else:
                partner.default_purchase_journal_id = False
