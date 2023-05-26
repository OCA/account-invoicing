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
        self.filtered(
            lambda r: r.state == "draft"
        ).invoice_line_ids._compute_price_unit()


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

    def _calculate_discount(self, base_price, final_price):
        discount = (base_price - final_price) / base_price * 100
        if (discount < 0 and base_price > 0) or (discount > 0 and base_price < 0):
            discount = 0.0
        return discount

    def _get_price_with_pricelist(self):
        price_unit = 0.0
        if self.move_id.pricelist_id and self.product_id and self.move_id.is_invoice():
            product = self.product_id
            qty = self.quantity or 1.0
            date = self.move_id.invoice_date or fields.Date.today()
            uom = self.product_uom_id
            (final_price, rule_id,) = self.move_id.pricelist_id._get_product_price_rule(
                product,
                qty,
                uom=uom,
                date=date,
            )
            if self.move_id.pricelist_id.discount_policy == "with_discount":
                price_unit = self.env["account.tax"]._fix_tax_included_price_company(
                    final_price,
                    product.taxes_id,
                    self.tax_ids,
                    self.company_id,
                )
                self.with_context(check_move_validity=False).discount = 0.0
                return price_unit
            else:
                rule_id = self.env["product.pricelist.item"].browse(rule_id)
                while (
                    rule_id.base == "pricelist"
                    and rule_id.base_pricelist_id.discount_policy == "without_discount"
                ):
                    new_rule_id = rule_id.base_pricelist_id._get_product_rule(
                        product, qty, uom=uom, date=date
                    )
                    rule_id = self.env["product.pricelist.item"].browse(new_rule_id)
                base_price = rule_id._compute_base_price(
                    product,
                    qty,
                    uom,
                    date,
                    target_currency=self.currency_id,
                )
                price_unit = max(base_price, final_price)
                self.with_context(
                    check_move_validity=False
                ).discount = self._calculate_discount(base_price, final_price)
        return price_unit
