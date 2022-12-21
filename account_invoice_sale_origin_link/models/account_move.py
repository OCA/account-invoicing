# Copyright 2022 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _selection_reference_model(self):
        res = super()._selection_reference_model() + [("sale.order", "Sale Order")]
        return res

    @api.model
    def _get_depends_compute_source_doc_ref(self):
        res = super()._get_depends_compute_source_doc_ref()
        res.append("line_ids.sale_line_ids.order_id")
        return res

    @api.depends(lambda x: x._get_depends_compute_source_doc_ref())
    def _compute_source_doc_ref(self):
        super()._compute_source_doc_ref()
        for rec in self.filtered(lambda line: line.move_type == "out_invoice"):
            so = rec.line_ids.mapped("sale_line_ids.order_id")
            if len(so) == 1:
                rec.origin_reference = "{},{}".format(so._name, so.id or 0)
