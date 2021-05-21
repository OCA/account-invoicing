# © 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

from odoo.tests import common


class TestSelfInvoice(common.TransactionCase):
    def setUp(self):
        res = super(TestSelfInvoice, self).setUp()
        self.partner = self.env["res.partner"].create(
            {"name": "Partner", "supplier_rank": 1}
        )
        self.simple_partner = self.env["res.partner"].create(
            {"name": "Partner", "supplier_rank": 1}
        )
        main_company = self.env.ref("base.main_company")
        main_company.external_report_layout_id = self.env.ref(
            "web.report_layout_standard"
        ).view_id
        self.invoice = self.env["account.move"].create(
            {
                "company_id": main_company.id,
                "partner_id": self.simple_partner.id,
                "type": "in_invoice",
            }
        )
        product = self.browse_ref("product.product_product_5")
        account = self.env["account.account"].create(
            {
                "company_id": main_company.id,
                "name": "Testing Product account",
                "code": "test_product",
                "user_type_id": self.env.ref("account.data_account_type_revenue").id,
            }
        )
        self.env["account.move.line"].create(
            {
                "move_id": self.invoice.id,
                "product_id": product.id,
                "quantity": 1,
                "account_id": account.id,
                "name": "Test product",
                # "price_unit": 20,
            }
        )
        self.invoice._onchange_invoice_line_ids()
        return res

    def test_check_set_self_invoice(self):
        self.assertFalse(self.partner.self_invoice)
        self.partner.set_self_invoice()
        self.assertTrue(self.partner.self_invoice)
        self.assertNotEqual(self.partner.self_invoice_sequence_id, False)
        sequence_id = self.partner.self_invoice_sequence_id.id
        self.partner.set_self_invoice()
        self.assertFalse(self.partner.self_invoice)
        self.partner.set_self_invoice()
        self.assertTrue(self.partner.self_invoice)
        self.assertEqual(sequence_id, self.partner.self_invoice_sequence_id.id)

    def test_none_self_invoice(self):
        self.assertFalse(self.invoice.self_invoice_number)
        self.invoice.action_post()
        self.assertFalse(self.invoice.self_invoice_number)

    def test_self_invoice(self):
        self.partner.set_self_invoice()
        self.assertFalse(self.simple_partner.self_invoice)
        self.assertFalse(self.invoice.can_self_invoice)
        self.invoice.partner_id = self.partner
        self.invoice._onchange_partner_id()
        self.assertTrue(self.invoice.can_self_invoice)
        self.assertTrue(self.invoice.set_self_invoice)
        self.invoice.action_post()
        self.assertTrue(self.invoice.self_invoice_number)

    def test_action_view_account_invoice_self(self):
        self.partner.set_self_invoice()
        self.invoice.partner_id = self.partner
        self.invoice._onchange_partner_id()
        self.invoice.action_post()
        self.assertTrue(self.invoice.self_invoice_number)
        report = self.invoice.action_view_account_invoice_self()
        self.assertTrue(report)
        self.assertEqual(report["type"], "ir.actions.report")
        self.assertEqual(report["name"], "Self Invoice")
        self.assertEqual(len(report["context"]["active_ids"]), 1)
        self.assertEqual(report["context"]["active_ids"][0], self.invoice.id)
