# Copyright 2023 Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    svl_warn_msg = fields.Text(compute="_compute_svl_warn_msg")

    @api.depends("invoice_line_ids.stock_valuation_ok")
    def _compute_svl_warn_msg(self):
        for invoice in self:
            svl_warn_msg = False
            if invoice.state == "draft" and invoice.invoice_line_ids.filtered(
                lambda l: not l.stock_valuation_ok
            ):
                svl_warn_msg = _(
                    "Warning: in this invoice, there are lines that have a unit price "
                    "that is different from that of the purchase order ! "
                    "The stock valuation as well as the purchase price of the product "
                    "will be updated when the invoice is validated."
                )
            invoice.svl_warn_msg = svl_warn_msg

    def action_post(self):
        res = super().action_post()
        for invoice in self:
            if invoice.move_type == "in_invoice":
                for line in invoice.invoice_line_ids.filtered(
                    lambda l: not l.stock_valuation_ok
                ):
                    line._update_product_standard_price()
                    line._create_in_svl()
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    stock_valuation_ok = fields.Boolean(
        string="Stock valuation is ok ?", compute="_compute_stock_valuation_ok"
    )

    @api.depends("price_unit", "purchase_line_id", "purchase_line_id.price_unit")
    def _compute_stock_valuation_ok(self):
        for line in self:
            stock_valuation_ok = True
            svl = (
                self.env["stock.valuation.layer"]
                .sudo()
                .search(
                    [
                        ("product_id", "=", line.product_id.id),
                        ("account_move_id", "=", line.move_id.id),
                        ("company_id", "=", line.company_id.id),
                    ]
                )
            )
            if (
                not svl
                and line.purchase_line_id
                and line.price_unit != line.purchase_line_id.price_unit
            ):
                stock_valuation_ok = False
            line.stock_valuation_ok = stock_valuation_ok

    def _prepare_common_svl_vals(self):
        self.ensure_one()
        return {
            "account_move_id": self.move_id.id,
            "company_id": self.company_id.id,
            "product_id": self.product_id.id,
            "description": "%s - %s" % (self.move_id.name, self.product_id.name)
            or self.product_id.name,
        }

    def _create_in_svl(self):
        for line in self:
            line = line.with_company(line.company_id)
            svl_vals = line.product_id._prepare_in_svl_vals(
                line.quantity, line.price_unit
            )
            svl_vals.update(line._prepare_common_svl_vals())
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
                    added_value_svls + line.price_unit
                ) / (total_qty_svls + line.quantity)
