# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSplitInvoice(TransactionCase):
    def setUp(self):
        super().setUp()
        self.journal = self.env["account.journal"].create(
            {"name": "Journal", "type": "purchase", "code": "TEST"}
        )
        self.partner = self.env.ref("base.res_partner_10")
        self.product_1 = self.browse_ref("product.product_product_8")
        self.product_2 = self.browse_ref("product.product_product_9")

    def test_split_invoice(self):
        Invoice = self.env["account.invoice"]
        InvoiceLine = self.env["account.invoice.line"]

        invoice = Invoice.create(
            {
                "partner_id": self.partner.id,
                "account_id": self.partner.property_account_payable_id.id,
                "journal_id": self.journal.id,
            }
        )
        product_accounts = (
            self.product_1.product_tmpl_id.get_product_accounts()
        )
        InvoiceLine.create(
            {
                "invoice_id": invoice.id,
                "product_id": self.product_1.id,
                "account_id": product_accounts["expense"].id,
                "name": self.product_1.name,
                "price_unit": 100,
            }
        )
        product_accounts = (
            self.product_2.product_tmpl_id.get_product_accounts()
        )
        InvoiceLine.create(
            {
                "invoice_id": invoice.id,
                "product_id": self.product_2.id,
                "account_id": product_accounts["expense"].id,
                "name": self.product_2.name,
                "price_unit": 150,
                "split": True,
            }
        )

        invoice.btn_split_quotation()
        split_invoice = Invoice.search([("split_id", "=", invoice.id)])

        self.assertEquals(len(invoice.invoice_line_ids), 1)
        self.assertEquals(invoice.invoice_line_ids.product_id, self.product_1)
        self.assertEquals(invoice.invoice_line_ids.price_unit, 100)

        self.assertEquals(len(split_invoice.invoice_line_ids), 1)
        self.assertEquals(
            split_invoice.invoice_line_ids.product_id, self.product_2
        )
        self.assertEquals(split_invoice.invoice_line_ids.price_unit, 150)
