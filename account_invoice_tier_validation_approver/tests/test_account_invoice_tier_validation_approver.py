# Copyright 2021 ForgeFlow (http://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo.tests.common import TransactionCase


class TestAccountInvoiceTierValidationApprover(TransactionCase):
    def setUp(self):
        super(TestAccountInvoiceTierValidationApprover, self).setUp()
        self.res_partner_1 = self.env["res.partner"].create(
            {"name": "Wood Corner", "email": "example@yourcompany.com"}
        )
        self.product_1 = self.env["product.product"].create(
            {"name": "Desk Combination"}
        )
        self.currency_euro = self.env["res.currency"].search([("name", "=", "EUR")])
        self.test_user_1 = self.env["res.users"].create(
            {"name": "User", "login": "test1", "email": "example@yourcompany.com"}
        )
        self.test_approver = self.env["res.users"].create(
            {"name": "Approver", "login": "test2", "email": "example@yourcompany.com"}
        )
        self.account_type_receivable = self.env["account.account.type"].create(
            {"name": "Test Receivable", "type": "receivable"}
        )
        self.account_type_regular = self.env["account.account.type"].create(
            {"name": "Test Regular", "type": "other"}
        )
        self.account_receivable = self.env["account.account"].create(
            {
                "name": "Test Receivable",
                "code": "TEST_AR",
                "user_type_id": self.account_type_receivable.id,
                "reconcile": True,
            }
        )
        self.invoice_line = self.env["account.invoice.line"].create(
            {
                "name": "Line",
                "price_unit": 1000.0,
                "account_id": self.account_receivable.id,
                "quantity": 1,
            }
        )
        self.vendor_bill = self.env["account.invoice"].create(
            {
                "name": "Test vendor Bill",
                "type": "in_invoice",
                "partner_id": self.res_partner_1.id,
                "currency_id": self.currency_euro.id,
                "approver_id": self.test_approver.id,
                "invoice_line_ids": [(4, self.invoice_line.id)],
            }
        )
        self.model_id = self.env["ir.model"].search(
            [("name", "=", "Invoice")], limit=1
        )
        self.field_id = self.env["ir.model.fields"].search(
            [("name", "=", "approver_id")], limit=1
        )

    def test_field_validation_approver(self):
        tiers = self.env["tier.definition"].search([])
        for tier in tiers:
            tier.write({"active": False})
        self.tier_definition = self.env["tier.definition"].create(
            {
                "name": "Test Tier",
                "model_id": self.model_id.id,
                "review_type": "field",
                "reviewer_field_id": self.field_id.id,
                "definition_type": "domain",
                "definition_domain": "[('type', '=', 'in_invoice')]",
            }
        )
        record = self.vendor_bill
        record.sudo(self.test_user_1.id).write({"approver_id": self.test_approver.id})
        record.sudo(self.test_user_1.id).request_validation()
        record.invalidate_cache()
        record.sudo(self.test_approver.id).validate_tier()
        record.sudo(self.test_user_1.id).action_invoice_open()
