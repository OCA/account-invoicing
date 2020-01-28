# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import SavepointCase
from odoo.tests.common import Form


class TestInvoiceTripleDiscount(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestInvoiceTripleDiscount, cls).setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test"})
        cls.journal = cls.env["account.journal"].search([("type", "=", "sale")])[0]
        cls.tax = cls.env["account.tax"].create(
            {
                "name": "TAX 15%",
                "amount_type": "percent",
                "type_tax_use": "purchase",
                "amount": 15.0,
            }
        )
        cls.account_type = cls.env["account.account.type"].create(
            {"name": "Test", "type": "other", "internal_group": "income"}
        )
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST",
                "user_type_id": cls.account_type.id,
                "reconcile": True,
            }
        )
        cls.invoice = cls.env["account.move"].create(
            {
                "name": "Test Customer Invoice",
                "journal_id": cls.journal.id,
                "partner_id": cls.partner.id,
                "type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        None,
                        {
                            "name": "Line 1",
                            "account_id": cls.account.id,
                            "quantity": 1,
                            "price_unit": 200.0,
                            "tax_ids": [(6, 0, [cls.tax.id])],
                        },
                    )
                ],
            }
        )
        cls.invoice_line1 = cls.invoice.invoice_line_ids[0]

    def test_01_discounts(self):
        """ Tests multiple discounts in line with taxes """
        # Adds a first discount
        move_form = Form(self.invoice)

        with move_form.invoice_line_ids.edit(0) as line_form:
            line_form.discount1 = 50.0
        move_form.save()
        self.assertEqual(self.invoice.amount_total, 115.0)

        with move_form.invoice_line_ids.edit(0) as line_form:
            line_form.discount2 = 40.0
        move_form.save()
        self.assertEqual(self.invoice.amount_total, 69.0)

        with move_form.invoice_line_ids.edit(0) as line_form:
            line_form.discount3 = 50.0
        move_form.save()
        self.assertEqual(self.invoice.amount_total, 34.5)

        with move_form.invoice_line_ids.edit(0) as line_form:
            line_form.discount1 = 0.0
        move_form.save()
        self.assertEqual(self.invoice.amount_total, 69.0)

        with move_form.invoice_line_ids.edit(0) as line_form:
            line_form.discount1 = -5.0
        move_form.save()
        self.assertEqual(self.invoice.amount_total, 72.45)

    def test_02_discounts_multiple_lines(self):
        # """ Tests multiple lines with mixed taxes """
        self.invoice.write(
            {
                "invoice_line_ids": [
                    (
                        0,
                        None,
                        {
                            "move_id": self.invoice.id,
                            "name": "Line 2",
                            "price_unit": 500.0,
                            "account_id": self.account.id,
                            "quantity": 1,
                        },
                    )
                ],
            }
        )

        move_form = Form(self.invoice)

        with move_form.invoice_line_ids.edit(1) as line_form:
            line_form.discount3 = 50.0
        move_form.save()
        self.assertEqual(self.invoice.amount_total, 480.0)

        with move_form.invoice_line_ids.edit(0) as line_form:
            line_form.discount1 = 50.0
        move_form.save()
        self.assertEqual(self.invoice.amount_total, 365.0)
