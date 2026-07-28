from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _filter_paid_lines_for_invoicing(self):
        return self.filtered(
            lambda line: line.state == "sale"
            and line.order_id._is_paid()
            and not line._is_delivery_started()
        )

    def _is_delivery_started(self):
        """Check if the delivery of the line has been started,
        i.e. if there is at least one done move."""
        return any(move.state == "done" for move in self.move_ids)

    @api.depends("order_id.transaction_ids.state")
    def _compute_qty_to_invoice(self):
        paid_lines = self._filter_paid_lines_for_invoicing()
        for line in paid_lines:
            line.qty_to_invoice = line.product_uom_qty - line.qty_invoiced
        self -= paid_lines
        return super()._compute_qty_to_invoice()

    @api.depends("order_id.transaction_ids.state")
    def _compute_amount_to_invoice(self):
        paid_lines = self._filter_paid_lines_for_invoicing()
        for line in paid_lines:
            # Compute the field based on product_uom_qty instead of qty_delivered.
            if line.product_uom_qty:
                uom_qty_to_consider = line.product_uom_qty
                qty_to_invoice = uom_qty_to_consider - line.qty_invoiced_posted
                unit_price_total = line.price_total / line.product_uom_qty
                line.amount_to_invoice = unit_price_total * qty_to_invoice
            else:
                line.amount_to_invoice = 0.0
        self -= paid_lines
        return super()._compute_amount_to_invoice()

    @api.depends("order_id.transaction_ids.state")
    def _compute_untaxed_amount_to_invoice(self):
        paid_lines = self._filter_paid_lines_for_invoicing().filtered(
            lambda line: line.product_id.invoice_policy == "delivery"
        )
        self -= paid_lines
        # Adapted from sale.order.line._compute_untaxed_amount_to_invoice (upstream),
        # using product_uom_qty instead of qty_delivered for paid delivery-policy lines.
        for line in paid_lines:
            price_reduce = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            price_subtotal = price_reduce * line.product_uom_qty
            if line.tax_id.filtered(lambda t: t.price_include):
                price_subtotal = line.tax_id.compute_all(
                    price_reduce,
                    currency=line.currency_id,
                    quantity=line.product_uom_qty,
                    product=line.product_id,
                    partner=line.order_id.partner_shipping_id,
                )["total_excluded"]
            line.untaxed_amount_to_invoice = (
                price_subtotal - line.untaxed_amount_invoiced
            )
        return super()._compute_untaxed_amount_to_invoice()
