from odoo import api, fields, models
from odoo.tools.float_utils import float_is_zero


class AccountMove(models.Model):
    _inherit = "account.move"

    autocomplete_purchase_picking_id = fields.Many2one(
        "stock.picking", copy=False, string="Auto-Complete from Picking"
    )

    def _update_invoice_from_purchase_order(self, purchase):
        if not purchase:
            return
        invoice_vals = purchase.with_company(purchase.company_id)._prepare_invoice()
        invoice_vals["currency_id"] = (
            self.invoice_line_ids
            and self.currency_id
            or invoice_vals.get("currency_id")
        )
        del invoice_vals["ref"]

        self.update(invoice_vals)
        origins = set(self.invoice_line_ids.mapped("purchase_line_id.order_id.name"))
        self.invoice_origin = ",".join(list(origins))

        refs = self._get_invoice_reference()
        self.ref = ", ".join(refs)
        if len(refs) == 1:
            self.payment_reference = refs[0]

    def _add_invoice_line_from_stock_move(self, stock_move):
        sequence = (
            max(self.invoice_line_ids.mapped("sequence")) + 1
            if self.invoice_line_ids
            else 10
        )
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        if float_is_zero(
            stock_move.qty_received_to_invoice, precision_digits=precision
        ):
            return
        line_vals = stock_move._prepare_account_move_line_from_stock(self, sequence)
        new_line = self.env["account.move.line"].new(line_vals)
        self.invoice_line_ids += new_line
        new_line._compute_account_id()
        new_line.picking_invoiced_id = self.autocomplete_purchase_picking_id

    @api.onchange("autocomplete_purchase_picking_id")
    def _onchange_autocomplete_purchase_picking_id(self):
        """Populate invoice lines from the selected purchase picking."""
        if (
            not self.autocomplete_purchase_picking_id
            or not self.autocomplete_purchase_picking_id.purchase_id
        ):
            return
        purchase = self.autocomplete_purchase_picking_id.purchase_id
        stock_moves = (
            self.autocomplete_purchase_picking_id.move_ids
            - self.invoice_line_ids.stock_move_invoiced_id
        )
        for stock_move in stock_moves:
            self._add_invoice_line_from_stock_move(stock_move)
        self._update_invoice_from_purchase_order(purchase)
        self.autocomplete_purchase_picking_id = False
        self.purchase_id = False
