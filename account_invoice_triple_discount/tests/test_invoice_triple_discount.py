# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase
from odoo.tests.common import Form


class TestInvoiceTripleDiscount(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestInvoiceTripleDiscount, cls).setUpClass()
        cls.Account = cls.env["account.account"]
        cls.AccountMove = cls.env["account.move"]
        cls.AccountTax = cls.env["account.tax"]
        cls.AccountType = cls.env["account.account.type"]
        cls.Partner = cls.env["res.partner"]
        cls.Journal = cls.env["account.journal"]

        cls.partner = cls.Partner.create({"name": "test"})
        cls.tax = cls.AccountTax.create(
            {
                "name": "TAX 15%",
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "amount": 15.0,
            }
        )
        cls.account_type = cls.AccountType.create(
            {"name": "Test", "type": "receivable", "internal_group": "income"}
        )
        cls.account = cls.Account.create(
            {
                "name": "Test account",
                "code": "TEST",
                "user_type_id": cls.account_type.id,
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
        """ Tests multiple discounts in line with taxes """
        invoice = self.create_simple_invoice(200)

        invoice_form = Form(invoice)
        with invoice_form.invoice_line_ids.edit(0) as line_form:
            line_form.discount = 50.0
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
            line_form.discount = 0
        invoice_form.save()
        self.assertEqual(invoice.amount_total, 69)

        # Charge 5% over price:
        with invoice_form.invoice_line_ids.edit(0) as line_form:
            line_form.discount = -5
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
            line_form.discount = 50.0
        invoice_form.save()
        self.assertEqual(invoice.amount_total, 365.0)
