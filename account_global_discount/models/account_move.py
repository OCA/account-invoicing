# Copyright 2019 Tecnativa - David Vidal
# Copyright 2020-2021 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, exceptions, fields, models
from odoo.tools import config


class AccountMove(models.Model):
    _inherit = "account.move"

    # HACK: Looks like UI doesn't behave well with Many2many fields and
    # negative groups when the same field is shown. In this case, we want to
    # show the readonly version to any not in the global discount group.
    # TODO: Check if it's fixed in future versions
    global_discount_ids_readonly = fields.Many2many(
        string="Invoice Global Discounts (readonly)",
        related="global_discount_ids",
        readonly=True,
    )
    global_discount_ids = fields.Many2many(
        comodel_name="global.discount",
        column1="invoice_id",
        column2="global_discount_id",
        string="Invoice Global Discounts",
        domain="[('discount_scope', 'in', {"
        "    'out_invoice': ['sale'], "
        "    'out_refund': ['sale'], "
        "    'in_refund': ['purchase'], "
        "    'in_invoice': ['purchase']"
        "}.get(move_type, [])), ('account_id', '!=', False), '|', "
        "('company_id', '=', company_id), ('company_id', '=', False)]",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    amount_global_discount = fields.Monetary(
        string="Total Global Discounts",
        compute="_compute_amount",
        currency_field="currency_id",
        readonly=True,
        compute_sudo=True,
        store=True,
    )
    amount_untaxed_before_global_discounts = fields.Monetary(
        string="Amount Untaxed Before Discounts",
        compute="_compute_amount",
        currency_field="currency_id",
        readonly=True,
        compute_sudo=True,
        store=True,
    )
    invoice_global_discount_ids = fields.One2many(
        comodel_name="account.invoice.global.discount",
        inverse_name="invoice_id",
        readonly=True,
    )

    def _prepare_global_discount_vals(self, global_discount, base, tax_ids):
        """Prepare the dictionary values for an invoice global discount
        line.
        """
        self.ensure_one()
        discount = global_discount._get_global_discount_vals(base)
        return {
            "name": global_discount.display_name,
            "invoice_id": self.id,
            "global_discount_id": global_discount.id,
            "discount": global_discount.discount,
            "base": base,
            "base_discounted": discount["base_discounted"],
            "account_id": global_discount.account_id.id,
            "tax_ids": [(4, tax_id) for tax_id in tax_ids],
        }

    def _set_global_discounts_by_tax(self):
        """Create invoice global discount lines by taxes combinations and
        discounts.

        This also resets previous global discounts in case they existed.
        """
        self.ensure_one()
        if not self.is_invoice():
            return
        in_draft_mode = self != self._origin
        taxes_keys = {}
        # Perform a sanity check for discarding cases that will lead to
        # incorrect data in discounts
        _self = self.filtered("global_discount_ids")
        for inv_line in _self.invoice_line_ids.filtered(
            lambda l: l.display_type not in ["line_section", "line_note"]
        ):
            if inv_line.product_id.bypass_global_discount:
                continue
            taxes_keys.setdefault(tuple(inv_line.tax_ids.ids), 0)
            taxes_keys[tuple(inv_line.tax_ids.ids)] += inv_line.price_subtotal
        # Reset previous global discounts
        self.invoice_global_discount_ids -= self.invoice_global_discount_ids
        model = "account.invoice.global.discount"
        create_method = in_draft_mode and self.env[model].new or self.env[model].create
        for tax_line in _self.line_ids.filtered("tax_line_id"):
            key = []
            discount_line_base = 0
            for key in taxes_keys:
                if tax_line.tax_line_id.id in key:
                    discount_line_base = taxes_keys[key]
                    taxes_keys[key] = 0  # mark for not duplicating
                    break  # we leave in key variable the proper taxes value
            if not discount_line_base:
                continue
            for global_discount in self.global_discount_ids:
                vals = self._prepare_global_discount_vals(
                    global_discount, discount_line_base, key
                )
                create_method(vals)
                discount_line_base = vals["base_discounted"]
        _self._set_global_discounts_by_zero_tax(taxes_keys, create_method)

    def _set_global_discounts_by_zero_tax(self, taxes_keys, create_method):
        # Check all moves with defined taxes to check if there's any discount not
        # created (tax amount is zero and only one tax is applied)
        base_total = 0
        zero_taxes = self.env["account.tax"]
        for line in self.line_ids.filtered("tax_ids"):
            if line.product_id.bypass_global_discount:
                continue
            key = tuple(line.tax_ids.ids)
            if taxes_keys.get(key):
                base_total += line.price_subtotal
                zero_taxes |= line.tax_ids
        for global_discount in self.global_discount_ids:
            if not base_total:
                break
            vals = self._prepare_global_discount_vals(
                global_discount, base_total, zero_taxes.ids
            )
            create_method(vals)
            base_total = vals["base_discounted"]

    def _recompute_global_discount_lines(self):
        """Append global discounts move lines.

        This is called when recomputing dynamic lines before calling
        `_recompute_payment_terms_lines`, but after calling `_recompute_tax_lines`.
        """
        self.ensure_one()
        in_draft_mode = self != self._origin
        model = "account.move.line"
        create_method = in_draft_mode and self.env[model].new or self.env[model].create
        for discount in self.invoice_global_discount_ids.filtered("discount"):
            sign = -1 if self.move_type in {"in_invoice", "out_refund"} else 1
            disc_amount = sign * discount.discount_amount
            disc_amount_company_currency = disc_amount
            if self.currency_id != self.company_id.currency_id:
                disc_amount_company_currency = self.currency_id._convert(
                    disc_amount,
                    self.company_id.currency_id,
                    self.company_id,
                    self.date or fields.Date.context_today(self),
                )
            create_method(
                {
                    "invoice_global_discount_id": discount.id,
                    "move_id": self.id,
                    "name": "%s - %s"
                    % (discount.name, ", ".join(discount.tax_ids.mapped("name"))),
                    "debit": disc_amount_company_currency > 0.0
                    and disc_amount_company_currency
                    or 0.0,
                    "credit": disc_amount_company_currency < 0.0
                    and -disc_amount_company_currency
                    or 0.0,
                    "amount_currency": (disc_amount > 0.0 and disc_amount or 0.0)
                    - (disc_amount < 0.0 and -disc_amount or 0.0),
                    "account_id": discount.account_id.id,
                    "tax_ids": [(4, x.id) for x in discount.tax_ids],
                    "partner_id": self.commercial_partner_id.id,
                    "currency_id": self.currency_id.id,
                    "price_unit": -1 * abs(disc_amount_company_currency),
                }
            )

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        res = super()._onchange_partner_id()
        discounts = False
        if (
            self.move_type in ["out_invoice", "out_refund"]
            and self.partner_id.customer_global_discount_ids
        ):
            discounts = self.partner_id.customer_global_discount_ids.filtered(
                lambda d: d.company_id == self.company_id
            )
        elif (
            self.move_type in ["in_refund", "in_invoice"]
            and self.partner_id.supplier_global_discount_ids
        ):
            discounts = self.partner_id.supplier_global_discount_ids.filtered(
                lambda d: d.company_id == self.company_id
            )
        if discounts:
            self.global_discount_ids = discounts
        return res

    def _compute_amount_one(self):
        """Perform totals computation of a move with global discounts."""
        if not self.invoice_global_discount_ids:
            self.amount_global_discount = 0.0
            self.amount_untaxed_before_global_discounts = 0.0
            return
        round_curr = self.currency_id.round
        self.amount_global_discount = sum(
            round_curr(discount.discount_amount) * -1
            for discount in self.invoice_global_discount_ids
        )
        self.amount_untaxed_before_global_discounts = (
            self.amount_untaxed - self.amount_global_discount
        )

    @api.depends(
        "line_ids.matched_debit_ids.debit_move_id.move_id.payment_id.is_matched",
        "line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual",
        "line_ids.matched_debit_ids.debit_move_id.move_id.line_ids.amount_residual_currency",
        "line_ids.matched_credit_ids.credit_move_id.move_id.payment_id.is_matched",
        "line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual",
        "line_ids.matched_credit_ids.credit_move_id.move_id.line_ids.amount_residual_currency",
        "line_ids.balance",
        "line_ids.currency_id",
        "line_ids.amount_currency",
        "line_ids.amount_residual",
        "line_ids.amount_residual_currency",
        "line_ids.payment_id.state",
        "line_ids.full_reconcile_id",
        "invoice_global_discount_ids",
        "global_discount_ids",
    )
    def _compute_amount(self):
        """Modify totals computation for including global discounts."""
        res = super()._compute_amount()
        for record in self:
            record._compute_amount_one()
        return res

    def _clean_global_discount_lines(self):
        self.ensure_one()
        gbl_disc_lines = self.env["account.move.line"].search(
            [
                ("move_id", "=", self.id),
                "|",
                ("global_discount_item", "=", True),
                ("invoice_global_discount_id", "!=", False),
            ]
        )
        if gbl_disc_lines:
            move_container = {"records": self}
            with self._check_balanced(move_container), self._sync_dynamic_lines(
                move_container
            ):
                gbl_disc_lines.unlink()

    @api.model_create_multi
    def create(self, vals_list):
        """If we create the invoice with the discounts already set like from
        a sales order, we must compute the global discounts as well, as some data
        like ``tax_ids`` is not set until the final step.
        """
        moves = super().create(vals_list)
        for move in moves:
            if move.move_type in ["out_refund", "in_refund"]:
                move._clean_global_discount_lines()
            move._set_global_discounts_by_tax()
            move._recompute_global_discount_lines()
        return moves

    def write(self, vals):
        res = super().write(vals)
        if "invoice_line_ids" in vals or "global_discount_ids" in vals:
            for move in self:
                move._clean_global_discount_lines()
                move._set_global_discounts_by_tax()
                move._recompute_global_discount_lines()
            move_container = {"records": self}
            self._global_discount_check(move_container)
        return res

    def _global_discount_check(self, container):
        test_condition = not config["test_enable"] or self.env.context.get(
            "test_account_global_discount"
        )
        for move in container["records"]:
            if not move.is_invoice() or not move.global_discount_ids:
                continue
            taxes_keys = {}
            for inv_line in move.invoice_line_ids:
                if inv_line.display_type != "product":
                    continue
                if not inv_line.tax_ids and test_condition:
                    raise exceptions.UserError(
                        _("With global discounts, taxes in lines are required.")
                    )
                for key in taxes_keys:
                    if key == tuple(inv_line.tax_ids.ids):
                        break
                    elif set(key) & set(inv_line.tax_ids.ids) and test_condition:
                        raise exceptions.UserError(
                            _("Incompatible taxes found for global discounts.")
                        )
                else:
                    taxes_keys[tuple(inv_line.tax_ids.ids)] = True
        return True


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    invoice_global_discount_id = fields.Many2one(
        comodel_name="account.invoice.global.discount",
        string="Invoice Global Discount",
    )
    base_before_global_discounts = fields.Monetary(
        string="Amount Untaxed Before Discounts",
        readonly=True,
    )
    # TODO: To be removed on future versions if invoice_global_discount_id is properly filled
    # Provided for compatibility in stable branch
    # UPD: can be removed past version 16.0
    global_discount_item = fields.Boolean()


class AccountInvoiceGlobalDiscount(models.Model):
    _name = "account.invoice.global.discount"
    _description = "Invoice Global Discount"

    name = fields.Char(string="Discount Name", required=True)
    invoice_id = fields.Many2one(
        "account.move",
        string="Invoice",
        ondelete="cascade",
        index=True,
        readonly=True,
        domain=[
            (
                "move_type",
                "in",
                ["out_invoice", "out_refund", "in_invoice", "in_refund"],
            )
        ],
    )
    global_discount_id = fields.Many2one(
        comodel_name="global.discount",
        string="Global Discount",
    )
    discount = fields.Float(string="Discount (number)")
    discount_display = fields.Char(
        compute="_compute_discount_display",
        string="Discount",
    )
    base = fields.Float(string="Base before discount", digits="Product Price")
    base_discounted = fields.Float(string="Base after discount", digits="Product Price")
    currency_id = fields.Many2one(related="invoice_id.currency_id", readonly=True)
    discount_amount = fields.Monetary(
        string="Discounted Amount",
        compute="_compute_discount_amount",
        currency_field="currency_id",
        compute_sudo=True,
    )
    tax_ids = fields.Many2many(comodel_name="account.tax", string="Taxes")
    account_id = fields.Many2one(
        comodel_name="account.account",
        required=True,
        string="Account",
        domain="[('account_type', 'not in', ['asset_receivable', 'liability_payable'])]",
    )
    account_analytic_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic account",
    )
    company_id = fields.Many2one(related="invoice_id.company_id", readonly=True)

    def _compute_discount_display(self):
        """Given a discount type, we need to render a different symbol"""
        for one in self:
            precision = self.env["decimal.precision"].precision_get("Discount")
            one.discount_display = "{0:.{1}f}%".format(one.discount * -1, precision)

    @api.depends("base", "base_discounted")
    def _compute_discount_amount(self):
        """Compute the amount discounted"""
        for one in self:
            one.discount_amount = one.base - one.base_discounted
