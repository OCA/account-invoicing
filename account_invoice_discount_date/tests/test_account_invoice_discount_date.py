# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from datetime import timedelta

from odoo import fields
from odoo.tests.common import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceDiscountDate(AccountTestInvoicingCommon):
    def test_discount_date_propagation(self):
        """Test discount date is propagated properly to invoice lines"""
        normal_discount_date = fields.Date.today() + timedelta(days=5)
        early_discount_date = fields.Date.today() + timedelta(days=3)
        for move_type in {"out_invoice", "in_invoice"}:
            with self.subTest(move_type=move_type):
                invoice = self._create_invoice(move_type=move_type)
                # Check inverse
                invoice.discount_date = normal_discount_date
                for date_due_line in invoice.line_ids.filtered("date_maturity"):
                    self.assertEqual(date_due_line.discount_date, invoice.discount_date)
                    self.assertEqual(invoice.discount_date, normal_discount_date)
                # Check computed
                early_discount_date = fields.Date.today() + timedelta(days=3)
                fields.first(
                    invoice.line_ids.filtered("date_maturity")
                ).discount_date = early_discount_date
                self.assertEqual(invoice.discount_date, early_discount_date)
