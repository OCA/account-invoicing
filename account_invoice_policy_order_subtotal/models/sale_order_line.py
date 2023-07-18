# Copyright 2022 Camptocamp SA <telmo.santos@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    amount_invoiced = fields.Float(
        compute="_compute_amount_invoiced",
        string="Invoiced Amount",
        store=True,
        readonly=True,
        compute_sudo=True,
        digits="Product Price",
    )
    amount_to_invoice = fields.Float(
        compute="_compute_amount_to_invoice",
        string="To Invoice Amount",
        store=True,
        readonly=True,
        compute_sudo=True,
        digits="Product Price",
    )

    def _get_policy_order_subtotal_lines(self):
        return self.filtered(
            lambda line: line.product_id.type == "consu"
            and line.product_id.invoice_policy == "order_subtotal"
        )

    @api.depends("invoice_lines.move_id.state", "invoice_lines.price_subtotal")
    def _compute_amount_invoiced(self):
        for sol in self:
            amount_invoiced = 0.0
            for inv_line in sol.invoice_lines:
                if inv_line.parent_state in ("draft", "posted"):
                    amount_invoiced -= inv_line.amount_currency
            sol.amount_invoiced = amount_invoiced

    @api.depends("amount_invoiced", "price_subtotal")
    def _compute_amount_to_invoice(self):
        for sol in self:
            sol.amount_to_invoice = sol.price_subtotal - sol.amount_invoiced

    @api.depends("qty_invoiced", "qty_delivered", "product_uom_qty", "order_id.state")
    def _get_to_invoice_qty(self):
        subtot_policy_lns = self._get_policy_order_subtotal_lines()
        for line in subtot_policy_lns:
            line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
        super(SaleOrderLine, self - subtot_policy_lns)._get_to_invoice_qty()

    @api.depends(
        "invoice_lines.move_id.state",
        "invoice_lines.quantity",
        "invoice_lines.price_subtotal",
    )
    def _get_invoice_qty(self):
        subtot_policy_lns = self._get_policy_order_subtotal_lines()
        for line in subtot_policy_lns:
            if line.price_subtotal:
                line.qty_invoiced = (
                    line.product_uom_qty * line.amount_invoiced / line.price_subtotal
                )
            else:
                line.qty_invoiced = 0.0
        super(SaleOrderLine, self - subtot_policy_lns)._get_invoice_qty()

    @api.depends("product_id")
    def _compute_qty_delivered_method(self):
        subtot_policy_lns = self._get_policy_order_subtotal_lines()
        for line in subtot_policy_lns:
            line.qty_delivered_method = False
        super(SaleOrderLine, self - subtot_policy_lns)._compute_qty_delivered_method()

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        if (
            self.product_id.type == "consu"
            and self.product_id.invoice_policy == "order_subtotal"
        ):
            # We set the quantity to ordered quantity and
            # let the user decide how much he wants to invoice
            res.update(
                {
                    "quantity": self.product_uom_qty,
                    "price_unit": 0,
                }
            )
        return res

    @api.depends(
        "state",
        "product_uom_qty",
        "qty_delivered",
        "qty_to_invoice",
        "qty_invoiced",
        "amount_invoiced",
    )
    def _compute_invoice_status(self):
        precision = self.env["decimal.precision"].precision_get("Product Price")
        subtot_policy_lns = self._get_policy_order_subtotal_lines()
        for line in subtot_policy_lns:
            if line.state not in ("sale", "done"):
                line.invoice_status = "no"
            elif (
                float_compare(
                    abs(line.price_subtotal),
                    abs(line.amount_invoiced),
                    precision_digits=precision,
                )
                > 0
            ):
                line.invoice_status = "to invoice"
            elif (
                float_compare(
                    abs(line.price_subtotal),
                    abs(line.amount_invoiced),
                    precision_digits=precision,
                )
                <= 0
            ):
                line.invoice_status = "invoiced"
            else:
                line.invoice_status = "no"
        super(SaleOrderLine, self - subtot_policy_lns)._compute_invoice_status()
