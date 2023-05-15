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
        for line in self.filtered(lambda r: r.state == "draft").invoice_line_ids:
            line.with_context(check_move_validity=False)._compute_price_unit()

    def _reverse_moves(self, default_values_list, cancel=True):
        if not default_values_list:
            default_values_list = [{} for move in self]
        for move, default_values in zip(self, default_values_list):
            default_values.update({
                'pricelist_id': move.pricelist_id.id,
            })
        return super(AccountMove, self)._reverse_moves(default_values_list=default_values_list, cancel=cancel)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _get_pricelist_rule(self):
        pricelist_rule = self.move_id.pricelist_id._get_product_rule(
            self.product_id,
            self.quantity or 1.0,
            uom=self.product_uom_id,
            date=self.move_id.invoice_date or fields.Date.today(),
        )
        pricelist_rule = self.env['product.pricelist.item'].browse(pricelist_rule)
        return pricelist_rule

    def _get_pricelist_price(self):
        """Compute the price given by the pricelist for the given line information.

        :return: the product sales price in the order currency (without taxes)
        :rtype: float
        """
        self.ensure_one()
        self.product_id.ensure_one()

        pricelist_rule = self._get_pricelist_rule()
        if not pricelist_rule:
            # No pricelist rule was found for the product
            return 0.0
        order_date = self.move_id.invoice_date or fields.Date.today()
        qty = self.quantity or 1.0
        uom = self.product_uom_id or self.product_id.uom_id

        price = pricelist_rule._compute_price(self.product_id, qty, uom, order_date, currency=self.currency_id)

        return price

    def _get_pricelist_price_before_discount(self):
        """Compute the price used as base for the pricelist price computation.

        :return: the product sales price in the order currency (without taxes)
        :rtype: float
        """
        self.ensure_one()
        self.product_id.ensure_one()

        pricelist_rule = self._get_pricelist_rule()
        invoice_date = self.move_id.invoice_date or fields.Date.today()
        product = self.product_id
        qty = self.quantity or 1.0
        uom = self.product_uom_id

        if pricelist_rule:
            pricelist_item = pricelist_rule
            if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                # Find the lowest pricelist rule whose pricelist is configured
                # to show the discount to the customer.
                while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                    rule_id = pricelist_item.base_pricelist_id._get_product_rule(
                        product, qty, uom=uom, date=invoice_date)
                    pricelist_item = self.env['product.pricelist.item'].browse(rule_id)

            pricelist_rule = pricelist_item

        price = pricelist_rule._compute_base_price(
            product,
            qty,
            uom,
            invoice_date,
            target_currency=self.currency_id,
        )

        return price

    def _get_display_price(self):
        """Compute the displayed unit price for a given line.

        Overridden in custom flows:
        * where the price is not specified by the pricelist
        * where the discount is not specified by the pricelist

        Note: self.ensure_one()
        """
        self.ensure_one()

        pricelist_item_id = self._get_pricelist_rule()
        pricelist_price = self._get_pricelist_price()


        if self.move_id.pricelist_id.discount_policy == 'with_discount':
            return pricelist_price

        if not pricelist_item_id:
            # No pricelist rule found => no discount from pricelist
            return pricelist_price

        base_price = self._get_pricelist_price_before_discount()

        # negative discounts (= surcharge) are included in the display price
        return max(base_price, pricelist_price)

    @api.depends('product_id', 'product_uom_id')
    def _compute_price_unit(self):
        for line in self:
            if not line.move_id.pricelist_id:
                return super()._compute_price_unit()
            if not line.product_id or line.display_type in ('line_section', 'line_note'):
                continue
            if line.move_id.is_sale_document(include_receipts=True):
                document_type = 'sale'
            elif line.move_id.is_purchase_document(include_receipts=True):
                document_type = 'purchase'
            else:
                document_type = 'other'
            price = line.with_company(line.company_id)._get_display_price()
            line.price_unit = line.product_id._get_tax_included_unit_price(
                line.move_id.company_id,
                line.move_id.currency_id,
                line.move_id.date,
                document_type,
                fiscal_position=line.move_id.fiscal_position_id,
                product_uom=line.product_uom_id,
                product_price_unit=price,
                product_currency=line.currency_id
            )
            line._calculate_discount()

    def _calculate_discount(self):
        for line in self:
            if not line.product_id or line.display_type:
                line.discount = 0.0

            if not (
                line.move_id.pricelist_id
                and line.move_id.pricelist_id.discount_policy == 'without_discount'
            ):
                continue

            line.discount = 0.0
            pricelist_item_id = self._get_pricelist_rule()
            if not pricelist_item_id:
                # No pricelist rule was found for the product
                # therefore, the pricelist didn't apply any discount/change
                # to the existing sales price.
                continue

            line = line.with_company(line.company_id)
            pricelist_price = line._get_pricelist_price()
            base_price = line._get_pricelist_price_before_discount()

            if base_price != 0:  # Avoid division by zero
                discount = (base_price - pricelist_price) / base_price * 100
                if (discount > 0 and base_price > 0) or (discount < 0 and base_price < 0):
                    # only show negative discounts if price is negative
                    # otherwise it's a surcharge which shouldn't be shown to the customer
                    line.discount = discount
