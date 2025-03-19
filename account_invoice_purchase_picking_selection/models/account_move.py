from odoo import api, fields, models
from odoo.tools.float_utils import float_is_zero


class AccountMove(models.Model):
    _inherit = "account.move"

    autocomplete_purchase_picking_id = fields.Many2one(
        "stock.picking", copy=False, string="Auto-Complete from Picking"
    )

    @api.onchange("autocomplete_purchase_picking_id")
    def _onchange_autocomplete_purchase_picking_id(self):
        """Load from either an stock.picking."""
        if (
            not self.autocomplete_purchase_picking_id
            or not self.autocomplete_purchase_picking_id.purchase_id
        ):
            return

        # Copy data from PO
        purchase = self.autocomplete_purchase_picking_id.purchase_id
        stock_moves = self.autocomplete_purchase_picking_id.move_lines
        invoice_vals = purchase.with_company(purchase.company_id)._prepare_invoice()
        invoice_vals["currency_id"] = (
            self.line_ids and self.currency_id or invoice_vals.get("currency_id")
        )
        del invoice_vals["ref"]
        self.update(invoice_vals)

        # Copy purchase lines.
        stock_moves -= self.line_ids.mapped("stock_move_invoiced_id")
        new_lines = self.env["account.move.line"]
        sequence = max(self.line_ids.mapped("sequence")) + 1 if self.line_ids else 10
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        for stock_move in stock_moves:
            if float_is_zero(
                stock_move.qty_received_to_invoice, precision_digits=precision
            ):
                continue
            line_vals = stock_move._prepare_account_move_line_from_stock(self, sequence)
            new_line = new_lines.new(line_vals)
            sequence += 1
            new_line.account_id = new_line._get_computed_account()
            new_line._onchange_price_subtotal()
            new_lines += new_line
        new_lines._onchange_mark_recompute_taxes()
        new_lines.picking_invoiced_id = self.autocomplete_purchase_picking_id

        # Compute invoice_origin.
        origins = set(self.line_ids.mapped("purchase_line_id.order_id.name"))
        self.invoice_origin = ",".join(list(origins))

        # Compute ref.
        refs = self._get_invoice_reference()
        self.ref = ", ".join(refs)

        # Compute payment_reference.
        if len(refs) == 1:
            self.payment_reference = refs[0]

        self.autocomplete_purchase_picking_id = False
        self.purchase_id = False
        self._onchange_currency()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    stock_move_invoiced_id = fields.Many2one(
        "stock.move", string="Stock Move", copy=False, readonly=True
    )
    picking_invoiced_id = fields.Many2one(
        "stock.picking", string="Picking", copy=False, readonly=True
    )
