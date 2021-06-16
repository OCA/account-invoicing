# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestInvoiceTripleDiscount(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestInvoiceTripleDiscount, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Test'})
        cls.tax = cls.env['account.tax'].create({
            'name': 'TAX 15%',
            'amount_type': 'percent',
            'type_tax_use': 'purchase',
            'amount': 15.0,
        })
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
        cls.invoice = cls.env['account.invoice'].create({
            'name': "Test Customer Invoice",
            'journal_id': cls.env['account.journal'].search(
                [('type', '=', 'sale')])[0].id,
            'partner_id': cls.partner.id,
            'account_id': cls.account.id,
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

    def test_01_discounts(self):
        """ Tests multiple discounts in line with taxes """
        # Adds a first discount
        self.invoice_line1.discount = 50.0
        self.invoice._onchange_invoice_line_ids()
        self.assertEqual(self.invoice.amount_total, 115.0)
        # Adds a second discount over the price calculated before
        self.invoice_line1.discount2 = 40.0
        self.invoice._onchange_invoice_line_ids()
        self.assertEqual(self.invoice.amount_total, 69.0)
        # Adds a third discount over the price calculated before
        self.invoice_line1.discount3 = 50.0
        self.invoice._onchange_invoice_line_ids()
        self.assertEqual(self.invoice.amount_total, 34.5)
        # Deletes first discount
        self.invoice_line1.discount = 0.0
        self.invoice._onchange_invoice_line_ids()
        self.assertEqual(self.invoice.amount_total, 69.0)
        # Charge 5% over price:
        self.invoice_line1.discount = -5.0
        self.invoice._onchange_invoice_line_ids()
        self.assertEqual(self.invoice.amount_total, 72.45)

    def test_02_discounts_multiple_lines(self):
        """ Tests multiple lines with mixed taxes """
        self.invoice_line2 = self.invoice_line.create({
            'invoice_id': self.invoice.id,
            'name': 'Line 1',
            'price_unit': 500.0,
            'account_id': self.account.id,
            'quantity': 1,
        })
        self.assertEqual(self.invoice_line2.price_subtotal, 500.0)
        self.invoice_line2.discount3 = 50.0
        self.invoice._onchange_invoice_line_ids()
        self.assertEqual(self.invoice_line2.price_subtotal, 250.0)
        self.assertEqual(self.invoice.amount_total, 480.0)
        self.invoice_line1.discount = 50.0
        self.invoice._onchange_invoice_line_ids()
        self.assertEqual(self.invoice.amount_total, 365.0)

    def test_03_discounts(self):
        """ Tests discounts in edge case """
        invoice = self.env['account.invoice'].create({
            'name': "Test Customer Invoice",
            'journal_id': self.env['account.journal'].search(
                [('type', '=', 'sale')])[0].id,
            'partner_id': self.partner.id,
            'account_id': self.account.id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Line 1',
                'price_unit': 25.0,
                'account_id': self.account.id,
                'quantity': 65,
                'discount': 50,
                'discount2': 13,
                'discount3': 0,
            })],
        })
        self.assertEqual(invoice.invoice_line_ids.price_subtotal, 706.88)

    def test_increased_precision(self):
        """
        Check that final discount is computed correctly
        when final discount's precision exceeds
        discount field's allowed precision.
        """
        invoice_line = self.invoice_line1
        discount_field = invoice_line._fields['discount']
        self.assertEqual(discount_field.digits[1], 2)
        invoice_line.discount = 45.0
        invoice_line.discount2 = 10.0
        invoice_line.discount3 = 5.0

        self.assertAlmostEqual(
            invoice_line._get_final_discount(),
            52.975,
            places=3,
        )
        invoice_line.triple_discount_preprocess()

        # Check that the line's discount still has all the 3 digits
        self.assertAlmostEqual(
            invoice_line.discount,
            52.975,
            places=3,
        )
        # Check that field's precision is not changed
        self.assertEqual(discount_field.digits[1], 2)
