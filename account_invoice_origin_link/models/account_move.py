# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    origin_reference = fields.Reference(
        selection="_selection_reference_model",
        compute="_compute_source_doc_ref",
        readonly=True,
        string="Source Document",
    )

    def _selection_reference_model(self):
        return []

    @api.depends("invoice_origin")
    def _compute_source_doc_ref(self):
        for rec in self:
            rec.origin_reference = False
