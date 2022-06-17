# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        string="Pricelist",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    @api.constrains("pricelist_id", "currency_id")
    def _check_currency(self):
        for sel in self.filtered(lambda a: a.pricelist_id and a.is_invoice()):
            if sel.pricelist_id.currency_id != sel.currency_id:
                raise UserError(
                    _("Pricelist and Invoice need to use the same currency.")
                )

    @api.onchange("partner_id", "company_id")
    def _onchange_partner_id_account_invoice_pricelist(self):
        if self.is_invoice():
            if (
                self.partner_id
                and self.move_type in ("out_invoice", "out_refund")
                and self.partner_id.property_product_pricelist
            ):
                self.pricelist_id = self.partner_id.property_product_pricelist
                self._set_pricelist_currency()

    @api.onchange("pricelist_id")
    def _set_pricelist_currency(self):
        if (
            self.is_invoice()
            and self.pricelist_id
            and self.currency_id != self.pricelist_id.currency_id
        ):
            self.currency_id = self.pricelist_id.currency_id

    def button_update_prices_from_pricelist(self):
        for inv in self.filtered(lambda r: r.state == "draft"):
            inv.invoice_line_ids._onchange_product_id_account_invoice_pricelist()
        self.filtered(lambda r: r.state == "draft").with_context(
            check_move_validity=False
        )._move_autocomplete_invoice_lines_values()
        self.filtered(lambda r: r.state == "draft").with_context(
            check_move_validity=False
        )._recompute_tax_lines()

    def _reverse_move_vals(self, default_values, cancel=True):
        move_vals = super(AccountMove, self)._reverse_move_vals(
            default_values, cancel=cancel
        )
        if self.pricelist_id:
            move_vals["pricelist_id"] = self.pricelist_id.id
        return move_vals


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange("product_id", "quantity")
    def _onchange_product_id_account_invoice_pricelist(self):
        for sel in self:
            if not sel.move_id.pricelist_id:
                return
            sel.with_context(check_move_validity=False).update(
                {"price_unit": sel._get_price_with_pricelist()}
            )

    @api.onchange("product_uom_id")
    def _onchange_uom_id(self):
        for sel in self:
            if (
                sel.move_id.is_invoice()
                and sel.move_id.state == "draft"
                and sel.move_id.pricelist_id
            ):
                price_unit = sel._get_computed_price_unit()
                taxes = sel._get_computed_taxes()
                if taxes and sel.move_id.fiscal_position_id:
                    price_subtotal = sel._get_price_total_and_subtotal(
                        price_unit=price_unit, taxes=taxes
                    )["price_subtotal"]
                    accounting_vals = sel._get_fields_onchange_subtotal(
                        price_subtotal=price_subtotal,
                        currency=self.move_id.company_currency_id,
                    )
                    amount_currency = accounting_vals["amount_currency"]
                    price_unit = sel._get_fields_onchange_balance(
                        amount_currency=amount_currency
                    ).get("price_unit", price_unit)
                sel.with_context(check_move_validity=False).update(
                    {"price_unit": price_unit}
                )
            else:
                super(AccountMoveLine, self)._onchange_uom_id()

    def _get_real_price_currency(self, product, rule_id, qty, uom, pricelist_id):
        PricelistItem = self.env["product.pricelist.item"]
        field_name = "lst_price"
        currency_id = None
        product_currency = product.currency_id
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            while (
                pricelist_item.base == "pricelist"
                and pricelist_item.base_pricelist_id
                and pricelist_item.base_pricelist_id.discount_policy
                == "without_discount"
            ):
                price, rule_id = pricelist_item.base_pricelist_id.with_context(
                    uom=uom.id
                ).get_product_price_rule(product, qty, self.move_id.partner_id)
                pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == "standard_price":
                field_name = "standard_price"
                product_currency = product.cost_currency_id
            elif (
                pricelist_item.base == "pricelist" and pricelist_item.base_pricelist_id
            ):
                field_name = "price"
                product = product.with_context(
                    pricelist=pricelist_item.base_pricelist_id.id
                )
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(
                    product_currency,
                    currency_id,
                    self.company_id or self.env.company,
                    self.move_id.invoice_date or fields.Date.today(),
                )

        product_uom = self.env.context.get("uom") or product.uom_id.id
        if uom and uom.id != product_uom:
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0

        return product[field_name] * uom_factor * cur_factor, currency_id

    def _calculate_discount(self, base_price, final_price):
        if not base_price:
            return 0.0
        discount = (base_price - final_price) / base_price * 100
        if (discount < 0 and base_price > 0) or (discount > 0 and base_price < 0):
            discount = 0.0
        return discount

    def _get_price_with_pricelist(self):
        price_unit = 0.0
        if self.move_id.pricelist_id and self.product_id and self.move_id.is_invoice():
            if self.move_id.pricelist_id.discount_policy == "with_discount":
                product = self.product_id.with_context(
                    lang=self.move_id.partner_id.lang,
                    partner=self.move_id.partner_id.id,
                    quantity=self.quantity,
                    date_order=self.move_id.invoice_date,
                    date=self.move_id.invoice_date,
                    pricelist=self.move_id.pricelist_id.id,
                    product_uom_id=self.product_uom_id.id,
                    fiscal_position=(
                        self.move_id.partner_id.property_account_position_id.id
                    ),
                )
                tax_obj = self.env["account.tax"]
                recalculated_price_unit = (
                    product.price * self.product_id.uom_id.factor
                ) / (self.product_uom_id.factor or 1.0)
                price_unit = tax_obj._fix_tax_included_price_company(
                    recalculated_price_unit,
                    product.taxes_id,
                    self.tax_ids,
                    self.company_id,
                )
                self.with_context(check_move_validity=False).discount = 0.0
            else:
                product_context = dict(
                    self.env.context,
                    partner_id=self.move_id.partner_id.id,
                    date=self.move_id.invoice_date or fields.Date.today(),
                    uom=self.product_uom_id.id,
                )
                final_price, rule_id = self.move_id.pricelist_id.with_context(
                    product_context
                ).get_product_price_rule(
                    self.product_id, self.quantity or 1.0, self.move_id.partner_id
                )
                base_price, currency = self.with_context(
                    product_context
                )._get_real_price_currency(
                    self.product_id,
                    rule_id,
                    self.quantity,
                    self.product_uom_id,
                    self.move_id.pricelist_id.id,
                )
                if currency != self.move_id.pricelist_id.currency_id:
                    base_price = currency._convert(
                        base_price,
                        self.move_id.pricelist_id.currency_id,
                        self.move_id.company_id or self.env.company,
                        self.move_id.invoice_date or fields.Date.today(),
                    )
                price_unit = max(base_price, final_price)
                self.with_context(
                    check_move_validity=False
                ).discount = self._calculate_discount(base_price, final_price)
        return price_unit

    def _get_computed_price_unit(self):
        price_unit = super(AccountMoveLine, self)._get_computed_price_unit()
        if self.move_id.pricelist_id and self.move_id.is_invoice():
            price_unit = self._get_price_with_pricelist()
        return price_unit
