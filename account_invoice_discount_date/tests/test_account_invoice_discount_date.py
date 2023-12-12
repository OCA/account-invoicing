# Copyright 2023 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from datetime import timedelta

from odoo import fields
from odoo.tests.common import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceDiscountDate(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.disc_partner = cls.env["res.partner"].create(
            {
                "name": "Early Discount Partner",
                "is_company": True,
            }
        )

    def test_discount_date_propagation(self):
        """Test discount date is propagated properly to invoice lines"""
        out_invoice = self.init_invoice(
            invoice_date=fields.Date.today(),
            move_type="out_invoice",
            partner=self.disc_partner,
            amounts=[100, 200],
            post=False,
        )

        out_invoice.discount_date = fields.Date.today() + timedelta(days=5)
        for date_due_line in out_invoice.line_ids.filtered("date_maturity"):
            self.assertEqual(date_due_line.discount_date, out_invoice.discount_date)

    def test_discount_date_reverse_propagation(self):
        """Test discount date is propagated properly from invoice lines"""
        in_invoice = self.init_invoice(
            invoice_date=fields.Date.today(),
            move_type="in_invoice",
            partner=self.disc_partner,
            amounts=[100, 200],
            post=False,
        )
        in_invoice.discount_date = fields.Date.today() + timedelta(days=5)
        for date_due_line in in_invoice.line_ids.filtered("date_maturity"):
            self.assertEqual(date_due_line.discount_date, in_invoice.discount_date)

        for date_due_line in in_invoice.line_ids.filtered("date_maturity"):
            date_due_line.discount_date = fields.Date.today() + timedelta(days=4)
        self.assertEqual(
            in_invoice.discount_date, fields.Date.today() + timedelta(days=4)
        )
