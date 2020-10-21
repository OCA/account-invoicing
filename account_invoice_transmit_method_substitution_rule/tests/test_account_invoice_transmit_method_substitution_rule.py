# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestAccountInvoiceTransmitMethodSubstitutionRule(TransactionCase):
    def setUp(self):
        super(TestAccountInvoiceTransmitMethodSubstitutionRule, self).setUp()
        self.partner = self.env["res.partner"].create(
            {
                "name": "name",
                "street": "street",
                "zip": "01545",
                "city": "city",
                "country_id": self.env.ref("base.us").id,
                "email": "email@email",
            }
        )

    def test_create_invoice_for_partner_without_email(self):
        self.partner.email = False
        invoice = self.env["account.invoice"].create(
            {
                "partner_id": self.partner.id,
                "transmit_method_id": self.env.ref(
                    "account_invoice_transmit_method.mail"
                ).id,
            }
        )
        self.assertEqual(
            invoice.transmit_method_id,
            self.env.ref("account_invoice_transmit_method.post"),
        )

    def test_create_invoice_for_partner_without_address(self):
        self.partner.street = False
        invoice = self.env["account.invoice"].create(
            {
                "partner_id": self.partner.id,
                "transmit_method_id": self.env.ref(
                    "account_invoice_transmit_method.post"
                ).id,
            }
        )
        self.assertEqual(
            invoice.transmit_method_id,
            self.env.ref("account_invoice_transmit_method.mail"),
        )

    def test_create_invoice_for_partner_without_address_email(self):
        """In case of conflict between rules, we keep the transmit method"""
        self.partner.street = False
        self.partner.email = False
        invoice = self.env["account.invoice"].create(
            {
                "partner_id": self.partner.id,
                "transmit_method_id": self.env.ref(
                    "account_invoice_transmit_method.post"
                ).id,
            }
        )
        self.assertEqual(
            invoice.transmit_method_id,
            self.env.ref("account_invoice_transmit_method.post"),
        )

    def test_create_invoice_for_partner_with_address_and_email(self):
        """If any rule is applicable, the transmit method is unchanged"""
        invoice = self.env["account.invoice"].create(
            {
                "partner_id": self.partner.id,
                "transmit_method_id": self.env.ref(
                    "account_invoice_transmit_method.post"
                ).id,
            }
        )
        self.assertEqual(
            invoice.transmit_method_id,
            self.env.ref("account_invoice_transmit_method.post"),
        )
        invoice = self.env["account.invoice"].create(
            {
                "partner_id": self.partner.id,
                "transmit_method_id": self.env.ref(
                    "account_invoice_transmit_method.mail"
                ).id,
            }
        )
        self.assertEqual(
            invoice.transmit_method_id,
            self.env.ref("account_invoice_transmit_method.mail"),
        )

    def test_create_invoice_without_transmit_method(self):
        """If the transmit method is unset, we don't apply any rule"""
        self.partner.street = False
        invoice = self.env["account.invoice"].create(
            {"partner_id": self.partner.id}
        )
        self.assertFalse(invoice.transmit_method_id)

    def test_create_invoice_without_any_rule(self):
        self.env["transmit.method.substitution.rule"].search([]).unlink()
        self.partner.email = False
        invoice = self.env["account.invoice"].create(
            {
                "partner_id": self.partner.id,
                "transmit_method_id": self.env.ref(
                    "account_invoice_transmit_method.mail"
                ).id,
            }
        )
        self.assertEqual(
            invoice.transmit_method_id,
            self.env.ref("account_invoice_transmit_method.mail"),
        )

    def test_create_invoice_with_archived_rule(self):
        self.env.ref(
            "account_invoice_transmit_method_substitution_rule."
            "transmit_method_substitution_rule_demo_1"
        ).active = False
        self.partner.email = False
        invoice = self.env["account.invoice"].create(
            {
                "partner_id": self.partner.id,
                "transmit_method_id": self.env.ref(
                    "account_invoice_transmit_method.mail"
                ).id,
            }
        )
        self.assertEqual(
            invoice.transmit_method_id,
            self.env.ref("account_invoice_transmit_method.mail"),
        )
