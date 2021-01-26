# Copyright 2019 Tecnativa - David Vidal
# Copyright 2020 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, exceptions, fields, models
from odoo.tools import config


class AccountMove(models.Model):
    _inherit = "account.move"

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
        "}.get(type, [])), ('account_id', '!=', False), '|', "
        "('company_id', '=', company_id), ('company_id', '=', False)]",
    )
    amount_global_discount = fields.Monetary(
        string="Total Global Discounts",
        compute="_compute_amount",
        currency_field="currency_id",
        readonly=True,
        compute_sudo=True,
    )
    amount_untaxed_before_global_discounts = fields.Monetary(
        string="Amount Untaxed Before Discounts",
        compute="_compute_amount",
        currency_field="currency_id",
        readonly=True,
        compute_sudo=True,
    )
    invoice_global_discount_ids = fields.One2many(
        comodel_name="account.invoice.global.discount",
        inverse_name="invoice_id",
        readonly=True,
    )

    def _recompute_tax_lines(self, recompute_tax_base_amount=False):
        super()._recompute_tax_lines(recompute_tax_base_amount)
        # If recompute_tax_base_amount is True, only the tax_base_amount
        # field is recalculated, therefore the debit and debit fields
        # will not be recalculated and it doesn't make sense to apply
        # the global discount to the taxes move lines by calling the
        # _update_tax_lines_for_global_discount method.
        if not recompute_tax_base_amount:
            self._update_tax_lines_for_global_discount()

    def _update_tax_lines_for_global_discount(self):
        """ Update tax_base_amount and taxes debits."""
        round_curr = self.currency_id.round
        tax_lines = self.line_ids.filtered(
            lambda r: r.tax_line_id.amount_type in ("percent", "division")
        )
        for tax_line in tax_lines:
            base = tax_line.tax_base_amount
            tax_line.base_before_global_discounts = base
            amount = tax_line.balance
            for discount in self.global_discount_ids:
                base = discount._get_global_discount_vals(base)["base_discounted"]
                amount = discount._get_global_discount_vals(amount)["base_discounted"]
            tax_line.tax_base_amount = round_curr(base)
            tax_line.debit = amount > 0.0 and amount or 0.0
            tax_line.credit = amount < 0.0 and -amount or 0.0
            # Apply onchanges
            tax_line._onchange_amount_currency()
            tax_line._onchange_balance()

    def _prepare_global_discount_vals(self, global_discount, base, tax_ids):
        """Prepare the dictionary values for an invoice global discount
        line.
        """
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
        """
        self.ensure_one()
        taxes_keys = {}
        # Perform a sanity check for discarding cases that will lead to
        # incorrect data in discounts
        for inv_line in self.invoice_line_ids.filtered(lambda l: not l.display_type):
            if not inv_line.tax_ids and (
                not config["test_enable"]
                or self.env.context.get("test_account_global_discount")
            ):
                raise exceptions.UserError(
                    _("With global discounts, taxes in lines are required.")
                )
            for key in taxes_keys:
                if key == tuple(inv_line.tax_ids.ids):
                    break
                elif set(key) & set(inv_line.tax_ids.ids) and (
                    not config["test_enable"]
                    or self.env.context.get("test_account_global_discount")
                ):
                    raise exceptions.UserError(
                        _("Incompatible taxes found for global discounts.")
                    )
            else:
                taxes_keys[tuple(inv_line.tax_ids.ids)] = True
        self.invoice_global_discount_ids = False
        invoice_global_discounts = []
        for tax_line in self.line_ids.filtered("tax_line_id"):
            key = []
            to_create = True
            for key in taxes_keys:
                if tax_line.tax_line_id.id in key:
                    to_create = taxes_keys[key]
                    taxes_keys[key] = False  # mark for not duplicating
                    break  # we leave in key variable the proper taxes value
            if not to_create:
                continue
            base = tax_line.base_before_global_discounts or tax_line.tax_base_amount
            for global_discount in self.global_discount_ids:
                vals = self._prepare_global_discount_vals(global_discount, base, key)
                invoice_global_discounts.append((0, 0, vals))
                base = vals["base_discounted"]
        # Check all moves with defined taxes to check if there's any discount not
        # created (tax amount is zero and only one tax is applied)
        for line in self.line_ids.filtered("tax_ids"):
            key = tuple(line.tax_ids.ids)
            if taxes_keys.get(key):
                base = line.price_subtotal
                for global_discount in self.global_discount_ids:
                    vals = self._prepare_global_discount_vals(
                        global_discount, base, key
                    )
                    invoice_global_discounts.append((0, 0, vals))
                    base = vals["base_discounted"]
        self.invoice_global_discount_ids = invoice_global_discounts

    def _create_global_discount_journal_items(self):
        """Append global discounts move lines"""
        lines_to_delete = self.line_ids.filtered("global_discount_item")
        if self != self._origin:
            self.line_ids -= lines_to_delete
        else:
            lines_to_delete.with_context(check_move_validity=False).unlink()
        vals_list = []
        for discount in self.invoice_global_discount_ids.filtered("discount"):
            disc_amount = discount.discount_amount
            vals_list.append(
                (
                    0,
                    0,
                    {
                        "global_discount_item": True,
                        "name": "%s - %s"
                        % (discount.name, ", ".join(discount.tax_ids.mapped("name"))),
                        "debit": disc_amount > 0.0 and disc_amount or 0.0,
                        "credit": disc_amount < 0.0 and -disc_amount or 0.0,
                        "account_id": discount.account_id.id,
                        "analytic_account_id": discount.account_analytic_id.id,
                        "exclude_from_invoice_tab": True,
                    },
                )
            )
        self.line_ids = vals_list
        self._onchange_recompute_dynamic_lines()

    def _set_global_discounts(self):
        """Get global discounts in order and apply them in chain. They will be
        fetched in their sequence order"""
        for inv in self:
            inv._set_global_discounts_by_tax()
            inv._create_global_discount_journal_items()

    @api.onchange("invoice_line_ids")
    def _onchange_invoice_line_ids(self):
        others_lines = self.line_ids.filtered(
            lambda line: line.exclude_from_invoice_tab
        )
        if others_lines:
            others_lines[0].recompute_tax_line = True
        res = super()._onchange_invoice_line_ids()
        self._set_global_discounts()
        return res

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id(self):
        res = super()._onchange_partner_id()
        if (
            self.type in ["out_invoice", "out_refund"]
            and self.partner_id.customer_global_discount_ids
        ):
            self.global_discount_ids = self.partner_id.customer_global_discount_ids
        elif (
            self.type in ["in_refund", "in_invoice"]
            and self.partner_id.supplier_global_discount_ids
        ):
            self.global_discount_ids = self.partner_id.supplier_global_discount_ids
        return res

    @api.onchange("global_discount_ids")
    def _onchange_global_discount_ids(self):
        """Trigger global discount lines to recompute all"""
        return self._onchange_invoice_line_ids()

    def _compute_amount_one(self):
        if not self.invoice_global_discount_ids:
            self.amount_global_discount = 0.0
            self.amount_untaxed_before_global_discounts = 0.0
            return
        round_curr = self.currency_id.round
        self.amount_global_discount = sum(
            round_curr(discount.discount_amount) * -1
            for discount in self.invoice_global_discount_ids
        )
        self.amount_untaxed_before_global_discounts = self.amount_untaxed
        self.amount_untaxed = self.amount_untaxed + self.amount_global_discount
        self.amount_total = self.amount_untaxed + self.amount_tax
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if (
            self.currency_id
            and self.company_id
            and self.currency_id != self.company_id.currency_id
        ):
            date = self.invoice_date or fields.Date.today()
            amount_total_company_signed = self.currency_id._convert(
                self.amount_total, self.company_id.currency_id, self.company_id, date
            )
            amount_untaxed_signed = self.currency_id._convert(
                self.amount_untaxed, self.company_id.currency_id, self.company_id, date
            )
        sign = self.type in ["in_refund", "out_refund"] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    @api.depends(
        "line_ids.debit",
        "line_ids.credit",
        "line_ids.currency_id",
        "line_ids.amount_currency",
        "line_ids.amount_residual",
        "line_ids.amount_residual_currency",
        "line_ids.payment_id.state",
        "invoice_global_discount_ids",
        "global_discount_ids",
    )
    def _compute_amount(self):
        super()._compute_amount()
        for record in self:
            record._compute_amount_one()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    invoice_global_discount_id = fields.Many2one(
        comodel_name="account.invoice.global.discount",
        string="Invoice Global Discount",
    )
    base_before_global_discounts = fields.Monetary(
        string="Amount Untaxed Before Discounts", readonly=True,
    )
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
            ("type", "in", ["out_invoice", "out_refund", "in_invoice", "in_refund"])
        ],
    )
    global_discount_id = fields.Many2one(
        comodel_name="global.discount", string="Global Discount", readonly=True,
    )
    discount = fields.Float(string="Discount (number)", readonly=True)
    discount_display = fields.Char(
        compute="_compute_discount_display", readonly=True, string="Discount",
    )
    base = fields.Float(
        string="Base discounted", digits="Product Price", readonly=True,
    )
    base_discounted = fields.Float(
        string="Discounted amount", digits="Product Price", readonly=True,
    )
    currency_id = fields.Many2one(related="invoice_id.currency_id", readonly=True)
    discount_amount = fields.Monetary(
        string="Discounted Amount",
        compute="_compute_discount_amount",
        currency_field="currency_id",
        readonly=True,
        compute_sudo=True,
    )
    tax_ids = fields.Many2many(comodel_name="account.tax")
    account_id = fields.Many2one(
        comodel_name="account.account",
        required=True,
        string="Account",
        domain="[('user_type_id.type', 'not in', ['receivable', 'payable'])]",
    )
    account_analytic_id = fields.Many2one(
        comodel_name="account.analytic.account", string="Analytic account",
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
