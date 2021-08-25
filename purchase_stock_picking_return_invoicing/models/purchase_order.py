# Copyright 2017 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import collections
from itertools import groupby

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    invoice_refund_count = fields.Integer(
        compute="_compute_invoice_refund_count", string="# of Invoice Refunds"
    )

    def _check_invoice_status_to_invoice(self):
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        return any(
            float_compare(
                line.qty_invoiced,
                line.product_qty
                if line.product_id.purchase_method == "purchase"
                else line.qty_received,
                precision_digits=precision,
            )
            for line in self.order_line
        )

    def _get_invoiced(self):
        """Modify invoice_status for taking into account returned/refunded
        qty, as the comparison qty_received vs qty_invoiced can be negative.
        It's only needed to modify the method for resetting state to
        "to invoice", as the rest of the states are already handled by super.
        """
        super(PurchaseOrder, self)._get_invoiced()
        for order in self.filtered(lambda x: x.state in ("purchase", "done")):
            if order._check_invoice_status_to_invoice():
                order.invoice_status = "to invoice"

    @api.depends("order_line.invoice_lines.move_id.state")
    def _compute_invoice_refund_count(self):
        for order in self:
            invoices = order.mapped("order_line.invoice_lines.move_id").filtered(
                lambda x: x.move_type == "in_refund"
            )
            order.invoice_refund_count = len(invoices)

    @api.depends("invoice_refund_count")
    def _compute_invoice(self):
        """Change computation for excluding refund invoices.

        Make this compatible with other extensions, only subtracting refunds
        from the number obtained in super.
        """
        super()._compute_invoice()
        for order in self:
            order.invoice_count -= order.invoice_refund_count

    def action_create_invoice_refund(self):
        """Create the refund associated to the PO."""
        precision = self.env["decimal.precision"].precision_get(
            "Product Unit of Measure"
        )
        # 1) Prepare refund vals and clean-up the section lines
        invoice_vals_list = []
        for order in self:
            if order.invoice_status != "to invoice":
                continue
            order = order.with_company(order.company_id)
            pending_section = None
            # Invoice values.
            invoice_vals = order._prepare_invoice()
            # Invoice line values (keep only necessary sections).
            for line in order.order_line:
                if line.display_type == "line_section":
                    pending_section = line
                    continue
                if not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    if pending_section:
                        invoice_vals["invoice_line_ids"].append(
                            (0, 0, pending_section._prepare_account_move_line())
                        )
                        pending_section = None
                    invoice_vals["invoice_line_ids"].append(
                        (0, 0, line._prepare_account_move_line())
                    )
            invoice_vals_list.append(invoice_vals)
        if not invoice_vals_list:
            raise UserError(
                _(
                    "There is no invoiceable line. "
                    "If a product has a control policy based on received quantity, "
                    "please make sure that a quantity has been received."
                )
            )
        # 2) group by (company_id, partner_id, currency_id) for batch creation
        new_invoice_vals_list = []
        for _grouping_keys, invoices in groupby(
            invoice_vals_list,
            key=lambda x: (
                x.get("company_id"),
                x.get("partner_id"),
                x.get("currency_id"),
            ),
        ):
            origins = set()
            payment_refs = set()
            refs = set()
            ref_invoice_vals = None
            for invoice_vals in invoices:
                if not ref_invoice_vals:
                    ref_invoice_vals = invoice_vals
                else:
                    ref_invoice_vals["invoice_line_ids"] += invoice_vals[
                        "invoice_line_ids"
                    ]
                origins.add(invoice_vals["invoice_origin"])
                payment_refs.add(invoice_vals["payment_reference"])
                refs.add(invoice_vals["ref"])
            ref_invoice_vals.update(
                {
                    "ref": ", ".join(refs)[:2000],
                    "invoice_origin": ", ".join(origins),
                    "payment_reference": len(payment_refs) == 1
                    and payment_refs.pop()
                    or False,
                }
            )
            new_invoice_vals_list.append(ref_invoice_vals)
        invoice_vals_list = new_invoice_vals_list
        # 3) Create refunds.
        moves = self.env["account.move"]
        AccountMove = self.env["account.move"].with_context(
            default_move_type="in_refund"
        )
        for vals in invoice_vals_list:
            moves |= AccountMove.with_company(vals["company_id"]).create(vals)
        return self.action_view_invoice_refund(moves)

    def action_view_invoice_refund(self, invoices=False):
        """This function returns an action that display existing vendor refund
        bills of given purchase order ids.
        When only one found, show the vendor bill immediately.
        """
        if not invoices:
            # Invoice_ids may be filtered depending on the user. To ensure we get all
            # invoices related to the purchase order, we read them in sudo to fill the
            # cache.
            self.sudo()._read(["invoice_ids"])
            invoices = self.invoice_ids
        refunds = invoices.filtered(lambda x: x.move_type == "in_refund")
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "account.action_move_in_refund_type"
        )
        # choose the view_mode accordingly
        if len(refunds) > 1:
            result["domain"] = [("id", "in", refunds.ids)]
        elif len(refunds) == 1:
            res = self.env.ref("account.view_move_form", False)
            form_view = [(res and res.id or False, "form")]
            if "views" in result:
                result["views"] = form_view + [
                    (state, view) for state, view in result["views"] if view != "form"
                ]
            else:
                result["views"] = form_view
            result["res_id"] = refunds.id
        else:
            result = {"type": "ir.actions.act_window_close"}
        return result

    def action_view_invoice(self, invoices=False):
        """Change super action for displaying only normal invoices."""
        if not invoices:
            # Invoice_ids may be filtered depending on the user. To ensure we get all
            # invoices related to the purchase order, we read them in sudo to fill the
            # cache.
            self.sudo()._read(["invoice_ids"])
            invoices = self.invoice_ids
        invoices = invoices.filtered(lambda x: x.move_type == "in_invoice")
        result = super(PurchaseOrder, self).action_view_invoice(invoices)
        return result


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    qty_refunded = fields.Float(compute="_compute_qty_refunded", string="Refunded Qty")
    qty_returned = fields.Float(
        compute="_compute_qty_returned",
        string="Returned* Qty",
        help="This is ONLY the returned quantity that is refundable.",
        store=True,
    )

    @api.depends("invoice_lines.move_id.state", "invoice_lines.quantity")
    def _compute_qty_refunded(self):
        for line in self:
            inv_lines = line.invoice_lines.filtered(
                lambda x: (
                    (x.move_id.move_type == "in_invoice" and x.quantity < 0.0)
                    or (x.move_id.move_type == "in_refund" and x.quantity > 0.0)
                )
            )
            line.qty_refunded = sum(
                inv_lines.mapped(
                    lambda x: (
                        x.product_uom_id._compute_quantity(x.quantity, line.product_uom)
                    )
                )
            )

    @api.depends("move_ids.state", "move_ids.returned_move_ids.state")
    def _compute_qty_returned(self):
        """Made through read_group for not impacting in performance."""
        ProductUom = self.env["uom.uom"]
        groups = self.env["stock.move"].read_group(
            [
                ("purchase_line_id", "in", self.ids),
                ("state", "=", "done"),
                ("to_refund", "=", True),
                ("location_id.usage", "!=", "supplier"),
            ],
            ["purchase_line_id", "product_uom_qty", "product_uom"],
            ["purchase_line_id", "product_uom"],
            lazy=False,
        )
        # load all UoM records at once on first access
        uom_ids = {g["product_uom"][0] for g in groups}
        ProductUom.browse(list(uom_ids))  # Prefetching
        line_qtys = collections.defaultdict(lambda: 0)
        for g in groups:
            uom = ProductUom.browse(g["product_uom"][0])
            line = self.browse(g["purchase_line_id"][0])
            if uom == line.product_uom:
                qty = g["product_uom_qty"]
            else:
                qty = uom._compute_quantity(g["product_uom_qty"], line.product_uom)
            line_qtys[line.id] += qty
        for line in self:
            line.qty_returned = line_qtys.get(line.id, 0)

    def _prepare_account_move_line(self, move=None):
        data = super()._prepare_account_move_line(move)
        move_type = self.env.context.get("default_move_type", False)
        if (move and move.move_type == "in_refund") or (
            not move and move_type and move_type == "in_refund"
        ):
            data["quantity"] *= -1.0
        return data
