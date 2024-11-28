# Copyright (C) 2024-Today - KMEE (<http://www.kmee.com.br>).
# Author: Diego Paradeda <diego.paradeda@kmee.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError

INVOICE_TYPE_MAP = {
    # Account Move Type | Picking Type Code | Local Origin Usage | Local Dest Usage
    "in_invoice": ("incoming", "supplier", "internal"),
    "in_refund": ("outgoing", "internal", "supplier"),
    "out_invoice": ("outgoing", "internal", "customer"),
    "out_refund": ("incoming", "customer", "internal"),
}


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def action_generate_pickings_from_invoices(self):
        """Generate pickings from invoice lines."""
        # Filter out cancelled invoices
        non_cancelled_invoices = self.filtered(lambda inv: inv.state != "cancel")
        if not non_cancelled_invoices:
            raise UserError(_("Cannot create stock transfer for cancelled invoices."))

        # Identify invoice lines eligible for transfer
        eligible_inv_lines = non_cancelled_invoices.mapped("invoice_line_ids")
        inv_lines_without_transfer = eligible_inv_lines.filtered(
            lambda inv_line: not inv_line.move_line_ids
        )

        # Raise error if all invoice lines already have transfers
        if not inv_lines_without_transfer:
            raise UserError(_("No invoice lines are eligible for stock transfer."))

        # Generate transfers for eligible invoice lines
        for record in self:
            transferable_inv_lines = record._get_transferable_invoice_lines()
            if transferable_inv_lines:
                record.generate_picking_from_invoice()

    def _get_transferable_invoice_lines(self):
        """Retrieve invoice lines without a picking associated."""
        return self.invoice_line_ids.filtered(
            lambda inv_line: not inv_line.move_line_ids.picking_id
        )

    def generate_picking_from_invoice(self):
        """Generate a picking from the invoice."""
        self.ensure_one()
        if self.move_type not in INVOICE_TYPE_MAP:
            raise UserError(f"Unsupported move type: {self.move_type}")

        picking_type_code, location_src_usage, location_dest_usage = INVOICE_TYPE_MAP[
            self.move_type
        ]

        # Picking type
        picking_type_id = self.env["stock.picking.type"].search(
            [("code", "=", picking_type_code)],
            limit=1,
        )

        # Locations
        location_src_id = self.env["stock.location"].search(
            [("usage", "=", location_src_usage)],
            limit=1,
        )
        location_dest_id = self.env["stock.location"].search(
            [("usage", "=", location_dest_usage)],
            limit=1,
        )

        # Picking
        picking_values = {
            "partner_id": self.partner_id.id,
            "picking_type_id": picking_type_id.id,
            "location_id": location_src_id.id,
            "location_dest_id": location_dest_id.id,
            "invoice_ids": self.ids,
            "origin": self.name,
        }

        # Moves
        transferable_move_line_ids = self._get_transferable_invoice_lines()
        move_values = [
            self._prepare_stock_move_values(line, picking_values)
            for line in transferable_move_line_ids
        ]
        picking_values["move_lines"] = [(0, 0, move) for move in move_values]

        self._create_picking(picking_values=picking_values)

    def _prepare_stock_move_values(self, invoice_line, picking_values):
        """Prepare stock move values from invoice line."""
        self.ensure_one()
        return {
            "name": invoice_line.product_id.name,
            "product_id": invoice_line.product_id.id,
            "location_id": picking_values.get("location_id"),
            "location_dest_id": picking_values.get("location_dest_id"),
            "state": "draft",
            "company_id": self.company_id.id,
            "product_uom_qty": invoice_line.quantity,
            "product_uom": invoice_line.product_uom_id.id,
            "invoice_line_ids": invoice_line.ids,
        }

    def _create_picking(self, picking_values):
        """Create a picking with the given values.

        Override this method if you need to change any values of the
        picking and the lines before the picking creation.

        :param picking_values: dict with the picking and its lines
        :return: picking
        """
        return self.env["stock.picking"].create(picking_values)

    # def action_match_pickings_from_invoices(self):
    #     action = self.env.ref("account_move_stock_create.action_account_move_match_picking")
    #     result = action.sudo().read()[0]
    #     result.update({"res_id": self.id})
    #     return result
