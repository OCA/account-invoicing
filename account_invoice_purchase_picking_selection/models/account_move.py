from odoo import api, fields, models
from odoo.tools.float_utils import float_is_zero


class AccountMove(models.Model):
    _inherit = "account.move"

    autocomplete_purchase_picking_id = fields.Many2one(
        "stock.picking", copy=False, string="Auto-Complete from Picking"
    )

    def _get_invoice_reference(self):
        self.ensure_one()
        vendor_refs = [
            ref
            for ref in set(
                self.invoice_line_ids.mapped("purchase_line_id.order_id.partner_ref")
            )
            if ref
        ]
        if self.ref:
            return [
                ref for ref in self.ref.split(", ") if ref and ref not in vendor_refs
            ] + vendor_refs
        return vendor_refs

    def _update_invoice_from_purchase_order(self, purchase):
        if not purchase:
            return
        invoice_vals = purchase.with_company(purchase.company_id)._prepare_invoice()
        has_invoice_lines = bool(
            self.invoice_line_ids.filtered(
                lambda line: line.display_type
                not in ("line_section", "line_subsection", "line_note")
            )
        )
        currency_id = (
            self.currency_id if has_invoice_lines else invoice_vals.get("currency_id")
        )
        invoice_vals.pop("ref", None)
        invoice_vals.pop("payment_reference", None)
        invoice_vals.pop("company_id", None)
        if self.move_type == invoice_vals["move_type"]:
            invoice_vals.pop("move_type")

        self.update(invoice_vals)
        self.currency_id = currency_id
        origins = set(self.invoice_line_ids.mapped("purchase_line_id.order_id.name"))
        self.invoice_origin = ",".join(list(origins))

        refs = self._get_invoice_reference()
        self.ref = ", ".join(refs)
        if len(refs) == 1:
            self.payment_reference = refs[0]
        if self.company_id != purchase.company_id:
            self.company_id = purchase.company_id

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
