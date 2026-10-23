# Copyright 2026 OSS Factory
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
#
# Functional backport of Odoo 19.0 CE ``purchase.bill.line.match``:
# https://github.com/odoo/odoo/blob/19.0/addons/purchase/models/purchase_bill_line_match.py
#
# Differences vs 19.0 (see readme/CREDITS.rst):
#  * the ``odoo.tools.SQL`` helper and ``_table_query`` do not exist in 16.0;
#    the SQL ``UNION`` view is created the 16.0 way, in ``init()``.
#  * the ``is_downpayment`` branch of the PO-line selection is dropped
#    (no such field on ``purchase.order.line`` in 16.0 CE).
#  * ``action_add_to_po`` (relies on the 19.0-only ``bill.to.po.wizard``) is
#    not backported.
from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError


class PurchaseBillLineMatch(models.Model):
    _name = "purchase.bill.line.match"
    _description = "Purchase Line and Vendor Bill line matching view"
    _auto = False
    _order = "product_id, aml_id, pol_id"

    pol_id = fields.Many2one(comodel_name="purchase.order.line", readonly=True)
    aml_id = fields.Many2one(comodel_name="account.move.line", readonly=True)
    company_id = fields.Many2one(comodel_name="res.company", readonly=True)
    partner_id = fields.Many2one(comodel_name="res.partner", readonly=True)
    product_id = fields.Many2one(comodel_name="product.product", readonly=True)
    line_qty = fields.Float(readonly=True)
    line_uom_id = fields.Many2one(comodel_name="uom.uom", readonly=True)
    qty_invoiced = fields.Float(readonly=True)
    qty_to_invoice = fields.Float("Qty to invoice", readonly=True)
    purchase_order_id = fields.Many2one(comodel_name="purchase.order", readonly=True)
    account_move_id = fields.Many2one(comodel_name="account.move", readonly=True)
    line_amount_untaxed = fields.Monetary(readonly=True)
    currency_id = fields.Many2one(comodel_name="res.currency", readonly=True)
    state = fields.Char(readonly=True)

    product_uom_id = fields.Many2one(
        comodel_name="uom.uom", related="product_id.uom_id"
    )
    product_uom_qty = fields.Float(
        compute="_compute_product_uom_qty",
        inverse="_inverse_product_uom_qty",
        readonly=False,
    )
    product_uom_price = fields.Float(
        compute="_compute_product_uom_price",
        inverse="_inverse_product_uom_price",
        readonly=False,
    )
    billed_amount_untaxed = fields.Monetary(
        compute="_compute_amount_untaxed_fields", currency_field="currency_id"
    )
    purchase_amount_untaxed = fields.Monetary(
        compute="_compute_amount_untaxed_fields", currency_field="currency_id"
    )
    reference = fields.Char(compute="_compute_reference")

    @api.onchange("product_uom_price")
    def _inverse_product_uom_price(self):
        for line in self:
            if line.aml_id:
                line.aml_id.price_unit = line.product_uom_price
            else:
                line.pol_id.price_unit = line.product_uom_price

    @api.onchange("product_uom_qty")
    def _inverse_product_uom_qty(self):
        for line in self:
            if line.aml_id:
                line.aml_id.quantity = line.product_uom_qty
            else:
                # On the PO line, setting product_qty recomputes price_unit back
                # to the old value; save and restore it so the price is kept.
                previous_price_unit = line.pol_id.price_unit
                line.pol_id.product_qty = line.product_uom_qty
                line.pol_id.price_unit = previous_price_unit

    def _compute_amount_untaxed_fields(self):
        for line in self:
            line.billed_amount_untaxed = (
                line.line_amount_untaxed if line.account_move_id else False
            )
            line.purchase_amount_untaxed = (
                line.line_amount_untaxed if line.purchase_order_id else False
            )

    def _compute_reference(self):
        for line in self:
            line.reference = (
                line.purchase_order_id.display_name or line.account_move_id.display_name
            )

    def name_get(self):
        # 16.0 computes display_name through name_get (the 19.0 model overrides
        # ``_compute_display_name`` instead). Same resulting label.
        result = []
        for line in self:
            name = (
                line.product_id.display_name
                or line.aml_id.name
                or line.pol_id.name
                or ""
            )
            result.append((line.id, name))
        return result

    def _compute_product_uom_qty(self):
        for line in self:
            if line.product_id:
                line.product_uom_qty = line.line_uom_id._compute_quantity(
                    line.line_qty, line.product_uom_id
                )
            else:
                line.product_uom_qty = line.line_qty

    @api.depends("aml_id.price_unit", "pol_id.price_unit")
    def _compute_product_uom_price(self):
        for line in self:
            line.product_uom_price = (
                line.aml_id.price_unit if line.aml_id else line.pol_id.price_unit
            )

    def _select_po_line(self):
        # Backport note: 19.0 also unions the ``is_downpayment`` purchase order
        # lines. That field does not exist on ``purchase.order.line`` in 16.0
        # CE, so the corresponding ``OR`` branch is dropped.
        return """
            SELECT pol.id AS id,
                   pol.id AS pol_id,
                   NULL AS aml_id,
                   pol.company_id AS company_id,
                   pol.partner_id AS partner_id,
                   pol.product_id AS product_id,
                   pol.product_qty AS line_qty,
                   pol.product_uom AS line_uom_id,
                   pol.qty_invoiced AS qty_invoiced,
                   pol.qty_to_invoice AS qty_to_invoice,
                   po.id AS purchase_order_id,
                   NULL AS account_move_id,
                   pol.price_subtotal AS line_amount_untaxed,
                   po.currency_id AS currency_id,
                   po.state AS state
              FROM purchase_order_line pol
         LEFT JOIN purchase_order po ON pol.order_id = po.id
             WHERE po.state = 'purchase'
               AND (pol.product_qty > pol.qty_invoiced OR pol.qty_to_invoice != 0)
        """

    def _select_am_line(self):
        return """
            SELECT -aml.id AS id,
                   NULL AS pol_id,
                   aml.id AS aml_id,
                   aml.company_id AS company_id,
                   am.partner_id AS partner_id,
                   aml.product_id AS product_id,
                   aml.quantity AS line_qty,
                   aml.product_uom_id AS line_uom_id,
                   NULL AS qty_invoiced,
                   NULL AS qty_to_invoice,
                   NULL AS purchase_order_id,
                   am.id AS account_move_id,
                   aml.amount_currency AS line_amount_untaxed,
                   aml.currency_id AS currency_id,
                   aml.parent_state AS state
              FROM account_move_line aml
         LEFT JOIN account_move am ON aml.move_id = am.id
             WHERE aml.display_type = 'product'
               AND am.move_type IN ('in_invoice', 'in_refund')
               AND aml.parent_state IN ('draft', 'posted')
               AND aml.purchase_line_id IS NULL
        """

    def init(self):
        # 16.0 has no ``odoo.tools.SQL`` / ``_table_query``; build the SQL view
        # the way 16.0 ``_auto = False`` models do. The query only interpolates
        # the model table name and our own static sub-selects (no user input).
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = "CREATE OR REPLACE VIEW %s AS (%s UNION ALL %s)" % (
            self._table,
            self._select_po_line(),
            self._select_am_line(),
        )
        self.env.cr.execute(query)

    def action_open_line(self):
        """Open the related purchase order or vendor bill (replaces the 19.0
        ``open_match_line_widget`` OWL widget)."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move" if self.account_move_id else "purchase.order",
            "view_mode": "form",
            "res_id": self.account_move_id.id
            if self.account_move_id
            else self.purchase_order_id.id,
        }

    def action_add_to_po(self):
        """Open the "Add to PO" wizard for the selected vendor bill lines.

        Backport of Odoo 19.0 ``purchase.bill.line.match.action_add_to_po``. The
        selected match record ids are passed as ``active_ids``: the SQL view
        encodes account move lines with a negative id (``id = -aml.id``), and the
        wizard recovers them with that same convention.

        The 19.0-only down-payment branch (``action_add_downpayment``) is not
        backported (``is_downpayment`` absent on ``purchase.order.line`` in 16.0
        CE), so the wizard exposes only the product "Add to PO" path.
        """
        if not self or not self.aml_id:
            raise UserError(_("Select Vendor Bill lines to add to a Purchase Order."))
        partner = self.mapped("partner_id.commercial_partner_id")
        if len(partner) > 1:
            raise UserError(_("Please select bill lines with the same vendor."))
        context = dict(self.env.context)
        context.update(
            {
                "active_model": self._name,
                "active_ids": self.ids,
                "default_partner_id": partner.id,
                "dialog_size": "medium",
            },
        )
        if len(self.purchase_order_id) > 1:
            raise UserError(
                _("Vendor Bill lines can only be added to one Purchase Order.")
            )
        if self.purchase_order_id:
            context["default_purchase_order_id"] = self.purchase_order_id.id
        return {
            "type": "ir.actions.act_window",
            "name": _("Add to Purchase Order"),
            "res_model": "bill.to.po.wizard",
            "target": "new",
            "view_mode": "form",
            "views": [
                (
                    self.env.ref(
                        "account_invoice_purchase_match.bill_to_po_wizard_form"
                    ).id,
                    "form",
                )
            ],
            "context": context,
        }

    @api.model
    def _action_create_bill_from_po_lines(self, partner, po_lines):
        """Create a new vendor bill with the selected PO lines and return an
        action to open it."""
        if len(po_lines.currency_id) == 1:
            currency = po_lines.currency_id
        elif len(po_lines.company_id) == 1:
            currency = po_lines.company_id.currency_id
        else:
            currency = self.env.company.currency_id
        bill = self.env["account.move"].create(
            {
                "move_type": "in_invoice",
                "partner_id": partner.id,
                "currency_id": currency.id,
            },
        )
        bill._add_purchase_order_lines(po_lines)
        # 16.0 has no ``_get_records_action`` helper; build the act_window dict.
        return {
            "type": "ir.actions.act_window",
            "name": _("Vendor Bill"),
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": bill.id,
        }

    @staticmethod
    def _group_by_product(lines):
        """Group a recordset by ``product_id`` preserving order.

        16.0 backport of ``recordset.grouped("product_id")`` (added in 17.0):
        returns ``{product_record: recordset}``.
        """
        groups = {}
        for line in lines:
            product = line.product_id
            groups[product] = groups.get(product, line.browse()) + line
        return groups

    def action_match_lines(self):
        if not self.pol_id:  # we need POL(s) to either match or create a bill
            raise UserError(
                _(
                    "You must select at least one Purchase Order line to match or create bill."
                )
            )
        if (
            not self.aml_id
        ):  # select POL(s) without AML -> create a draft bill with the POL(s)
            return self._action_create_bill_from_po_lines(self.partner_id, self.pol_id)

        # 16.0 has no ``recordset.grouped()`` (added in 17.0); group manually.
        pol_by_product = self._group_by_product(self.pol_id)
        aml_by_product = self._group_by_product(self.aml_id)
        residual_purchase_order_lines = self.pol_id
        residual_account_move_lines = self.aml_id

        # Match all matchable POL-AML lines and remove them from the residual group
        for product, po_lines in pol_by_product.items():
            po_line = po_lines[
                0
            ]  # in case of multiple POL with same product, only match the first one
            matching_bill_lines = aml_by_product.get(product)
            if matching_bill_lines:
                matching_bill_lines.purchase_line_id = po_line.id
                residual_purchase_order_lines -= po_line
                residual_account_move_lines -= matching_bill_lines

        if len(residual_bill := self.aml_id.move_id) == 1:
            # Delete all unmatched selected AML
            if residual_account_move_lines:
                residual_account_move_lines.unlink()

            # Add all remaining POL to the residual bill
            residual_bill._add_purchase_order_lines(residual_purchase_order_lines)
        return None
