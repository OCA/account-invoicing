# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestAccountCustomAccountByInvoiceAddress(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        acc_model = cls.env["account.account"]
        partner_model = cls.env["res.partner"]
        cls.custom_receivable = acc_model.create(
            {
                "name": "Custom Receivable",
                "code": "RCVTEST",
                "account_type": "asset_receivable",
                "reconcile": True,
            }
        )
        cls.custom_payable = acc_model.create(
            {
                "name": "Custom Payable",
                "code": "PYTEST",
                "account_type": "liability_payable",
                "reconcile": True,
            }
        )
        cls.customer = partner_model.create({"name": "Main Customer"})
        cls.invoice_address = partner_model.create(
            {
                "name": "Customer Branch A",
                "parent_id": cls.customer.id,
                "type": "invoice",
            }
        )
        cls.vendor = partner_model.create({"name": "Main Vendor"})
        cls.vendor_invoice_address = partner_model.create(
            {
                "name": "Vendor Branch A",
                "parent_id": cls.vendor.id,
                "type": "invoice",
            }
        )
        cls.product = cls.env["product.product"].create({"name": "Test Product"})

    def _create_invoice(self, move_type, partner):
        return self.env["account.move"].create(
            {
                "move_type": move_type,
                "partner_id": partner.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "quantity": 1,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )

    def test_standard_receivable_used_without_flag(self):
        """custom receivable shouldn't be used without flag set on parent"""
        self.invoice_address.property_account_receivable_id = self.custom_receivable
        invoice = self._create_invoice("out_invoice", self.invoice_address)
        receivable_line = invoice.line_ids.filtered(
            lambda r: r.account_id.account_type == "asset_receivable"
        )
        self.assertNotEqual(receivable_line.account_id, self.custom_receivable)

    def test_custom_receivable_used_with_flag(self):
        """custom receivable should be used with flag set on parent"""
        self.customer.use_invoice_address_accounts = True
        self.invoice_address.property_account_receivable_id = self.custom_receivable
        invoice = self._create_invoice("out_invoice", self.invoice_address)
        receivable_line = invoice.line_ids.filtered(
            lambda r: r.account_id.account_type == "asset_receivable"
        )
        self.assertEqual(receivable_line.account_id, self.custom_receivable)

    def test_standard_payable_used_without_flag(self):
        self.vendor_invoice_address.property_account_payable_id = self.custom_payable
        bill = self._create_invoice("in_invoice", self.vendor_invoice_address)
        payable_line = bill.line_ids.filtered(
            lambda r: r.account_id.account_type == "liability_payable"
        )
        self.assertNotEqual(payable_line.account_id, self.custom_payable)

    def test_custom_payable_used_with_flag(self):
        self.vendor.use_invoice_address_accounts = True
        self.vendor_invoice_address.property_account_payable_id = self.custom_payable
        bill = self._create_invoice("in_invoice", self.vendor_invoice_address)
        payable_line = bill.line_ids.filtered(
            lambda r: r.account_id.account_type == "liability_payable"
        )
        self.assertEqual(payable_line.account_id, self.custom_payable)
