import logging

from odoo import fields
from odoo.tests.common import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

_logger = logging.getLogger(__name__)


@tagged("post_install", "-at_install")
class TestinvoiceDate(AccountTestInvoicingCommon):
    def setUp(self):
        super(TestinvoiceDate, self).setUp()
        self.partner_test = (
            self.env["res.partner"]
            .sudo()
            .create({"name": "Test User", "email": "test@test.com"})
        )

    def create_invoice(self, invoice_date):
        return self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_test.id,
                "invoice_date": invoice_date,
                "currency_id": self.currency_data["currency"].id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test line",
                            "price_unit": 5,
                            "quantity": 1,
                            "account_id": self.company_data[
                                "default_account_revenue"
                            ].id,
                        },
                    )
                ],
            }
        )

    def test_invoice_has_date(self):
        """This method has an invoice that has a date
        and it will not trigger the confirm date wizard"""
        date = fields.Date.from_string("2023-02-05")
        invoice = self.create_invoice(date)
        inv_date = invoice.invoice_date
        invoice.open_invoice_date_wizard()
        # Compare invoice_date is same as before action_post()
        self.assertEqual(invoice.invoice_date, inv_date)
        self.assertTrue(invoice.state == "posted")

    def test_invoice_has_not_date(self):
        """This method triggers the wizard to fill
        in the date of the invoice"""
        date = False
        invoice = self.create_invoice(date)
        date_wizard = invoice.open_invoice_date_wizard()
        if date_wizard:
            ctx = {
                "active_model": invoice._name,
                "active_ids": invoice.ids,
                "active_id": invoice.ids,
            }
            wizard = (
                self.env["account.voucher.proforma.date"]
                .with_context(**ctx)
                .create({"date": fields.Date.from_string("2023-02-10")})
            )
            wizard.with_context(**ctx).action_post()
        # Checks that wizard date is written in invoice
        self.assertTrue(invoice.invoice_date == fields.Date.from_string("2023-02-10"))
