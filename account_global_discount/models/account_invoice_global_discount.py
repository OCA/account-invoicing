# Copyright 2019 Tecnativa - David Vidal
# Copyright 2020-2021 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


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
        domain=(
            "[('account_type', 'not in', ['asset_receivable', 'liability_payable'])]"
        ),
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
