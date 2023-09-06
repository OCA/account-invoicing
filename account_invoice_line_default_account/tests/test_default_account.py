#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.fields import first
from odoo.tests import Form, tagged

from odoo.addons.account.tests.account_test_users import AccountTestUsers


@tagged("post_install", "-at_install")
class TestDefaultAccount(AccountTestUsers):
    def _create_invoice(self, user, partner, product=None):
        account_invoice_model = self.account_invoice_model
        if user:
            account_invoice_model = account_invoice_model.sudo(user.id)

        invoice_form = Form(account_invoice_model)
        invoice_form.partner_id = partner
        with invoice_form.invoice_line_ids.new() as line:
            if product:
                line.product_id = product
            else:
                # Required for invoice lines
                line.name = "Test line"

        return invoice_form.save()

    def setUp(self):
        super().setUp()
        self.partner = self.env.ref("base.res_partner_3")
        self.account_invoice_model = self.env["account.invoice"].sudo(
            self.account_user.id
        )
        self.product = self.env.ref("product.product_product_5")

        self.invoice = self._create_invoice(
            self.account_user,
            self.partner,
        )
        invoice_line = first(self.invoice.invoice_line_ids)
        self.default_account = invoice_line.account_id
        self.partner_account = self.default_account.search(
            [
                ("id", "!=", self.default_account.id),
            ],
            limit=1,
        )

    def test_default_account_product(self):
        """
        If the invoice line has a product, account is not changed
        """
        # Arrange: Set a different account in the partner
        self.partner.property_account_income = self.partner_account
        self.assertNotEqual(self.default_account, self.partner_account)

        # Act: Create an invoice
        invoice = self._create_invoice(
            self.account_user,
            self.partner,
            self.product,
        )
        invoice_line = first(invoice.invoice_line_ids)

        # Assert: Account in the line is not changed
        self.assertEqual(invoice_line.account_id, self.default_account)

    def test_default_account_no_product(self):
        """
        If the invoice line has no product, account is changed
        """
        # Arrange: Set a different account in the partner
        self.partner.property_account_income = self.partner_account
        self.assertNotEqual(self.default_account, self.partner_account)

        # Act: Create an invoice without product
        invoice = self._create_invoice(
            self.account_user,
            self.partner,
        )
        invoice_line = first(invoice.invoice_line_ids)

        # Assert: Account in the line is what was set in the partner
        self.assertEqual(invoice_line.account_id, self.partner_account)

    def test_default_account_autosave(self):
        """
        If the partner is configured to save the updated account, it is saved.
        """
        # Arrange: Set a different account in the partner
        self.partner.property_account_income = self.partner_account
        self.assertNotEqual(self.default_account, self.partner_account)
        used_accounts = self.default_account | self.partner_account
        other_account = self.default_account.search(
            [
                ("id", "not in", used_accounts.ids),
            ],
            limit=1,
        )

        # pre-condition: Partner is set to save income account
        self.assertTrue(self.partner.auto_update_account_income)

        # Act: Edit the account in the line
        invoice_form = Form(self.invoice)
        with invoice_form.invoice_line_ids.edit(0) as line:
            line.account_id = other_account
        invoice_form.save()

        # Assert: Account in the line has been set in the partner
        self.assertEqual(
            self.partner.property_account_income,
            other_account,
        )
