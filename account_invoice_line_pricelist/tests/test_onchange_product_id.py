# -*- coding: utf-8 -*-
# © 2016 ONESTEiN BV (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestOnchangeProductId(TransactionCase):
    """Test that when an included tax is mapped by a fiscal position,
    the included tax must be subtracted to the price of the product.
    """

    def setUp(self):
        super(TestOnchangeProductId, self).setUp()
        curr_obj = self.env['res.currency']
        self.eur = curr_obj.search([('name', '=', 'EUR')], limit=1).id
        self.usd = curr_obj.search([('name', '=', 'USD')], limit=1).id
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'lst_price': 10.00,
        })
        version_dict1 = {
            'name': 'Test version 1',
            'items_id': [
                (0, 0, {
                    'name': 'Test item default',
                    'base': 1,
                    'price_discount': 0.1, })]
        }
        version_dict2 = {
            'name': 'Test version 2',
            'items_id': [
                (0, 0, {
                    'name': 'Test item default',
                    'base': 1,
                    'price_discount': 0.2, })]
        }
        self.plist1 = self.env['product.pricelist'].create(
            {'name': 'Test pricelist 1',
             'type': 'sale',
             'currency_id': self.usd,
             'version_id': [(0, 0, version_dict1)]})
        self.plist2 = self.env['product.pricelist'].create(
            {'name': 'Test pricelist 2',
             'type': 'sale',
             'currency_id': self.usd,
             'version_id': [(0, 0, version_dict2)]})
        self.partner = self.env['res.partner'].create(
            {'name': 'Test partner',
             'property_product_pricelist': self.plist1.id})
        self.invoice_line = self.env['account.invoice.line'].create(
            {'name': 'Test line',
             'quantity': 1.0,
             'price_unit': 1.0})

    def test_onchange_product_id_pricelist(self):

        currency = self.env['res.currency'].browse(self.eur)
        rate = currency.rate_silent
        price_unit = currency.round(10.00 * rate)
        exp_value = currency.round((11.00 * rate))
        res = self.invoice_line.product_id_change(
            self.product.id, self.product.uom_id.id, qty=1.0,
            partner_id=self.partner.id, currency_id=self.eur,
            price_unit=price_unit, company_id=self.env.user.company_id.id)

        self.assertLessEqual(
            abs(exp_value - res['value']['price_unit']), 0.0001,
            "ERROR in getting price from pricelist")

    def test_onchange_product_id_invoice_pricelist(self):

        currency = self.env['res.currency'].browse(self.usd)
        rate = currency.rate_silent
        price_unit = currency.round(10.00 * rate)
        exp_value = currency.round((12.00 * rate))
        res = (
            self.invoice_line
            .with_context({'pricelist_id': self.plist2.id})
            .product_id_change(
                self.product.id, self.product.uom_id.id, qty=1.0,
                partner_id=self.partner.id, currency_id=self.usd,
                price_unit=price_unit, company_id=self.env.user.company_id.id)
        )

        self.assertLessEqual(
            abs(exp_value - res['value']['price_unit']), 0.0001,
            "ERROR in getting price from pricelist")

    def test_onchange_product_id_different_currency(self):

        currency = self.env['res.currency'].browse(self.usd)
        rate = currency.rate_silent
        price_unit = currency.round(10.00 * rate)
        exp_value = currency.round((11.00 * rate))
        res = self.invoice_line.product_id_change(
            self.product.id, self.product.uom_id.id, qty=1.0,
            partner_id=self.partner.id, currency_id=self.usd,
            price_unit=price_unit, company_id=self.env.user.company_id.id)

        self.assertLessEqual(
            abs(exp_value - res['value']['price_unit']), 0.0001,
            "ERROR in getting price from pricelist")
