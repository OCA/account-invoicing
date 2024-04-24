#  Copyright 2022 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.fields import first
from odoo.tests import Form

from .common import DefaultAccountCommon


class TestDefaultAccountSupplier(DefaultAccountCommon):

    _default_move_type = "in_invoice"

    def test_default_account_product(self):
        """
        If the invoice line has a product, account is not changed
        """
        # Arrange: Set a different account in the partner
        self.partner.property_account_expense = self.partner_account
        self.assertNotEqual(self.default_account, self.partner_account)

        # Act: Create an invoice
        invoice = self._create_invoice(
            self.env.user,
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
        self.partner.property_account_expense = self.partner_account
        self.assertNotEqual(self.default_account, self.partner_account)

        # Act: Create an invoice without product
        invoice = self._create_invoice(
            self.env.user,
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
        self.partner.property_account_expense = self.partner_account
        self.assertNotEqual(self.default_account, self.partner_account)
        other_account = self.other_income_account
        # pre-condition: Partner is set to save income account
        self.assertTrue(self.partner.auto_update_account_expense)

        # Act: Edit the account in the line
        invoice_form = Form(self.invoice)
        with invoice_form.invoice_line_ids.edit(0) as line:
            line.account_id = other_account
        invoice_form.save()

        # Assert: Account in the line has been set in the partner
        self.assertEqual(
            self.partner.property_account_expense,
            other_account,
        )

    def test_default_account_no_autosave(self):
        """
        Check if the account is not updated if partner account auto save
        is disabled.
        """
        # Arrange: Set a different account in the partner
        self.partner.auto_update_account_expense = False
        self.partner.property_account_expense = self.partner_account
        self.assertNotEqual(self.default_account, self.partner_account)
        other_account = self.other_income_account

        # Act: Edit the account in the line
        invoice_form = Form(self.invoice)
        with invoice_form.invoice_line_ids.edit(0) as line:
            line.account_id = other_account
        invoice_form.save()

        # Assert: Account in the line has been set in the partner
        self.assertEqual(
            self.partner.property_account_expense,
            self.partner_account,
        )
