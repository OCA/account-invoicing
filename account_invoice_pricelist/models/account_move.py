# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import config


class AccountMove(models.Model):
    _inherit = "account.move"

    pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        string="Pricelist",
        compute="_compute_pricelist_id",
        tracking=True,
        store=True,
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

    pricelist_item_id = fields.Many2one(
        comodel_name="product.pricelist.item", compute="_compute_pricelist_item_id"
    )

    @api.depends("product_id", "product_uom_id", "quantity")
    def _compute_pricelist_item_id(self):
        for line in self:
            if (
                not line.product_id
                or line.display_type != "product"
                or not line.move_id.pricelist_id
            ):
                line.pricelist_item_id = False
            else:
                line.pricelist_item_id = line.move_id.pricelist_id._get_product_rule(
                    line.product_id,
                    quantity=line.quantity or 1.0,
                    uom=line.product_uom_id,
                    date=line._get_move_date(),
                )

    def _get_move_date(self):
        self.ensure_one()
        return self.move_id.invoice_date

    @api.depends("product_id", "product_uom_id", "quantity")
    def _compute_discount(self):
        discount_enabled = self.env[
            "product.pricelist.item"
        ]._is_discount_feature_enabled()
        for line in self:
            if not (line.move_id.pricelist_id and discount_enabled):
                continue

            line.discount = 0.0

            if not line.pricelist_item_id._show_discount():
                # No pricelist rule was found for the product
                # therefore, the pricelist didn't apply any discount/change
                # to the existing sales price.
                continue

            line = line.with_company(line.company_id)
            pricelist_price = line._get_pricelist_price()
            base_price = line._get_pricelist_price_before_discount()

            if base_price != 0:  # Avoid division by zero
                discount = (base_price - pricelist_price) / base_price * 100
                if (discount > 0 and base_price > 0) or (
                    discount < 0 and base_price < 0
                ):
                    # only show negative discounts if price is negative
                    # otherwise it's a surcharge which shouldn't be shown
                    # to the customer
                    line.discount = discount

    @api.depends("quantity")
    def _compute_price_unit(self):
        res = super()._compute_price_unit()
        for line in self:
            line = line.with_company(line.company_id)
            if not line.move_id.pricelist_id:
                continue
            if not line.product_uom_id or not line.product_id:
                line.price_unit = 0.0
            else:
                price = line._get_display_price()
                line.with_context(
                    check_move_validity=False
                ).price_unit = line.product_id._get_tax_included_unit_price_from_price(
                    price,
                    product_taxes=line.product_id.taxes_id.filtered(
                        lambda tax, line=line: tax.company_id == line.env.company
                    ),
                    fiscal_position=line.move_id.fiscal_position_id,
                )
        return res

    def _get_display_price(self):
        """Compute the displayed unit price for a given line.

        Overridden in custom flows:
        * where the price is not specified by the pricelist
        * where the discount is not specified by the pricelist

        Note: self.ensure_one()
        """
        self.ensure_one()

        if self.product_id.type == "combo":
            return 0  # The display price of a combo line should always be 0.
        return self._get_display_price_ignore_combo()

    def _get_display_price_ignore_combo(self):
        """This helper method allows to compute the display price of a SOL,
        while ignoring combo logic.

        I.e. this method returns the display price of a SOL as if it were neither
        a combo line nor a combo item line.
        """
        self.ensure_one()

        pricelist_price = self._get_pricelist_price()

        if not self.pricelist_item_id._show_discount():
            # No pricelist rule found => no discount from pricelist
            return pricelist_price

        base_price = self._get_pricelist_price_before_discount()

        self._compute_discount()

        # negative discounts (= surcharge) are included in the display price
        return max(base_price, pricelist_price)

    def _get_pricelist_price(self):
        """Compute the price given by the pricelist for the given line information.

        :return: the product price in the move currency (without taxes)
        :rtype: float
        """
        self.ensure_one()
        self.product_id.ensure_one()

        price = self.pricelist_item_id._compute_price(
            product=self.product_id,
            quantity=self.quantity or 1.0,
            uom=self.product_uom_id,
            date=self._get_move_date(),
            currency=self.currency_id,
        )

        return price

    def _get_pricelist_price_before_discount(self):
        """Compute the price used as base for the pricelist price computation.

        :return: the product price in the move currency (without taxes)
        :rtype: float
        """
        self.ensure_one()
        self.product_id.ensure_one()

        return self.pricelist_item_id._compute_price_before_discount(
            product=self.product_id,
            quantity=self.quantity or 1.0,
            uom=self.product_uom_id,
            date=self._get_move_date(),
            currency=self.currency_id,
        )
