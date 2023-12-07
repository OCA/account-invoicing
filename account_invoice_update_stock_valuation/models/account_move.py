# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    all_stock_valuation_ok = fields.Boolean(
        string="All stock valuation is ok ?",
        compute="_compute_all_stock_valuation_ok",
        store=True,
    )

    @api.depends("state", "invoice_line_ids", "invoice_line_ids.stock_valuation_ok")
    def _compute_all_stock_valuation_ok(self):
        for invoice in self:
            invoice.all_stock_valuation_ok = not (
                invoice.state == "draft"
                and invoice.invoice_line_ids.filtered(
                    lambda l: not l.stock_valuation_ok
                )
            )

    def action_post(self):
        for invoice in self:
            if invoice.move_type == "in_invoice":
                for line in invoice.invoice_line_ids.filtered(
                    lambda l: not l.stock_valuation_ok
                ):
                    line._create_in_svl()
                    line._update_product_standard_price()
        return super().action_post()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    stock_valuation_ok = fields.Boolean(
        string="Stock valuation is ok ?",
        compute="_compute_stock_valuation_ok",
        store=True,
    )

    @api.depends(
        "move_id.state",
        "price_unit",
        "product_uom_id",
        "purchase_line_id",
        "purchase_line_id.price_unit",
        "purchase_line_id.product_uom",
    )
    def _compute_stock_valuation_ok(self):
        for line in self:
            svl = (
                self.env["stock.valuation.layer"]
                .sudo()
                .search(
                    [
                        ("product_id", "=", line.product_id.id),
                        ("unit_cost", "=", line.price_unit),
                        ("quantity", "=", line.quantity),
                        ("account_move_id", "=", line.move_id.id),
                        ("company_id", "=", line.company_id.id),
                    ]
                )
            )
            if line.product_uom_id == line.purchase_line_id.product_uom:
                line_price_unit = line.price_unit
            else:
                line_price_unit = line.product_uom_id._compute_price(
                    price=line.price_unit, to_unit=line.purchase_line_id.product_uom
                )
            line.stock_valuation_ok = not (
                line.move_id.state == "draft"
                and not svl
                and line.purchase_line_id
                and line_price_unit != line.purchase_line_id.price_unit
            )

    def _prepare_common_svl_vals(self):
        self.ensure_one()
        return {
            "account_move_id": self.move_id.id,
            "company_id": self.company_id.id,
            "description": "%s - %s" % (self.move_id.name, self.product_id.name),
        }

    def _create_in_svl(self):
        for line in self:
            line = line.with_company(line.company_id)
            svl_vals = line.product_id._prepare_in_svl_vals(
                line.quantity, line.price_unit
            )
            svl_vals.update(line._prepare_common_svl_vals())
            if line.product_uom_id != line.product_id.uom_po_id:
                svl_vals["quantity"] = line.product_uom_id._compute_quantity(
                    qty=line.quantity,
                    to_unit=line.product_id.uom_po_id,
                    round=True,
                    rounding_method="UP",
                    raise_if_failure=True,
                )
                svl_vals["unit_cost"] = line.product_uom_id._compute_price(
                    price=line.price_unit, to_unit=line.product_id.uom_po_id
                )
        return self.env["stock.valuation.layer"].sudo().create(svl_vals)

    def _update_product_standard_price(self):
        for line in self:
            svls = self.env["stock.valuation.layer"].search(
                [
                    ("product_id", "=", line.product_id.id),
                    ("company_id", "=", line.company_id.id),
                ]
            )
            added_value_svls = sum(svls.mapped("value"))
            total_qty_svls = sum(svls.mapped("quantity"))
            # Update the standard price in case of AVCO
            if line.product_id.categ_id.property_cost_method == "average":
                line.product_id.with_context(disable_auto_svl=True).standard_price = (
                    added_value_svls / total_qty_svls
                )
