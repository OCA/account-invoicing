#  Copyright 2023 Simone Rubino - TAKOBI
#  License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .common import Common, set_complimentary_account, create_invoice


class TestComplimentary (Common):

    def test_complimentary_line(self):
        """The Taxed Amount of a Complimentary Line
        is not to be paid by the customer."""
        # Arrange
        complimentary_account = self.complimentary_account
        set_complimentary_account(self.env, complimentary_account)

        tax = self.tax_22
        invoice_values = {
            'partner_id': self.customer,
        }
        invoice_lines_values = [
            {
                'name': "Test Invoice Line",
                'price_unit': 100,
            },
            {
                'name': "Test Complimentary Invoice Line",
                'price_unit': 10,
                'is_complimentary': True,
            },
        ]
        invoice = create_invoice(
            self.env,
            invoice_values,
            invoice_lines_values,
            tax,
        )
        # pre-condition: Check the invoice amounts
        # and the configured Complimentary Account
        company = self.env.user.company_id
        self.assertEqual(company.complimentary_account_id, complimentary_account)
        self.assertEqual(invoice.amount_tax, 24.2)
        self.assertEqual(invoice.amount_total, 134.2)

        # Act: Validate the invoice
        invoice.action_invoice_open()

        # Assert
        move = invoice.move_id
        move_lines = move.line_ids
        # The tax owed is still as usual: 100 * 0.22 + 10 * 0.22 = 24.2
        tax_lines = move_lines.filtered(lambda ml: ml.tax_line_id == tax)
        self.assertEqual(sum(tax_lines.mapped('balance')), -24.2)
        # The product lines are as usual: 100 + 10 = 110
        product_lines = move_lines.filtered(lambda ml: tax in ml.tax_ids)
        self.assertEqual(sum(product_lines.mapped('balance')), -110)

        # The customer has to pay only for 100 + 100 * 0.22 = 122
        customer_payment_lines = move_lines.filtered(
            lambda ml: invoice.account_id == ml.account_id)
        self.assertEqual(sum(customer_payment_lines.mapped('balance')), 122)
        self.assertEqual(invoice.residual, 122)
        self.assertEqual(move.amount, 134.2)
        # Because the complimentary line (with tax)
        # is accounted for in the Complimentary Account:
        # 10 + 10 * 0.22 = 12.2
        complimentary_lines = move_lines.filtered(
            lambda ml: ml.account_id == complimentary_account)
        self.assertEqual(sum(complimentary_lines.mapped('balance')), 12.2)
