# Copyright 2026 OSS Factory
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
#
# Functional backport of the Odoo 19.0 CE ``bill.to.po.wizard`` "Add to PO"
# flow (only ``action_add_to_po``):
# https://github.com/odoo/odoo/blob/19.0/addons/purchase/wizard/bill_to_po_wizard.py
#
# Differences vs 19.0 (see readme/CREDITS.rst):
#  * ``action_add_downpayment`` is NOT backported: it relies on
#    ``purchase.order.line.is_downpayment`` and ``purchase.order._create_downpayments``
#    which do not exist in 16.0 CE (same wall as the down-payment branch already
#    dropped from the matching view).
#  * 19.0 ``account.move.line._prepare_line_values_for_purchase`` does not exist
#    in 16.0 CE, so the per-line purchase values are built inline here.
#  * ``purchase.order.line`` has no ``discount`` field in 16.0 CE (17.0+): the
#    bill line discount is folded into the net unit price instead of being copied.
from odoo import Command, _, fields, models
from odoo.exceptions import UserError


class BillToPoWizard(models.TransientModel):
    _name = "bill.to.po.wizard"
    _description = "Bill to Purchase Order"

    purchase_order_id = fields.Many2one(comodel_name="purchase.order")
    partner_id = fields.Many2one(comodel_name="res.partner")

    def _prepare_line_values_for_purchase(self, lines):
        """Build ``purchase.order.line`` values from vendor bill lines.

        Inlined backport of the 19.0 ``account.move.line._prepare_line_values_for_purchase``
        (absent in 16.0 CE). Currency is converted to the target purchase order
        currency when they differ, mirroring the 19.0 down-payment helper for
        regular product lines.
        """
        self.ensure_one()
        po_currency = self.purchase_order_id.currency_id or self.env.company.currency_id
        company = self.purchase_order_id.company_id or self.env.company
        date = self.purchase_order_id.date_order or fields.Date.today()
        # purchase.order.line has NO `discount` field in 16.0 CE (added in 17.0+).
        # If the field exists (future base), pass it through; otherwise fold the
        # bill line discount into the net unit price so the line amount stays faithful.
        has_po_discount = "discount" in self.env["purchase.order.line"]._fields
        line_vals = []
        for line in lines:
            price_unit = line.price_unit
            if line.currency_id and line.currency_id != po_currency:
                price_unit = line.currency_id._convert(
                    price_unit, po_currency, company, date
                )
            vals = {
                "product_id": line.product_id.id,
                "product_qty": line.quantity,
                "product_uom": line.product_uom_id.id,
                "price_unit": price_unit,
                "taxes_id": [Command.set(line.tax_ids.ids)],
            }
            if has_po_discount:
                vals["discount"] = line.discount
            elif line.discount:
                vals["price_unit"] = price_unit * (1.0 - (line.discount or 0.0) / 100.0)
            line_vals.append(vals)
        return line_vals

    def action_add_to_po(self):
        """Add the selected vendor bill lines to a purchase order.

        The matching screen passes the selected ``purchase.bill.line.match`` ids
        as ``active_ids``; faithfully to 19.0, account move lines carry a
        negative id in that view (``id = -aml.id``), so we keep the negative-id
        convention to recover them.
        """
        active_ids = self.env.context.get("active_ids") or []
        aml_ids = [abs(record_id) for record_id in active_ids if record_id < 0]
        lines_to_add = (
            self.env["account.move.line"]
            .browse(aml_ids)
            .filtered(lambda line: line.product_id)
        )
        if not lines_to_add:
            raise UserError(
                _(
                    "There are no products to add to the Purchase Order. "
                    "Are these Down Payments?"
                )
            )
        # Materialise the target PO first (unlike 19.0, which builds the new PO
        # with its lines in a single ``create``): on 16.0 we need the PO's
        # currency/date_order to be readable when converting the line prices.
        if not self.purchase_order_id:
            self.purchase_order_id = self.env["purchase.order"].create(
                {
                    "partner_id": lines_to_add.partner_id.id,
                },
            )
        line_vals = self._prepare_line_values_for_purchase(lines_to_add)
        new_po_lines = self.env["purchase.order.line"].create(
            [
                {
                    **val,
                    "order_id": self.purchase_order_id.id,
                }
                for val in line_vals
            ],
        )
        # The lines created above already belong to the order through ``order_id``,
        # so the order's ``order_line`` must NOT be assigned again: re-writing that
        # one2many re-triggers ``_compute_price_unit_and_date_planned_and_name`` on
        # the new lines, and since ``price_unit`` is a stored computed field
        # (``readonly=False``) on 16.0 CE, the bill price is then replaced by the
        # vendor price read from ``product.supplierinfo`` -- a record
        # ``button_confirm`` creates for every ordered product. Reproducible with
        # ``purchase_stock`` installed.
        self.purchase_order_id.button_confirm()
        for aml, pol in zip(lines_to_add, new_po_lines):
            if aml.product_id == pol.product_id:
                aml.purchase_line_id = pol.id
        return {
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "view_mode": "form",
            "res_id": self.purchase_order_id.id,
        }
