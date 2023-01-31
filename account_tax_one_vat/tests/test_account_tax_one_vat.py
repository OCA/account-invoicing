# Copyright 2023 Acsone SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command
from odoo.tests import tagged

from .common import TestAccountTaxOneVatCommon


@tagged("post_install", "-at_install")
class TestAccountTaxOneVat(TestAccountTaxOneVatCommon):
    def test_move_line_without_limitation(self):
        """
        data:
            - 'one vat tax only' setting is unset
        case:
            - create an invoice
              set 2 VAT taxes on an invoice line
        result:
            - No warning upon onchange tax_ids
        """
        # unset the one vat tax only setting
        self.env["res.config.settings"].create({"account_tax_one_vat": False}).execute()
        invoice = self._create_invoice([(100, self.tax_3)])
        move_line = invoice.line_ids[0]
        move_line.tax_ids = [Command.set(self.vat_taxes.ids)]
        action = move_line._onchange_only_one_vat_tax()
        self.assertEqual(action, {})
        self.assertEqual(move_line.tax_ids, self.vat_taxes)

    def test_move_line_with_limitation_warning(self):
        """
        data:
            - 'one vat tax only' setting is set
        case:
            - create an invoice
            - set 2 VAT taxes on an invoice line
        result:
            - Get a warning upon onchange tax_ids
        """
        self.env["res.config.settings"].create({"account_tax_one_vat": True}).execute()
        invoice = self._create_invoice([(100, self.tax_3)])
        move_line = invoice.line_ids[0]
        move_line.tax_ids = [Command.set(self.vat_taxes.ids)]
        action = move_line._onchange_only_one_vat_tax()
        self.assertTrue("warning" in action)
        self.assertDictEqual(
            action,
            {
                "warning": {
                    "title": "More than one VAT tax selected!",
                    "message": "You selected more than one tax of type VAT.",
                }
            },
        )
        self.assertEqual(move_line.tax_ids, self.vat_taxes)

    def test_move_line_with_limitation_no_warning(self):
        """
        data:
            - 'one vat tax only' setting is set
        case:
            - create an invoice
            - set 2 taxes (only 1 is VAT) on an invoice line
        result:
            - No warning upon onchange tax_ids
        """
        self.env["res.config.settings"].create({"account_tax_one_vat": True}).execute()
        invoice = self._create_invoice([(100, self.tax_3)])
        move_line = invoice.line_ids[0]
        move_line.tax_ids = [Command.set(self.mixed_taxes.ids)]
        action = move_line._onchange_only_one_vat_tax()
        self.assertEqual(action, {})
        self.assertEqual(move_line.tax_ids, self.mixed_taxes)

    def test_invoice_post_with_limitation(self):
        """
        data:
            - 'one vat tax only' setting is set
            - one draft invoice
        case:
            - set 2 VAT taxes on an invoice line and confirm the invoice
        result:
            - Get a UserError and the invoice is still draft
        """
        self.env["res.config.settings"].create({"account_tax_one_vat": True}).execute()
        invoice = self._create_invoice([(100, self.tax_3)])
        move_line = invoice.line_ids[0]
        move_line.tax_ids = [Command.set(self.vat_taxes.ids)]
        self.assertEqual(invoice.state, "draft")
        with self.assertRaises(UserError):
            invoice.action_post()
        self.assertEqual(invoice.state, "draft")

    def test_product_without_limitation(self):
        """
        data:
            - 'one vat tax only' setting is unset
            - a product
        case:
            - create an invoice
            - set 2 VAT taxes on the product
        result:
            - vat field is not set
        """
        # unset the one vat tax only setting
        self.env["res.config.settings"].create({"account_tax_one_vat": False}).execute()
        self.product_test.taxes_id = [Command.set(self.vat_taxes.ids)]
        self.assertEqual(self.product_test.taxes_id, self.vat_taxes)
        self.product_test.supplier_taxes_id = [Command.set(self.vat_taxes.ids)]
        self.assertEqual(self.product_test.supplier_taxes_id, self.vat_taxes)
        # vat is not set
        self.assertFalse(self.product_test.vat_id)
        self.assertFalse(self.product_test.vat)

    def test_product_with_limitation_constraint(self):
        """
        data:
            - 'one vat tax only' setting is set
            - a product
        case:
            - set 2 VAT taxes on the product
        result:
            - get a ValidationError
            - vat field is not set
        """
        # set the one vat tax only setting
        self.env["res.config.settings"].create({"account_tax_one_vat": True}).execute()
        msg = "Multiple customer tax of type VAT are selected. Only one is allowed."
        with self.assertRaises(ValidationError, msg=msg):
            self.product_test.taxes_id = [Command.set(self.vat_taxes.ids)]
        with self.assertRaises(ValidationError, msg=msg):
            self.product_test.supplier_taxes_id = [Command.set(self.vat_taxes.ids)]
        # vat is not set
        self.assertFalse(self.product_test.vat_id)
        self.assertFalse(self.product_test.vat)

    def test_product_with_limitation_no_constraint(self):
        """
        data:
            - 'one vat tax only' setting is set
            - a product
        case:
            - set 2 taxes (only 1 VAT) on the product
        result:
            - vat field is set to the VAT tax
        """
        # set the one vat tax only setting
        self.env["res.config.settings"].create({"account_tax_one_vat": True}).execute()
        self.product_test.taxes_id = [Command.link(t.id) for t in self.mixed_taxes]
        self.product_test.supplier_taxes_id = [
            Command.link(t.id) for t in self.mixed_taxes
        ]
        # vat is set
        self.assertEqual(self.product_test.vat_id, self.vat_tax_1)
        self.assertEqual(self.product_test.vat, self.vat_tax_1.name)
