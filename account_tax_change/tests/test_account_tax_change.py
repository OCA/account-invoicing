# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.exceptions import UserError

from .common import AccountTaxChangeCommon


class TestAccountTaxChange(AccountTaxChangeCommon):
    at_install = False
    post_install = True
    def test_apply_tax_change(self):
        """Apply a tax change A to B on an invoice using tax A."""
        invoice = self.invoice_tax_a
        old_taxes = invoice.invoice_line_ids.invoice_line_tax_ids
        old_amount_tax = invoice.amount_tax
        self.apply_tax_change(self.tax_change_a2b, invoice)
        new_taxes = invoice.invoice_line_ids.invoice_line_tax_ids
        new_amount_tax = invoice.amount_tax
        self.assertNotEqual(old_taxes, new_taxes)
        self.assertEqual(new_taxes, self.tax_sale_b)
        self.assertNotEqual(old_amount_tax, new_amount_tax)

    def test_apply_tax_change_no_change(self):
        """Apply a tax change A to B on an invoice using already tax B."""
        invoice = self.invoice_tax_b
        old_taxes = invoice.invoice_line_ids.invoice_line_tax_ids
        old_amount_tax = invoice.amount_tax
        self.apply_tax_change(self.tax_change_a2b, invoice)
        new_taxes = invoice.invoice_line_ids.invoice_line_tax_ids
        new_amount_tax = invoice.amount_tax
        self.assertEqual(old_taxes, new_taxes, self.tax_sale_b)
        self.assertEqual(old_amount_tax, new_amount_tax)

    def test_apply_tax_change_invalid_invoice(self):
        """Run the tax change wizard on a non-elligible invoice."""
        invoice = self.invoice_tax_a
        invoice.state = "cancel"
        # Adding the invoice on the wizard
        with self.assertRaises(UserError):
            self.apply_tax_change(self.tax_change_a2b, invoice)
        # Or calling the wizard directly on the selected invoice
        with self.assertRaises(UserError):
            wiz_model = self.env["account.move.apply.tax.change"]
            wiz_model.with_context(
                active_model=invoice._name, active_ids=invoice.ids
            ).default_get(list(invoice._fields))
