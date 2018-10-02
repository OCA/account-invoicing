# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class IsRefundCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        """Add some defaults to let the test run without an accounts chart."""
        super(IsRefundCase, cls).setUpClass()
        cls.AccountInvoice = cls.env["account.invoice"]
        cls.journal_sale = cls.env["account.journal"].create({
            "name": "Test sale journal",
            "type": "sale",
            "code": "TEST_SJ",
        })
        cls.journal_purchase = cls.env["account.journal"].create({
            "name": "Test purchase journal",
            "type": "purchase",
            "code": "TEST_PJ",
        })
        cls.at_receivable = cls.env["account.account.type"].create({
            "name": "Test receivable account",
            "type": "receivable",
        })
        cls.at_payable = cls.env["account.account.type"].create({
            "name": "Test payable account",
            "type": "payable",
        })
        cls.a_receivable = cls.env["account.account"].create({
            "name": "Test receivable account",
            "code": "TEST_RA",
            "user_type_id": cls.at_receivable.id,
            "reconcile": True,
        })
        cls.a_payable = cls.env["account.account"].create({
            "name": "Test payable account",
            "code": "TEST_PA",
            "user_type_id": cls.at_payable.id,
            "reconcile": True,
        })
        cls.partner = cls.env.ref('base.res_partner_1')
        cls.partner.property_account_receivable_id = cls.a_receivable
        cls.partner.property_account_payable_id = cls.a_payable
        cls.product = cls.env.ref('product.product_product_6')
        cls.product.property_account_income_id = cls.a_receivable
        cls.product.property_account_expense_id = cls.a_payable

    def test_customer_invoice(self):
        """Customer invoice is converted to/from refund fine."""
        invoice = self.AccountInvoice.create({
            "type": "out_invoice",
            "partner_id": self.partner.id,
            "account_id": self.a_receivable.id,
            "invoice_line_ids": [(0, False, {
                "product_id": self.product.id,
                "account_id": self.a_receivable.id,
                "name": self.product.name,
                "quantity": 1,
                "price_unit": 100,
            })],
        })
        self.assertEqual(invoice.is_refund, False)
        self.assertEqual(invoice.amount_untaxed_signed, 100)
        invoice.is_refund = True
        self.assertEqual(invoice.is_refund, True)
        self.assertEqual(invoice.type, "out_refund")
        # HACK https://github.com/odoo/odoo/pull/14187
        invoice._compute_amount()
        self.assertEqual(invoice.amount_untaxed_signed, -100)

    def test_vendor_invoice(self):
        """Vendor invoice is converted to/from refund fine."""
        invoice = self.AccountInvoice.create({
            "type": "in_invoice",
            "partner_id": self.partner.id,
            "account_id": self.a_payable.id,
            "invoice_line_ids": [(0, False, {
                "product_id": self.product.id,
                "account_id": self.a_payable.id,
                "name": self.product.name,
                "quantity": 1,
                "price_unit": 100,
            })],
        })
        self.assertEqual(invoice.is_refund, False)
        self.assertEqual(invoice.amount_untaxed_signed, 100)
        invoice.is_refund = True
        self.assertEqual(invoice.is_refund, True)
        self.assertEqual(invoice.type, "in_refund")
        # HACK https://github.com/odoo/odoo/pull/14187
        invoice._compute_amount()
        self.assertEqual(invoice.amount_untaxed_signed, -100)
