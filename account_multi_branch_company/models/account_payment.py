# Copyright 2023 Ecosoft Co., Ltd (https://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    branch_id = fields.Many2one(
        comodel_name="res.branch",
        compute="_compute_journal_branch",
        store=True,
        readonly=False,
        tracking=True,
    )

    @api.depends("journal_id")
    def _compute_journal_branch(self):
        for rec in self:
            rec.branch_id = rec.journal_id.branch_id.id
