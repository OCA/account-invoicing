# Copyright 2016 Tecnativa - Carlos Dauden
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestSaleTimesheetDescription(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleTimesheetDescription, cls).setUpClass()
        # Make sure user is in English
        cls.env['res.lang'].load_lang('en_US')
        cls.env.user.lang = 'en_US'
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test partner',
        })
        cls.product_uom = cls.env.ref('product.product_uom_unit')
        cls.product = cls.env['product.product'].create({
            'name': 'Test product',
            'service_type': 'timesheet',
            'uom_id': cls.product_uom.id,
        })
        cls.analytic_account = cls.env['account.analytic.account'].create({
            'name': 'Test analytic account',
        })
        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'partner_invoice_id': cls.partner.id,
            'partner_shipping_id': cls.partner.id,
            'pricelist_id': cls.partner.property_product_pricelist.id,
            'analytic_account_id': cls.analytic_account.id,
            'order_line': [
                (0, 0, {
                    'name': cls.product.name,
                    'product_id': cls.product.id,
                    'product_uom_qty': 5,
                    'product_uom': cls.product.uom_id.id,
                    'price_unit': cls.product.list_price,
                }),
            ],
        })
        cls.analytic_line = cls.env['account.analytic.line'].create({
            'account_id': cls.analytic_account.id,
            'date': '2017-08-04',
            'name': 'Test description 1234567890',
            'product_uom_id': cls.product_uom.id,
            'so_line': cls.sale_order.order_line[0].id,
            'unit_amount': 10.5,
            'user_id': cls.env.user.id,
        })

    def _test_sale_time_description(self, desc_option, expected):
        self.sale_order.timesheet_invoice_description = desc_option
        self.sale_order.action_confirm()
        invoice_id = self.sale_order.with_context(
            test_timesheet_description=True
        ).action_invoice_create()
        invoice = self.env['account.invoice'].browse(invoice_id)
        self.assertEqual(invoice.invoice_line_ids[0].name, expected)

        # trigger the creation of another invoice
        for line in self.sale_order.order_line:
            line.product_uom_qty += 1
        invoice_id = self.sale_order.with_context(
            test_timesheet_description=True
        ).action_invoice_create()
        invoice = self.env['account.invoice'].browse(invoice_id)
        self.assertEqual(invoice.invoice_line_ids[0].name, expected)

    def test_sale_timesheet_description_000(self):
        self._test_sale_time_description(
            '000',
            'Test product',
        )

    def test_sale_timesheet_description_111(self):
        self._test_sale_time_description(
            '111',
            'Test product\n'
            '2017-08-04 - 10.5 Unit(s) - Test description 1234567890',
        )

    def test_sale_timesheet_description_101(self):
        self._test_sale_time_description(
            '101',
            'Test product\n'
            '2017-08-04 - Test description 1234567890',
        )

    def test_sale_timesheet_description_001(self):
        self._test_sale_time_description(
            '001',
            'Test product\n'
            'Test description 1234567890',
        )

    def test_sale_timesheet_description_011(self):
        self._test_sale_time_description(
            '011',
            'Test product\n'
            '10.5 Unit(s) - Test description 1234567890',
        )

    def test_settings(self):
        settings = self.env['res.config.settings'].create({})
        settings.default_timesheet_invoice_description = '101'
        settings.execute()
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'pricelist_id': self.partner.property_product_pricelist.id,
        })
        self.assertEqual(sale_order.timesheet_invoice_description, '101')
