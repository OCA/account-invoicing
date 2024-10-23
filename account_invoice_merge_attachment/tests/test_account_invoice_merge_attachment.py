# Copyright 2016-2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountInvoiceMergeAttachment(AccountTestInvoicingCommon):
    def create_invoice_attachment(self, invoice):
        return self.env["ir.attachment"].create(
            {
                "name": "Attach",
                "raw": b"bWlncmF0aW9uIHRlc3Q=",
                "res_model": invoice._name,
                "res_id": invoice.id,
            }
        )

    def test_merge_invoice_attachments(self):
        today = fields.Date.today()
        invoice1 = self.init_invoice(
            "out_invoice",
            partner=self.partner_a,
            invoice_date=today,
            products=self.product_a,
        )
        self.create_invoice_attachment(invoice1)

        invoice2 = self.init_invoice(
            "out_invoice",
            partner=self.partner_a,
            invoice_date=today,
            products=self.product_a,
        )
        self.create_invoice_attachment(invoice2)
        self.create_invoice_attachment(invoice2)

        invoices = invoice1 + invoice2
        invoices_info = invoices.with_context(link_attachment=True).do_merge()
        self.assertTrue(len(list(invoices_info.keys())) == 1)
        attach = self.env["ir.attachment"].search(
            [
                ("res_id", "in", list(invoices_info.keys())),
                ("res_model", "=", invoices._name),
            ]
        )
        self.assertEqual(
            len(attach), 3, msg="Merged invoiced should have 3 attachments"
        )
