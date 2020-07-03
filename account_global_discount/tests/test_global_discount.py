# Copyright 2019 Tecnativa - David Vidal
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import exceptions
from odoo.tests import common


class TestGlobalDiscount(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.account_type = cls.env['account.account.type'].create({
            'name': 'Test',
            'type': 'receivable',
        })
        cls.account = cls.env['account.account'].create({
            'name': 'Test account',
            'code': 'TEST',
            'user_type_id': cls.account_type.id,
            'reconcile': True,
        })
        cls.global_discount_obj = cls.env['global.discount']
        cls.global_discount_1 = cls.global_discount_obj.create({
            'name': 'Test Discount 1',
            'discount_scope': 'sale',
            'discount': 20,
            'account_id': cls.account.id,
        })
        cls.global_discount_2 = cls.global_discount_obj.create({
            'name': 'Test Discount 2',
            'discount_scope': 'purchase',
            'discount': 30,
            'account_id': cls.account.id,
        })
        cls.global_discount_3 = cls.global_discount_obj.create({
            'name': 'Test Discount 3',
            'discount_scope': 'purchase',
            'discount': 50,
            'account_id': cls.account.id,
        })
        cls.partner_1 = cls.env['res.partner'].create({
            'name': 'Mr. Odoo',
        })
        cls.partner_2 = cls.env['res.partner'].create({
            'name': 'Mrs. Odoo',
        })
        cls.partner_2.supplier_global_discount_ids = cls.global_discount_2
        cls.tax = cls.env['account.tax'].create({
            'name': 'TAX 15%',
            'amount_type': 'percent',
            'type_tax_use': 'purchase',
            'amount': 15.0,
        })
        cls.invoice = cls.env['account.invoice'].create({
            'name': "Test Customer Invoice",
            'journal_id': cls.env['account.journal'].search(
                [('type', '=', 'sale')])[0].id,
            'partner_id': cls.partner_1.id,
            'account_id': cls.account.id,
            'type': 'in_invoice',
        })
        cls.invoice_line = cls.env['account.invoice.line']
        cls.invoice_line1 = cls.invoice_line.create({
            'invoice_id': cls.invoice.id,
            'name': 'Line 1',
            'price_unit': 200.0,
            'account_id': cls.account.id,
            'invoice_line_tax_ids': [(6, 0, [cls.tax.id])],
            'quantity': 1,
        })
        cls.invoice._onchange_invoice_line_ids()

    def test_01_global_invoice_succesive_discounts(self):
        """Add global discounts to the invoice"""
        self.assertAlmostEqual(self.invoice.amount_total, 230)
        self.assertAlmostEqual(self.invoice.tax_line_ids.base, 200.0)
        self.assertAlmostEqual(self.invoice.tax_line_ids.amount, 30.0)
        # Global discounts are applied to the base and taxes are recomputed:
        # 200 - 50% (global disc. 1) =  100
        self.invoice.global_discount_ids = self.global_discount_3
        self.invoice._onchange_global_discount_ids()
        self.assertEqual(len(self.invoice.invoice_global_discount_ids), 1)
        precision = self.env['decimal.precision'].precision_get('Discount')
        self.assertEqual(
            self.invoice.invoice_global_discount_ids.discount_display,
            '-50.{}%'.format('0' * precision))
        self.assertAlmostEqual(self.invoice.tax_line_ids.base, 100.0)
        self.assertAlmostEqual(self.invoice.tax_line_ids.amount, 15.0)
        self.assertAlmostEqual(self.invoice.amount_untaxed, 100.0)
        self.assertAlmostEqual(self.invoice.amount_total, 115.0)
        self.assertAlmostEqual(self.invoice.amount_global_discount, -100.0)
        # Global discounts are computed succecively:
        # 200 - 50% (global disc. 1) =  100
        # 100  - 30% (global disc. 2) =  70
        # The global discounts amount is then 200 - 70 = 130
        self.invoice.global_discount_ids += self.global_discount_2
        self.invoice._onchange_global_discount_ids()
        self.assertEqual(len(self.invoice.invoice_global_discount_ids), 2)
        self.assertAlmostEqual(self.invoice.tax_line_ids.base, 70.0)
        self.assertAlmostEqual(self.invoice.tax_line_ids.amount, 10.5)
        self.assertAlmostEqual(self.invoice.amount_untaxed, 70.0)
        self.assertAlmostEqual(self.invoice.amount_total, 80.5)
        self.assertAlmostEqual(self.invoice.amount_global_discount, -130.0)
        # Line discounts apply before global ones so:
        # 200 - 20% (line discount)  = 160
        # 160 - 50% (global disc. 1) =  80
        # 80  - 30% (global disc. 2) =  56
        # The global discounts amount is then 160 - 56 = 104
        self.invoice_line1.discount = 20
        self.invoice._onchange_invoice_line_ids()
        self.assertEqual(len(self.invoice.invoice_global_discount_ids), 2)
        self.assertAlmostEqual(self.invoice.tax_line_ids.base, 56.0)
        self.assertAlmostEqual(self.invoice.tax_line_ids.amount, 8.4)
        self.assertAlmostEqual(self.invoice.amount_untaxed, 56.0)
        self.assertAlmostEqual(self.invoice.amount_total, 64.4)
        self.assertAlmostEqual(self.invoice.amount_global_discount, -104.0)

    def test_02_global_invoice_discounts_from_partner(self):
        """Change the partner and his global discounts go to the invoice"""
        self.assertAlmostEqual(self.invoice.amount_total, 230)
        self.assertAlmostEqual(self.invoice.tax_line_ids.base, 200.0)
        self.assertAlmostEqual(self.invoice.tax_line_ids.amount, 30.0)
        # When we change the parter, his global discounts are fetched depending
        # on the type of the invoice. In this case, we fetch the supplier
        # global discounts
        self.invoice.partner_id = self.partner_2
        # trigger onchanges mimicking UI
        self.invoice._onchange_partner_id()
        self.invoice._onchange_global_discount_ids()
        self.assertAlmostEqual(self.invoice.tax_line_ids.base, 140.0)
        self.assertAlmostEqual(self.invoice.tax_line_ids.amount, 21.0)
        self.assertAlmostEqual(self.invoice.amount_untaxed, 140.0)
        self.assertAlmostEqual(self.invoice.amount_total, 161.0)
        self.assertAlmostEqual(self.invoice.amount_global_discount, -60.0)

    def test_03_multiple_taxes_multi_line(self):
        tax2 = self.env['account.tax'].create({
            'name': 'TAX 20%',
            'amount_type': 'percent',
            'type_tax_use': 'purchase',
            'amount': 20.0,
        })
        self.invoice_line.create({
            'invoice_id': self.invoice.id,
            'name': 'Line 2',
            'price_unit': 100.0,
            'account_id': self.account.id,
            'invoice_line_tax_ids': [(6, 0, [tax2.id])],
            'quantity': 1,
        })
        self.invoice.global_discount_ids = self.global_discount_1
        self.invoice._onchange_global_discount_ids()
        # Global discounts are applied to the base and taxes are recomputed:
        # 300 - 20% (global disc. 1) =  240
        self.assertEqual(len(self.invoice.invoice_global_discount_ids), 2)
        discount_tax_15 = self.invoice.invoice_global_discount_ids.filtered(
            lambda x: x.tax_ids == self.tax)
        discount_tax_20 = self.invoice.invoice_global_discount_ids.filtered(
            lambda x: x.tax_ids == tax2)
        self.assertAlmostEqual(discount_tax_15.discount_amount, 40)
        self.assertAlmostEqual(discount_tax_20.discount_amount, 20)
        tax_line_15 = self.invoice.tax_line_ids.filtered(
            lambda x: x.tax_id == self.tax)
        tax_line_20 = self.invoice.tax_line_ids.filtered(
            lambda x: x.tax_id == tax2)
        self.assertAlmostEqual(tax_line_15.base, 160)
        self.assertAlmostEqual(tax_line_15.amount, 24)
        self.assertAlmostEqual(tax_line_20.base, 80.0)
        self.assertAlmostEqual(tax_line_20.amount, 16)
        self.assertAlmostEqual(self.invoice.amount_untaxed, 240.0)
        self.assertAlmostEqual(self.invoice.amount_total, 280)
        self.assertAlmostEqual(self.invoice.amount_global_discount, -60.0)
        # Validate invoice for seeing result
        self.invoice.action_invoice_open()
        self.assertEqual(len(self.invoice.move_id.line_ids), 7)

    def test_04_multiple_taxes_same_line(self):
        tax2 = self.env['account.tax'].create({
            'name': 'Retention 20%',
            'amount_type': 'percent',
            'type_tax_use': 'purchase',
            'amount': -20.0,  # negative for testing more use cases
        })
        self.invoice_line1.invoice_line_tax_ids = [(4, tax2.id)]
        self.invoice.global_discount_ids = self.global_discount_1
        self.invoice._onchange_global_discount_ids()
        # Global discounts are applied to the base and taxes are recomputed:
        # 300 - 20% (global disc. 1) =  240
        self.assertEqual(len(self.invoice.invoice_global_discount_ids), 1)
        self.assertAlmostEqual(
            self.invoice.invoice_global_discount_ids.discount_amount, 40)
        self.assertEqual(
            self.invoice.invoice_global_discount_ids.tax_ids, self.tax + tax2)
        tax_line_15 = self.invoice.tax_line_ids.filtered(
            lambda x: x.tax_id == self.tax)
        tax_line_20 = self.invoice.tax_line_ids.filtered(
            lambda x: x.tax_id == tax2)
        self.assertAlmostEqual(tax_line_15.base, 160)
        self.assertAlmostEqual(tax_line_15.amount, 24)
        self.assertAlmostEqual(tax_line_20.base, 160.0)
        self.assertAlmostEqual(tax_line_20.amount, -32)
        self.assertAlmostEqual(self.invoice.amount_untaxed, 160.0)
        self.assertAlmostEqual(self.invoice.amount_total, 152)
        self.assertAlmostEqual(self.invoice.amount_global_discount, -40.0)
        # Validate invoice for seeing result
        self.invoice.action_invoice_open()
        move = self.invoice.move_id
        self.assertEqual(len(move.line_ids), 5)
        line = move.line_ids.filtered(lambda x: "Test Discount 1" in x.name)
        self.assertEqual(line.tax_ids, self.tax + tax2)

    def test_05_incompatible_taxes(self):
        # Line 1 with tax and tax2
        # Line 2 with only tax2
        tax2 = self.env['account.tax'].create({
            'name': 'Retention 20%',
            'amount_type': 'percent',
            'type_tax_use': 'purchase',
            'amount': -20.0,  # negative for testing more use cases
        })
        self.invoice_line1.invoice_line_tax_ids = [
            (4, tax2.id), (4, self.tax.id)]
        self.invoice_line.create({
            'invoice_id': self.invoice.id,
            'name': 'Line 2',
            'price_unit': 100.0,
            'account_id': self.account.id,
            'invoice_line_tax_ids': [(6, 0, [tax2.id])],
            'quantity': 1,
        })
        self.invoice.global_discount_ids = self.global_discount_1
        with self.assertRaises(exceptions.UserError):
            self.invoice._onchange_global_discount_ids()

    def test_06_no_taxes(self):
        self.invoice_line1.invoice_line_tax_ids = False
        self.invoice.global_discount_ids = self.global_discount_1
        with self.assertRaises(exceptions.UserError):
            self.invoice._onchange_global_discount_ids()
