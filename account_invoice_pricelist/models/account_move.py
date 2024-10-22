# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import config


class AccountMove(models.Model):
    _inherit = "account.move"

    pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        string="Pricelist",
        states={"draft": [("readonly", False)]},
        compute="_compute_pricelist_id",
        tracking=True,
        store=True,
        readonly=True,
        precompute=True,
        copy=True,
    )

    @api.constrains("pricelist_id", "currency_id")
    def _check_currency(self):
        if (
            not config["test_enable"]
            or (
                config["test_enable"]
                and self._context.get("force_check_currecy", False)
            )
        ) and self.filtered(
            lambda a: a.pricelist_id
            and a.is_sale_document()
            and a.pricelist_id.currency_id != a.currency_id
        ):
            raise UserError(_("Pricelist and Invoice need to use the same currency."))

    @api.depends("partner_id", "company_id")
    def _compute_pricelist_id(self):
        for invoice in self:
            if (
                invoice.partner_id
                and invoice.is_sale_document()
                and invoice.partner_id.property_product_pricelist
            ):
                invoice.pricelist_id = invoice.partner_id.property_product_pricelist

    @api.depends("pricelist_id")
    def _compute_currency_id(self):
        res = super()._compute_currency_id()
        for invoice in self:
            if (
                invoice.is_sale_document()
                and invoice.pricelist_id
                and invoice.currency_id != invoice.pricelist_id.currency_id
            ):
                invoice.currency_id = self.pricelist_id.currency_id
        return res

    def button_update_prices_from_pricelist(self):
        moves = self.filtered(lambda r: r.state == "draft")
        moves.invoice_line_ids._compute_price_unit()
        for line in moves.invoice_line_ids:
            line._onchange_quantity()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.depends("quantity")
    def _compute_price_unit(self):
        res = super()._compute_price_unit()
        for line in self:
            if not line.move_id.pricelist_id:
                continue
            line.with_context(
                check_move_validity=False
            ).price_unit = line._get_price_with_pricelist()
        return res

    @api.onchange("quantity")
    def _onchange_quantity(self):
        if (
            not self.move_id.pricelist_id
            or not self.product_id
            or not self.move_id.is_invoice()
        ):
            return
        if self.move_id.pricelist_id.discount_policy == "with_discount":
            self.with_context(check_move_validity=False).discount = 0.0
        else:
            final_price, rule_id = self._get_final_price_with_pricelist()
            base_price = self._get_base_price_with_pricelist_without_discount(rule_id)
            self.with_context(
                check_move_validity=False
            ).discount = self._calculate_discount(base_price, final_price)

    def _calculate_discount(self, base_price, final_price):
        if base_price == 0.0:
            return 0.0
        discount = (base_price - final_price) / base_price * 100
        if (discount < 0 and base_price > 0) or (discount > 0 and base_price < 0):
            discount = 0.0
        return discount

    def _get_final_price_with_pricelist(self):
        self.ensure_one()
        (final_price, rule_id,) = self.move_id.pricelist_id._get_product_price_rule(
            self.product_id,
            self.quantity or 1.0,
            uom=self.product_uom_id,
            date=self.move_id.invoice_date or fields.Date.today(),
        )
        return final_price, rule_id

    def _get_base_price_with_pricelist_without_discount(self, rule_id):
        self.ensure_one()
        product = self.product_id
        qty = self.quantity or 1.0
        date = self.move_id.invoice_date or fields.Date.today()
        uom = self.product_uom_id
        rule = self.env["product.pricelist.item"].browse(rule_id)
        while (
            rule.base == "pricelist"
            and rule.base_pricelist_id.discount_policy == "without_discount"
        ):
            new_rule_id = rule.base_pricelist_id._get_product_rule(
                product, qty, uom=uom, date=date
            )
            rule = self.env["product.pricelist.item"].browse(new_rule_id)
        return rule._compute_base_price(
            product, qty, uom, date, target_currency=self.currency_id
        )

    def _get_price_with_pricelist(self):
        price_unit = 0.0
        if self.move_id.pricelist_id and self.product_id and self.move_id.is_invoice():
            final_price, rule_id = self._get_final_price_with_pricelist()
            if self.move_id.pricelist_id.discount_policy == "with_discount":
                price_unit = self.env["account.tax"]._fix_tax_included_price_company(
                    final_price, self.product_id.taxes_id, self.tax_ids, self.company_id
                )
                self.with_context(check_move_validity=False).discount = 0.0
                return price_unit
            else:
                base_price = self._get_base_price_with_pricelist_without_discount(
                    rule_id
                )
                price_unit = max(base_price, final_price)
        return price_unit
