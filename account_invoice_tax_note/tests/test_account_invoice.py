# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4

from odoo import fields
from odoo.tests.common import TransactionCase


class TestAccountInvoice(TransactionCase):
    """
    Tests for account.invoice
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        tax_group_obj = cls.env["account.tax.group"]
        tax_obj = cls.env["account.tax"]
        invoice_obj = cls.env["account.move"]
        cls.product1 = cls.env["product.product"].create({"name": "Test product 1"})
        cls.product2 = cls.env["product.product"].create({"name": "Test product 2"})
        customer = cls.env["res.partner"].create({"name": "Test customer"})
        cls.tax_group1 = tax_group_obj.create(
            {"name": "Secret Taxes", "sequence": 20, "report_note": str(uuid4())}
        )
        cls.tax_group2 = tax_group_obj.create(
            {"name": "Public taxes", "sequence": 30, "report_note": str(uuid4())}
        )
        cls.tax1 = tax_obj.create(
            {
                "name": "TVA 1",
                "type_tax_use": "sale",
                "amount_type": "percent",
                "amount": "35",
                "description": "Top secret",
                "tax_group_id": cls.tax_group1.id,
            }
        )
        cls.tax2 = tax_obj.create(
            {
                "name": "TVA 2",
                "type_tax_use": "sale",
                "amount_type": "percent",
                "amount": "22",
                "description": "Hello",
                "tax_group_id": cls.tax_group2.id,
            }
        )
        taxes = cls.tax1 | cls.tax2
        cls.product1.write({"taxes_id": [(6, False, cls.tax1.ids)]})
        cls.product2.write({"taxes_id": [(6, False, cls.tax2.ids)]})
        account = cls.env["account.account"].search(
            [("account_type", "=", "income"), ("company_ids", "=", cls.env.company.id)],
            limit=1,
        )
        account.write({"tax_ids": [(4, cls.tax1.id, False), (4, cls.tax2.id, False)]})
        journal = cls.env["account.journal"].create(
            {"name": "Sale journal - Test", "code": "SJ-TT", "type": "sale"}
        )
        invoice_lines1 = [
            (
                0,
                False,
                {
                    "name": cls.product1.display_name,
                    "product_id": cls.product1.id,
                    "quantity": 3,
                    "product_uom_id": cls.product1.uom_id.id,
                    "price_unit": cls.product1.standard_price,
                    "account_id": account.id,
                    "tax_ids": cls.tax1.ids,
                },
            )
        ]
        # Invoice 1 must have 1 tax group only
        cls.invoice1 = invoice_obj.create(
            {
                "partner_id": customer.id,
                "move_type": "out_invoice",
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": invoice_lines1,
                "invoice_origin": "Unit test",
                "journal_id": journal.id,
            }
        )
        invoice_lines2 = [
            (
                0,
                False,
                {
                    "name": cls.product1.display_name,
                    "product_id": cls.product1.id,
                    "quantity": 3,
                    "product_uom_id": cls.product1.uom_id.id,
                    "price_unit": cls.product1.standard_price,
                    "account_id": account.id,
                    "tax_ids": cls.tax1.ids,
                },
            ),
            (
                0,
                False,
                {
                    "name": cls.product1.display_name,
                    "product_id": cls.product2.id,
                    "quantity": 3,
                    "product_uom_id": cls.product2.uom_id.id,
                    "price_unit": cls.product2.standard_price,
                    "account_id": account.id,
                    "tax_ids": taxes.ids,
                },
            ),
        ]
        # Invoice 2 must have more than 1 tax group
        cls.invoice2 = invoice_obj.create(
            {
                "partner_id": customer.id,
                "move_type": "out_invoice",
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": invoice_lines2,
                "invoice_origin": "Unit test",
                "journal_id": journal.id,
            }
        )

    def test_get_account_tax_groups_with_notes1(self):
        """
        Test the function _get_account_tax_groups_with_notes()
        This function should return every account.tax.group used on the
        invoice (by invoice_line_ids.tax_ids)
        For this test, we use an invoice with only 1 tax group
        :return: bool
        """
        tax_group = self.invoice1.mapped("invoice_line_ids.tax_ids.tax_group_id")
        # We need only 1 tax group for this test
        self.assertEqual(len(tax_group), 1)
        tax_group_result = self.invoice1._get_account_tax_groups_with_notes()
        self.assertEqual(set(tax_group.ids), set(tax_group_result.ids))
        return True

    def test_get_account_tax_groups_with_notes2(self):
        """
        Test the function _get_account_tax_groups_with_notes()
        This function should return every account.tax.group used on the
        invoice (by invoice_line_ids.tax_ids)
        For this test, we use an invoice with more than 1 tax group
        :return: bool
        """
        tax_group = self.invoice2.mapped("invoice_line_ids.tax_ids.tax_group_id")
        # We need more than 1 tax group for this test
        self.assertGreater(len(tax_group), 1)
        tax_group_result = self.invoice2._get_account_tax_groups_with_notes()
        self.assertEqual(set(tax_group.ids), set(tax_group_result.ids))
        return True

    def test_get_account_tax_groups_with_notes3(self):
        """
        Test the function _get_account_tax_groups_with_notes()
        This function should return every account.tax.group used on the
        invoice (by invoice_line_ids.tax_ids)
        For this test, we use the function on a multi invoice without any
        taxes. So the result should be empty
        :return: bool
        """
        self.invoice1.invoice_line_ids.write({"tax_ids": [(6, False, [])]})
        tax_group = self.invoice1.mapped("invoice_line_ids.tax_ids.tax_group_id")
        # We need 0 tax group for this test
        self.assertFalse(bool(tax_group))
        tax_group_result = self.invoice1._get_account_tax_groups_with_notes()
        self.assertFalse(bool(tax_group_result))
        return True
