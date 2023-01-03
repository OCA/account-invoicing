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
        if (
            self.partner_id
            and self.is_sale_document()
            and self.partner_id.property_product_pricelist
        ):
            self.pricelist_id = self.partner_id.property_product_pricelist

    @api.onchange("pricelist_id")
    def _set_pricelist_currency(self):
        if (
            self.is_invoice()
            and self.pricelist_id
            and self.currency_id != self.pricelist_id.currency_id
        ):
            self.currency_id = self.pricelist_id.currency_id

    def button_update_prices_from_pricelist(self):
        self.filtered(
            lambda r: r.state == "draft"
        ).invoice_line_ids._onchange_product_id_account_invoice_pricelist()


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
