# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.tools import float_compare


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"
    supplier_product_code = fields.Char(readonly=True)
    purchase_line_mismatch = fields.Boolean(
        compute="_compute_purchase_line_mismatch",
        help="Checked when this invoice line does not fully match its related purchase"
        " order line.",
    )
    purchase_line_mismatch_details = fields.Text(
        compute="_compute_purchase_line_mismatch",
        help="Human-readable description of the differences between this invoice line"
        " and the related purchase order line.",
    )

    @api.depends(
        "purchase_line_id", "move_id.state", "price_unit", "price_subtotal", "quantity"
    )
    def _compute_purchase_line_mismatch(self):
        for rec in self:
            if not rec.purchase_line_id or rec.move_id.state != "draft":
                rec.purchase_line_mismatch = False
                rec.purchase_line_mismatch_details = False
                continue

            differences = []
            po_line = rec.purchase_line_id
            precision = rec.currency_id.rounding or 0.01
            if (
                float_compare(
                    rec.price_unit,
                    po_line.price_unit,
                    precision_rounding=precision,
                )
                != 0
            ):
                differences.append(
                    _("- Unit price differs from the purchase order line.")
                )
            if (
                float_compare(
                    po_line.qty_invoiced,
                    po_line.product_uom_qty,
                    precision_rounding=po_line.product_uom.rounding or 0.01,
                )
                > 0
            ):
                differences.append(
                    _("- Invoiced quantity exceeds the ordered quantity.")
                )
            if differences:
                rec.purchase_line_mismatch = True
                rec.purchase_line_mismatch_details = "\n".join(differences)
            else:
                rec.purchase_line_mismatch = False
                rec.purchase_line_mismatch_details = False

    def _update_product_supplier_name(self):
        for rec in self:
            if not rec.name or not rec.product_id:
                continue
            seller = rec.product_id.seller_ids.filtered(
                lambda s: s.partner_id == rec.move_id.partner_id
                and (
                    s.product_id == rec.product_id
                    or s.product_tmpl_id == rec.product_id.product_tmpl_id
                )
            )
            if not seller:
                rec.product_id.seller_ids.create(
                    {
                        "product_id": rec.product_id.id,
                        "product_name": rec.name,
                        "product_code": rec.supplier_product_code,
                        "price": rec.price_unit,
                    }
                )
            else:
                seller.product_name = rec.name
                if rec.supplier_product_code:
                    seller.product_code = rec.supplier_product_code

    def action_select_purchase_line(self):
        self.ensure_one()
        if self.purchase_line_id:
            purchase_order = self.purchase_line_id.order_id
        else:
            order_ref = self.move_id.invoice_origin
            purchase_order = self.env["purchase.order"].search(
                [
                    "|",
                    ("name", "=", order_ref),
                    ("partner_ref", "=", order_ref),
                    ("state", "in", ("purchase", "done")),
                ]
            )
        context = {
            **self.env.context,
            **{
                "default_move_line_id": self.id,
                "default_purchase_order_id": purchase_order.id
                if purchase_order
                else False,
            },
        }
        return {
            "type": "ir.actions.act_window",
            "name": "Select Purchase Line",
            "res_model": "account.move.line.select.purchase.line.wizard",
            "view_mode": "form",
            "target": "new",
            "context": context,
        }

    def action_show_purchase_line(self):
        self.ensure_one()
        if not self.purchase_line_id:
            return {}
        form = self.env.ref(
            "account_edi_ubl_cii_purchase_match.purchase_order_line_form_view"
        )
        return {
            "type": "ir.actions.act_window",
            "name": self.purchase_line_id.display_name,
            "res_model": self.purchase_line_id._name,
            "view_mode": "form",
            "views": [(form.id, "form")],
            "view_id": form.id,
            "res_id": self.purchase_line_id.id,
            "target": "new",
            "context": self.env.context,
        }

    def _set_product(self, product):
        self.ensure_one()
        price_unit = self.price_unit
        self.product_id = product
        self.price_unit = price_unit
