# Copyright 2019 Tecnativa - David Vidal
# Copyright 2020 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestGlobalDiscount(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.env.ref("base_global_discount.group_global_discount").write(
            {"users": [(4, cls.env.user.id)]}
        )
        cls.currency_eur = cls.env.ref("base.EUR")
        cls.currency_usd = cls.env.ref("base.USD")
        cls.currency_usd.active = True
        # Make sure the currency of the company is USD, as this not always happens
        # To be removed in V17: https://github.com/odoo/odoo/pull/107113
        cls.company = cls.env.company
        cls.env.cr.execute(
            "UPDATE res_company SET currency_id = %s WHERE id = %s",
            (cls.env.ref("base.USD").id, cls.company.id),
        )
        cls.account = cls.env["account.account"].create(
            {
                "name": "Test account",
                "code": "TEST",
                "account_type": "income_other",
                "reconcile": True,
            }
        )
        cls.account_receivable = cls.env["account.account"].create(
            {
                "name": "Test receivable account",
                "code": "ACCRV",
                "account_type": "asset_receivable",
                "reconcile": True,
            }
        )
        cls.account_payable = cls.env["account.account"].create(
            {
                "name": "Test receivable account",
                "code": "ACCPAY",
                "account_type": "liability_payable",
                "reconcile": True,
            }
        )
        cls.global_discount_obj = cls.env["global.discount"]
        cls.global_discount_1 = cls.global_discount_obj.create(
            {
                "name": "Test Discount 1",
                "discount_scope": "sale",
                "discount": 20,
                "account_id": cls.account.id,
                "sequence": 3,
            }
        )
        cls.global_discount_2 = cls.global_discount_obj.create(
            {
                "name": "Test Discount 2",
                "discount_scope": "purchase",
                "discount": 30,
                "account_id": cls.account.id,
                "sequence": 2,
            }
        )
        cls.global_discount_3 = cls.global_discount_obj.create(
            {
                "name": "Test Discount 3",
                "discount_scope": "purchase",
                "discount": 50,
                "account_id": cls.account.id,
                "sequence": 1,
            }
        )
        cls.partner_1 = cls.env["res.partner"].create(
            {
                "name": "Mr. Odoo",
                "property_account_receivable_id": cls.account_receivable.id,
                "property_account_payable_id": cls.account_payable.id,
            }
        )
        cls.partner_2 = cls.env["res.partner"].create(
            {
                "name": "Mrs. Odoo",
                "property_account_receivable_id": cls.account_receivable.id,
                "property_account_payable_id": cls.account_payable.id,
            }
        )
        cls.partner_2.supplier_global_discount_ids = cls.global_discount_2
        cls.tax = cls.tax_purchase_a
        cls.tax.amount = 15
        cls.tax_0 = cls.tax_purchase_b
        cls.tax_0.amount = 0
        cls.journal = cls.env["account.journal"].create(
            {"name": "Test purchase journal", "code": "TPUR", "type": "purchase"}
        )
        cls.invoice_line = cls.env["account.move.line"]
        invoice_form = Form(
            cls.env["account.move"].with_context(
                default_move_type="in_invoice",
                test_account_global_discount=True,
            )
        )
        invoice_form.partner_id = cls.partner_1
        invoice_form.ref = "Test global discount"
        with invoice_form.invoice_line_ids.new() as line_form:
            line_form.name = "Line 1"
            line_form.price_unit = 200.0
            line_form.quantity = 1
            line_form.tax_ids.clear()
            line_form.tax_ids.add(cls.tax)
        cls.invoice = invoice_form.save()

    def test_01_global_invoice_succesive_discounts(self):
        """Add global discounts to the invoice"""
        invoice_tax_line = self.invoice.line_ids.filtered("tax_line_id")
        self.assertAlmostEqual(self.invoice.amount_total, 230)
        self.assertAlmostEqual(invoice_tax_line.tax_base_amount, 200.0)
        self.assertAlmostEqual(invoice_tax_line.balance, 30.0)
        # Global discounts are applied to the base and taxes are recomputed:
        # 200 - 50% (global disc. 3) =  100
        with Form(self.invoice) as invoice_form:
            invoice_form.global_discount_ids.clear()
            invoice_form.global_discount_ids.add(self.global_discount_3)
        self.assertEqual(len(self.invoice.invoice_global_discount_ids), 1)
        precision = self.env["decimal.precision"].precision_get("Discount")
        self.assertEqual(
            self.invoice.invoice_global_discount_ids.discount_display,
            "-50.{}%".format("0" * precision),
        )
        invoice_tax_line = self.invoice.line_ids.filtered("tax_line_id")
        self.assertAlmostEqual(invoice_tax_line.tax_base_amount, 100.0)
        self.assertAlmostEqual(invoice_tax_line.balance, 15.0)
        self.assertAlmostEqual(self.invoice.amount_untaxed, 100.0)
        self.assertAlmostEqual(self.invoice.amount_total, 115.0)
        self.assertAlmostEqual(self.invoice.amount_global_discount, -100.0)
        # Global discounts are computed succecively:
        # 200 - 50% (global disc. 1) =  100
        # 100  - 30% (global disc. 2) =  70
        # The global discounts amount is then 200 - 70 = 130
        with Form(self.invoice) as invoice_form:
            invoice_form.global_discount_ids.add(self.global_discount_2)
        self.assertEqual(len(self.invoice.invoice_global_discount_ids), 2)
        invoice_tax_line = self.invoice.line_ids.filtered("tax_line_id")
        self.assertAlmostEqual(invoice_tax_line.tax_base_amount, 70.0)
        self.assertAlmostEqual(invoice_tax_line.balance, 10.5)
        self.assertAlmostEqual(self.invoice.amount_untaxed, 70.0)
        self.assertAlmostEqual(self.invoice.amount_total, 80.5)
        self.assertAlmostEqual(self.invoice.amount_global_discount, -130.0)
        # Line discounts apply before global ones so:
        # 200 - 20% (line discount)  = 160
        # 160 - 50% (global disc. 1) =  80
        # 80  - 30% (global disc. 2) =  56
        # The global discounts amount is then 160 - 56 = 104
        with Form(self.invoice) as invoice_form:
            with invoice_form.invoice_line_ids.edit(0) as line_form:
                line_form.discount = 20
        self.assertEqual(len(self.invoice.invoice_global_discount_ids), 2)
        invoice_tax_line = self.invoice.line_ids.filtered("tax_line_id")
        self.assertAlmostEqual(invoice_tax_line.tax_base_amount, 56.0)
        self.assertAlmostEqual(invoice_tax_line.balance, 8.4)
        self.assertAlmostEqual(self.invoice.amount_untaxed, 56.0)
        self.assertAlmostEqual(self.invoice.amount_total, 64.4)
        self.assertAlmostEqual(self.invoice.amount_global_discount, -104.0)

    def test_02_global_invoice_discounts_from_partner(self):
        """Change the partner and his global discounts go to the invoice"""
        invoice_tax_line = self.invoice.line_ids.filtered("tax_line_id")
        self.assertAlmostEqual(self.invoice.amount_total, 230)
        self.assertAlmostEqual(invoice_tax_line.tax_base_amount, 200.0)
        self.assertAlmostEqual(invoice_tax_line.balance, 30.0)
        # When we change the parter, his global discounts are fetched depending
        # on the type of the invoice. In this case, we fetch the supplier
        # global discounts
        with Form(self.invoice) as invoice_form:
            invoice_form.partner_id = self.partner_2
        self.assertAlmostEqual(invoice_tax_line.tax_base_amount, 140.0)
        self.assertAlmostEqual(invoice_tax_line.balance, 21.0)
        self.assertAlmostEqual(self.invoice.amount_untaxed, 140.0)
        self.assertAlmostEqual(self.invoice.amount_total, 161.0)
        self.assertAlmostEqual(self.invoice.amount_global_discount, -60.0)

    def test_03_multiple_taxes_multi_line(self):
        tax2 = self.tax.copy(default={"amount": 20.0})
        with Form(self.invoice) as invoice_form:
            invoice_form.global_discount_ids.add(self.global_discount_1)
            with invoice_form.invoice_line_ids.new() as line_form:
                line_form.name = "Line 2"
                line_form.price_unit = 100.0
                line_form.quantity = 1
                line_form.tax_ids.clear()
                line_form.tax_ids.add(tax2)
        self.assertEqual(len(self.invoice.invoice_global_discount_ids), 2)
        discount_tax_15 = self.invoice.invoice_global_discount_ids.filtered(
            lambda x: x.tax_ids == self.tax
        )
        discount_tax_20 = self.invoice.invoice_global_discount_ids.filtered(
            lambda x: x.tax_ids == tax2
        )
        self.assertAlmostEqual(discount_tax_15.discount_amount, 40)
        self.assertAlmostEqual(discount_tax_20.discount_amount, 20)
        tax_line_15 = self.invoice.line_ids.filtered(
            lambda x: x.tax_line_id == self.tax
        )
        tax_line_20 = self.invoice.line_ids.filtered(lambda x: x.tax_line_id == tax2)
        self.assertAlmostEqual(tax_line_15.tax_base_amount, 160)
        self.assertAlmostEqual(tax_line_15.balance, 24)
        self.assertAlmostEqual(tax_line_20.tax_base_amount, 80.0)
        self.assertAlmostEqual(tax_line_20.balance, 16)
        self.assertAlmostEqual(self.invoice.amount_untaxed, 240.0)
        self.assertAlmostEqual(self.invoice.amount_total, 280)
        self.assertAlmostEqual(self.invoice.amount_global_discount, -60.0)
        # Check journal items validity
        lines = self.invoice.line_ids
        line_15 = lines.filtered(
            lambda x: x.invoice_global_discount_id and x.tax_ids == self.tax
        )
        self.assertAlmostEqual(line_15.credit, 40)
        line_20 = lines.filtered(
            lambda x: x.invoice_global_discount_id and x.tax_ids == tax2
        )
        self.assertAlmostEqual(line_20.credit, 20)

    def test_04_multiple_taxes_same_line(self):
        tax2 = self.tax.copy(
            default={"amount": -20.0}
        )  # negative for testing more use cases
        with Form(self.invoice.with_context(check_move_validity=False)) as invoice_form:
            invoice_form.global_discount_ids.add(self.global_discount_1)
            with invoice_form.invoice_line_ids.edit(0) as line_form:
                line_form.tax_ids.add(tax2)
        # Global discounts are applied to the base and taxes are recomputed:
        # 300 - 20% (global disc. 1) =  240
        self.assertEqual(len(self.invoice.invoice_global_discount_ids), 1)
        self.assertAlmostEqual(
            self.invoice.invoice_global_discount_ids.discount_amount, 40
        )
        self.assertEqual(
            self.invoice.invoice_global_discount_ids.tax_ids, self.tax + tax2
        )
        tax_line_15 = self.invoice.line_ids.filtered(
            lambda x: x.tax_line_id == self.tax
        )
        tax_line_20 = self.invoice.line_ids.filtered(lambda x: x.tax_line_id == tax2)
        self.assertAlmostEqual(tax_line_15.tax_base_amount, 160)
        self.assertAlmostEqual(tax_line_15.balance, 24)
        self.assertAlmostEqual(tax_line_20.tax_base_amount, 160.0)
        self.assertAlmostEqual(tax_line_20.balance, -32)
        self.assertAlmostEqual(self.invoice.amount_untaxed, 160.0)
        self.assertAlmostEqual(self.invoice.amount_total, 152)
        self.assertAlmostEqual(self.invoice.amount_global_discount, -40.0)

    def test_05_incompatible_taxes(self):
        # Line 1 with tax and tax2
        # Line 2 with only tax2
        tax2 = self.tax.copy(
            default={"amount": -20.0}
        )  # negative for testing more use cases
        with self.assertRaises(exceptions.UserError):
            with Form(self.invoice) as invoice_form:
                invoice_form.global_discount_ids.add(self.global_discount_1)
                with invoice_form.invoice_line_ids.new() as line_form:
                    line_form.name = "Line 2"
                    line_form.price_unit = 100.0
                    line_form.quantity = 1
                    line_form.tax_ids.clear()
                    line_form.tax_ids.add(self.tax)
                    line_form.tax_ids.add(tax2)

    def test_06_no_taxes(self):
        with self.assertRaises(exceptions.UserError):
            with Form(self.invoice) as invoice_form:
                invoice_form.global_discount_ids.add(self.global_discount_1)
                with invoice_form.invoice_line_ids.edit(0) as line_form:
                    line_form.tax_ids.clear()

    def test_07_line_with_tax_0(self):
        with Form(self.invoice) as invoice_form:
            invoice_form.global_discount_ids.add(self.global_discount_1)
            with invoice_form.invoice_line_ids.edit(0) as line_form:
                line_form.tax_ids.clear()
                line_form.tax_ids.add(self.tax_0)
        discounts = self.invoice.invoice_global_discount_ids
        self.assertEqual(len(discounts), 1)
        self.assertAlmostEqual(discounts.discount_amount, 40)

    def test_08_line2_with_tax_0(self):
        with Form(self.invoice) as invoice_form:
            invoice_form.global_discount_ids.add(self.global_discount_1)
            with invoice_form.invoice_line_ids.new() as line_form:
                line_form.name = "Line 2"
                line_form.price_unit = 100.0
                line_form.quantity = 1
                line_form.tax_ids.clear()
                line_form.tax_ids.add(self.tax_0)
        self.assertEqual(len(self.invoice.invoice_global_discount_ids), 2)
        discount_tax_15 = self.invoice.invoice_global_discount_ids.filtered(
            lambda x: x.tax_ids == self.tax
        )
        self.assertAlmostEqual(discount_tax_15.discount_amount, 40)
        discount_tax_0 = self.invoice.invoice_global_discount_ids.filtered(
            lambda x: x.tax_ids == self.tax_0
        )
        self.assertAlmostEqual(discount_tax_0.discount_amount, 20)

    def test_09_customer_invoice(self):
        global_discount = self.global_discount_obj.create(
            {
                "name": "Test Discount Sales",
                "discount_scope": "sale",
                "discount": 50,
                "account_id": self.account.id,
                "sequence": 1,
            }
        )
        tax = self.tax_sale_a.copy(default={"amount": 15.0})
        invoice = (
            self.env["account.move"]
            .with_context(test_account_global_discount=True)
            .create(
                {
                    "move_type": "out_invoice",
                    "partner_id": self.partner_1.id,
                    "global_discount_ids": [(6, 0, global_discount.ids)],
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "Line 1",
                                "price_unit": 200.0,
                                "quantity": 1,
                                "tax_ids": [(6, 0, tax.ids)],
                            },
                        )
                    ],
                }
            )
        )
        self.assertEqual(len(invoice.invoice_global_discount_ids), 1)
        invoice_tax_line = invoice.line_ids.filtered("tax_line_id")
        self.assertAlmostEqual(invoice_tax_line.tax_base_amount, 100.0)
        self.assertAlmostEqual(invoice_tax_line.balance, -15.0)
        self.assertAlmostEqual(invoice.amount_untaxed, 100.0)
        self.assertAlmostEqual(invoice.amount_total, 115.0)
        self.assertAlmostEqual(invoice.amount_global_discount, -100.0)
        # Check journal item validity
        lines = invoice.line_ids
        line_15 = lines.filtered(
            lambda x: x.invoice_global_discount_id and x.tax_ids == tax
        )
        self.assertAlmostEqual(line_15.debit, 100)

    def test_10_customer_invoice_currency(self):
        """Multi-currency"""
        eur = self.env.ref("base.EUR")
        usd = self.env.ref("base.USD")
        self.assertEqual(self.env.user.company_id.currency_id, usd)
        with Form(self.invoice) as invoice_form:
            invoice_form.currency_id = eur
        invoice = invoice_form.save()
        self.assertAlmostEqual(invoice.amount_total, 230.0)
        self.assertAlmostEqual(invoice.amount_untaxed, 200.0)
        self.assertAlmostEqual(invoice.amount_global_discount, 0)
        base_line = invoice.line_ids.filtered(
            lambda l: l.tax_ids and not l.invoice_global_discount_id
        )
        self.assertEqual(len(base_line), 1)
        self.assertAlmostEqual(
            base_line.balance,
            eur._convert(
                invoice.amount_untaxed, usd, self.env.user.company_id, invoice.date
            ),
        )
        tax_line = invoice.line_ids.filtered(
            lambda l: l.tax_line_id and not l.invoice_global_discount_id
        )
        self.assertEqual(len(tax_line), 1)
        tax_line_balance_before_discount = tax_line.balance
        self.assertAlmostEqual(
            tax_line_balance_before_discount,
            eur._convert(
                invoice.amount_untaxed * (self.tax.amount / 100),
                usd,
                self.env.user.company_id,
                invoice.date,
            ),
        )
        self.assertAlmostEqual(
            tax_line.tax_base_amount,
            eur._convert(
                invoice.amount_untaxed,
                usd,
                self.env.user.company_id,
                invoice.date,
            ),
        )
        discount_line = invoice.line_ids.filtered("invoice_global_discount_id")
        self.assertFalse(discount_line)
        with Form(self.invoice) as invoice_form:
            invoice_form.global_discount_ids.add(self.global_discount_1)
        invoice = invoice_form.save()
        # Check that when we add a global discount it will be based on the
        # correct currency
        self.assertAlmostEqual(invoice.amount_total, 184)
        self.assertAlmostEqual(invoice.amount_untaxed, 160.0)
        self.assertAlmostEqual(invoice.amount_global_discount, -40.0)
        base_line = invoice.line_ids.filtered(
            lambda l: l.tax_ids and not l.invoice_global_discount_id
        )
        self.assertEqual(len(base_line), 1)
        self.assertAlmostEqual(
            base_line.balance,
            eur._convert(
                invoice.amount_untaxed_before_global_discounts,
                usd,
                self.env.user.company_id,
                invoice.date,
            ),
        )
        tax_line = invoice.line_ids.filtered(
            lambda l: l.tax_line_id and not l.invoice_global_discount_id
        )
        self.assertEqual(len(tax_line), 1)
        self.assertAlmostEqual(
            tax_line.tax_base_amount,
            eur._convert(
                invoice.amount_untaxed,
                usd,
                self.env.user.company_id,
                invoice.date,
            ),
        )
        self.assertAlmostEqual(
            tax_line.balance,
            eur._convert(
                invoice.amount_untaxed * (self.tax.amount / 100),
                usd,
                self.env.user.company_id,
                invoice.date,
            ),
        )
        self.assertLess(tax_line.balance, tax_line_balance_before_discount)
        discount_line = invoice.line_ids.filtered("invoice_global_discount_id")
        self.assertEqual(len(discount_line), 1)
        self.assertAlmostEqual(
            discount_line.balance,
            eur._convert(
                invoice.amount_global_discount,
                usd,
                self.env.user.company_id,
                invoice.date,
            ),
        )
