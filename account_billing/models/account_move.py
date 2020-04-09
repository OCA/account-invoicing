# Copyright 2019 Ecosoft Co., Ltd (https://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    billing_ids = fields.Many2many(
        comodel_name="account.billing",
        string="Biilings",
        compute="_compute_billing_ids",
        help="Relationship between invoice and billing",
    )

    def _compute_billing_ids(self):
        BillLine = self.env["account.billing.line"]
        for rec in self:
            billing_lines = BillLine.search([("invoice_id", "=", rec.id)])
            rec.billing_ids = billing_lines.mapped("billing_id")
