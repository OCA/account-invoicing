# © 2017 Creu Blanca
# Copyright 2022 - Moduon
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

from odoo.tests import Form, common


class TestSelfInvoice(common.TransactionCase):
    def setUp(self):
        res = super(TestSelfInvoice, self).setUp()
        self.user = self.env.ref("base.user_admin")
        self.partner = self.env["res.partner"].create(
            {"name": "Partner", "supplier_rank": 1}
        )
        self.child_partner = self.env["res.partner"].create(
            {
                "name": "Partner",
                "parent_id": self.partner.id,
            }
        )
        self.simple_partner = self.env["res.partner"].create(
            {"name": "Partner", "supplier_rank": 1}
        )
        main_company = self.env.ref("base.main_company")
        main_company.self_invoice_prefix = "MC"
        main_company.external_report_layout_id = self.env.ref(
            "web.report_layout_standard"
        ).view_id
        self.invoice = self.env["account.move"].create(
            {
                "company_id": main_company.id,
                "partner_id": self.simple_partner.id,
                "move_type": "in_invoice",
                "invoice_date": "2016-03-12",
            }
        )
        self.refund = self.env["account.move"].create(
            {
                "company_id": main_company.id,
                "partner_id": self.simple_partner.id,
                "move_type": "in_refund",
                "invoice_date": "2016-03-12",
            }
        )
        product = self.env["product.product"].create({"name": "Lemonade"})
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
        self.env["account.move.line"].create(
            {
                "move_id": self.refund.id,
                "product_id": product.id,
                "quantity": 1,
                "account_id": account.id,
                "name": "Test product",
                # "price_unit": 20,
            }
        )
        self.invoice._onchange_invoice_line_ids()
        self.refund._onchange_invoice_line_ids()
        return res

    def test_check_set_self_invoice(self):
        self.assertFalse(self.partner.self_invoice)
        self.assertFalse(self.partner.self_invoice_report_footer)
        with Form(self.partner) as f:
            f.self_invoice = True
        self.assertFalse(self.partner.self_invoice_sequence_id)
        self.assertTrue(self.partner.self_invoice_report_footer)
        self.invoice.partner_id = self.partner
        self.invoice._onchange_partner_id()
        self.invoice.action_post()
        self.assertTrue(self.partner.self_invoice_sequence_id)
        self.assertRegex(self.invoice.ref, r"/INV/")
        self.assertFalse(self.partner.self_invoice_refund_sequence_id)

    def test_check_set_self_invoice_refund(self):
        self.assertFalse(self.partner.self_invoice)
        with Form(self.partner) as f:
            f.self_invoice = True
        self.assertFalse(self.partner.self_invoice_sequence_id)
        self.refund.partner_id = self.partner
        self.refund._onchange_partner_id()
        self.refund.action_post()
        self.assertFalse(self.partner.self_invoice_sequence_id)
        self.assertRegex(self.refund.ref, r"/RINV/")
        self.assertTrue(self.partner.self_invoice_refund_sequence_id)

    def test_none_self_invoice(self):
        self.assertFalse(self.invoice.self_invoice_number)
        self.invoice.action_post()
        self.assertFalse(self.invoice.self_invoice_number)

    def test_self_invoice(self):
        with Form(self.partner) as f:
            f.self_invoice = True
        self.assertFalse(self.simple_partner.self_invoice)
        self.assertFalse(self.invoice.can_self_invoice)
        self.invoice.partner_id = self.partner
        self.invoice._onchange_partner_id()
        self.assertTrue(self.invoice.can_self_invoice)
        self.assertTrue(self.invoice.set_self_invoice)
        self.invoice.invoice_date = None
        self.invoice.with_user(self.user.id).action_post()
        self.assertTrue(self.invoice.invoice_date)
        self.assertTrue(self.invoice.self_invoice_number)

    def test_self_invoice_child(self):
        with Form(self.partner) as f:
            f.self_invoice = True
        self.assertFalse(self.simple_partner.self_invoice)
        self.assertFalse(self.invoice.can_self_invoice)
        self.invoice.partner_id = self.child_partner
        self.invoice._onchange_partner_id()
        self.assertTrue(self.invoice.can_self_invoice)
        self.assertTrue(self.invoice.set_self_invoice)
        self.invoice.invoice_date = None
        self.invoice.with_user(self.user.id).action_post()
        self.assertTrue(self.invoice.invoice_date)
        self.assertTrue(self.invoice.self_invoice_number)
