# Copyright 2017 Tecnativa - David Vidal
# Copyright 2023 Simone Rubino - Aion Tech
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form

from odoo.addons.base.tests.common import BaseCommon


class TestInvoiceTripleDiscount(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super(TestInvoiceTripleDiscount, cls).setUpClass()
        cls.env.user.groups_id += cls.env.ref("product.group_discount_per_so_line")
        cls.Account = cls.env["account.account"]
        cls.AccountMove = cls.env["account.move"]
        cls.AccountTax = cls.env["account.tax"]
        cls.Partner = cls.env["res.partner"]
        cls.Journal = cls.env["account.journal"]

        cls.tax = cls.AccountTax.create(
            {
                "name": "TAX 15%",
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "amount": 15.0,
                "country_id": cls.env.ref("base.us").id,
            }
        )
        cls.account = cls.Account.create(
            {
                "name": "Test account",
                "code": "TEST",
                "account_type": "asset_receivable",
                "reconcile": True,
            }
        )
        cls.sale_journal = cls.Journal.search([("type", "=", "sale")], limit=1)

    def create_simple_invoice(self, amount):
        invoice_form = Form(
            self.AccountMove.with_context(
                default_move_type="out_invoice",
                default_journal_id=self.sale_journal.id,
            )
        )
        invoice_form.partner_id = self.partner

        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.name = "Line 1"
            line_form.quantity = 1
            line_form.price_unit = amount
            line_form.tax_ids.clear()
            line_form.tax_ids.add(self.tax)

        invoice = invoice_form.save()
        return invoice

    def test_01_discounts(self):
        """Tests multiple discounts in line with taxes"""
        invoice = self.create_simple_invoice(200)

        invoice_form = Form(invoice)
        with invoice_form.invoice_line_ids.edit(0) as line_form:
            line_form.discount1 = 50.0
        invoice_form.save()

        invoice_line = invoice.invoice_line_ids[0]

        # Adds a first discount
        self.assertEqual(invoice.amount_total, 115.0)

        # Adds a second discount over the price calculated before
        with invoice_form.invoice_line_ids.edit(0) as line_form:
            line_form.discount2 = 40.0
        invoice_form.save()
        self.assertEqual(invoice.amount_total, 69.0)

        # Adds a third discount over the price calculated before
        with invoice_form.invoice_line_ids.edit(0) as line_form:
            line_form.discount3 = 50.0
        invoice_form.save()
        self.assertEqual(invoice.amount_total, 34.5)

        # Deletes first discount
        with invoice_form.invoice_line_ids.edit(0) as line_form:
            line_form.discount1 = 0
        invoice_form.save()
        self.assertEqual(invoice.amount_total, 69)

        # Charge 5% over price:
        with invoice_form.invoice_line_ids.edit(0) as line_form:
            line_form.discount1 = -5
        invoice_form.save()
        self.assertEqual(invoice.amount_total, 72.45)

        self.assertEqual(invoice_line.price_unit, 200)

    def test_02_discounts_multiple_lines(self):
        invoice = self.create_simple_invoice(200)
        invoice_form = Form(invoice)
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.name = "Line 2"
            line_form.quantity = 1
            line_form.price_unit = 500
            line_form.tax_ids.clear()
        invoice_form.save()

        invoice_line2 = invoice.invoice_line_ids[1]
        self.assertEqual(invoice_line2.price_subtotal, 500.0)

        with invoice_form.invoice_line_ids.edit(1) as line_form:
            line_form.discount3 = 50.0
        invoice_form.save()
        self.assertEqual(invoice.amount_total, 480.0)

        with invoice_form.invoice_line_ids.edit(0) as line_form:
            line_form.discount1 = 50.0
        invoice_form.save()
        self.assertEqual(invoice.amount_total, 365.0)

    def test_03_discounts_decimals_price(self):
        """
        Tests discount with decimals price
        causing a round up after discount
        """
        invoice = self.create_simple_invoice(0)
        invoice_form = Form(invoice)
        with invoice_form.invoice_line_ids.edit(0) as line_form:
            line_form.name = "Line Decimals"
            line_form.quantity = 9950
            line_form.price_unit = 0.14
            line_form.tax_ids.clear()
        invoice_form.save()

        invoice_line1 = invoice.invoice_line_ids[0]

        self.assertEqual(invoice_line1.price_subtotal, 1393.0)

        with invoice_form.invoice_line_ids.edit(0) as line_form:
            line_form.discount1 = 15.0
        invoice_form.save()

        self.assertEqual(invoice_line1.price_subtotal, 1184.05)

    def test_04_discounts_decimals_tax(self):
        """
        Tests amount tax with discount
        """
        invoice = self.create_simple_invoice(0)
        invoice_form = Form(invoice)
        with invoice_form.invoice_line_ids.edit(0) as line_form:
            line_form.name = "Line Decimals"
            line_form.quantity = 9950
            line_form.price_unit = 0.14
            line_form.discount1 = 0
            line_form.discount2 = 0
        invoice_form.save()

        self.assertEqual(invoice.amount_tax, 208.95)
        with invoice_form.invoice_line_ids.edit(0) as line_form:
            line_form.discount1 = 15.0
        invoice_form.save()

    def test_06_round_discount(self):
        """Discount value is rounded correctly"""
        invoice = self.create_simple_invoice(0)
        invoice_line = invoice.invoice_line_ids[0]
        invoice_line.discount1 = 100
        self.assertEqual(invoice_line.discount1, 100)
        self.assertEqual(invoice_line.discount, 100)

    def test_07_round_tax_discount(self):
        """Discount value is rounded correctly when taxes change"""
        invoice = self.create_simple_invoice(0)
        invoice_line = invoice.invoice_line_ids[0]
        invoice_line.discount1 = 100
        invoice_line.tax_ids = False
        self.assertEqual(invoice_line.discount1, 100)
        self.assertEqual(invoice_line.discount, 100)

    def test_tax_compute_with_lock_date(self):
        # Check that the tax computation works even if the lock date is set
        invoice = self.create_simple_invoice(0)
        invoice_form = Form(invoice)
        with invoice_form.invoice_line_ids.edit(0) as line_form:
            line_form.name = "Line Decimals"
            line_form.quantity = 9950
            line_form.price_unit = 0.14
            line_form.discount1 = 10
            line_form.discount2 = 20
        invoice_form.save()
        invoice_line = invoice.invoice_line_ids[0]
        invoice.action_post()
        self.env.user.company_id.fiscalyear_lock_date = "2000-01-01"
        invoice_line._compute_all_tax()
