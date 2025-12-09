# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import tagged
from odoo.tools import file_open

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountEdiUblCiiPurchaseMatch(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "test_product", "standard_price": 100}
        )
        cls.partner = cls.env["res.partner"].create(
            {"name": "ALD Automotive LU", "vat": "LU25587702"}
        )
        cls.purchase_order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_qty": 1,
                            "price_unit": 657,
                        }
                    ),
                ],
            }
        )
        cls.po_line = cls.purchase_order.order_line
        cls.purchase_order.button_confirm()

    def _import_invoice(self, journal, file_path=None):
        if file_path is None:
            file_path = (
                "account_edi_ubl_cii_purchase_match/tests/test_files/"
                "bis3_bill_example.xml"
            )
        with file_open(file_path, "rb") as file:
            xml_attachment = self.env["ir.attachment"].create(
                {
                    "mimetype": "application/xml",
                    "name": "test_invoice.xml",
                    "raw": file.read(),
                }
            )
        move = (
            self.env["account.journal"]
            .with_context(default_journal_id=journal.id)
            ._create_document_from_attachment(xml_attachment.id)
        )
        return move

    def test_0(self):
        """
        Default behavior
        without matching criteria, no purchase line or product
        is assigned. Sale journals are also ignored
        """
        bill = self._import_invoice(self.company_data["default_journal_purchase"])
        self.assertEqual(bill.partner_id, self.partner)
        inv_line = bill.invoice_line_ids
        self.assertFalse(inv_line.purchase_line_id)
        self.assertFalse(inv_line.product_id)
        invoice = self._import_invoice(self.company_data["default_journal_sale"])
        self.assertEqual(invoice.partner_id, self.partner)
        inv_line = invoice.invoice_line_ids
        self.assertFalse(inv_line.purchase_line_id)
        self.assertFalse(inv_line.product_id)

    def test_1(self):
        """
        OrderReference matches a purchase order, but no product match is found.
        Standard behavior is disabled: no PO lines are created from the PO, only the
        UBL invoice line is imported
        """
        self.purchase_order.partner_ref = "FAC/2023/00052"
        bill = self._import_invoice(self.company_data["default_journal_purchase"])
        inv_line = bill.invoice_line_ids
        self.assertEqual(len(inv_line), 1)  # standard behavior is desabled
        self.assertFalse(inv_line.purchase_line_id)
        self.assertFalse(inv_line.product_id)

    def test_2(self):
        """
        The product name matches the UBL line description, so the vendor bill line is
        linked to the PO line and the product is set accordingly
        """
        self.purchase_order.partner_ref = "FAC/2023/00052"
        self.product.name = "Locations and leasing"
        bill = self._import_invoice(self.company_data["default_journal_purchase"])
        inv_line = bill.invoice_line_ids
        self.assertEqual(inv_line.purchase_line_id, self.po_line)
        self.assertEqual(inv_line.product_id, self.product)
        return inv_line

    def test_3(self):
        """
        The supplier product name (defined on the product variant via supplierinfo)
        matches the UBL line description, so the bill line is correctly linked to the
        PO line and product
        """

        self.purchase_order.partner_ref = "FAC/2023/00052"
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.partner.id,
                "product_name": "Locations and leasing",
                "product_id": self.product.id,
            }
        )
        bill = self._import_invoice(self.company_data["default_journal_purchase"])
        inv_line = bill.invoice_line_ids
        self.assertEqual(inv_line.purchase_line_id, self.po_line)
        self.assertEqual(inv_line.product_id, self.product)

    def test_4(self):
        """
        The supplier product name (defined on the product template via supplierinfo)
        matches the UBL line description, so the bill line is linked to the PO line and
        product
        """

        self.purchase_order.partner_ref = "FAC/2023/00052"
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.partner.id,
                "product_name": "Locations and leasing",
                "product_tmpl_id": self.product.product_tmpl_id.id,
            }
        )
        bill = self._import_invoice(self.company_data["default_journal_purchase"])
        inv_line = bill.invoice_line_ids
        self.assertEqual(inv_line.purchase_line_id, self.po_line)
        self.assertEqual(inv_line.product_id, self.product)

    def test_5(self):
        """
        When no product match is found, the user manually links the bill line to the PO
        line, the supplier info is updated with the product supplier name
        On the next import, the supplierinfo is used to automatically match the
        bill line with the correct PO line
        """
        self.purchase_order.partner_ref = "FAC/2023/00052"
        bill = self._import_invoice(self.company_data["default_journal_purchase"])
        inv_line = bill.invoice_line_ids
        self.assertFalse(inv_line.purchase_line_id)
        self.assertEqual(inv_line.price_unit, 657.0)
        action = inv_line.action_select_purchase_line()
        wizard = (
            self.env[action.get("res_model")]
            .with_context(**action.get("context"))
            .create({})
        )
        self.assertEqual(wizard.move_line_id, inv_line)
        self.assertEqual(wizard.purchase_order_id, self.purchase_order)
        wizard.product_id = self.product
        wizard.select_purchase_line()
        self.assertEqual(inv_line.purchase_line_id, self.po_line)
        self.assertEqual(self.product.seller_ids.product_name, "Locations and leasing")
        bill.unlink()
        bill = self._import_invoice(self.company_data["default_journal_purchase"])
        inv_line = bill.invoice_line_ids
        self.assertEqual(inv_line.purchase_line_id, self.po_line)

    def test_6(self):
        """
        price unit imported from file is unchanged after po auto match
        """
        inv_line = self.test_2()
        self.assertEqual(inv_line.price_unit, 657.0)
        inv_line.product_id = False
        inv_line.product_id = self.product
        self.assertEqual(inv_line.price_unit, 100)

    def test_7(self):
        """
        price unit imported from file is unchanged after po manual match
        """
        self.purchase_order.partner_ref = "FAC/2023/00052"
        bill = self._import_invoice(self.company_data["default_journal_purchase"])
        inv_line = bill.invoice_line_ids
        self.assertEqual(inv_line.price_unit, 657.0)
        action = inv_line.action_select_purchase_line()
        wizard = (
            self.env[action.get("res_model")]
            .with_context(**action.get("context"))
            .create({})
        )
        wizard.product_id = self.product
        wizard.select_purchase_line()
        self.assertEqual(inv_line.price_unit, 657.0)

    def test_8(self):
        """match product by default_code"""
        self.purchase_order.partner_ref = "FAC/2023/00052"
        self.product.default_code = "leasing001"
        bill = self._import_invoice(self.company_data["default_journal_purchase"])
        inv_line = bill.invoice_line_ids
        self.assertEqual(inv_line.purchase_line_id, self.po_line)
        self.assertEqual(inv_line.product_id, self.product)

    def test_9(self):
        """match product by supplier code"""
        self.purchase_order.partner_ref = "FAC/2023/00052"
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.partner.id,
                "product_code": "leasing001",
                "product_id": self.product.id,
            }
        )
        bill = self._import_invoice(self.company_data["default_journal_purchase"])
        inv_line = bill.invoice_line_ids
        self.assertEqual(inv_line.purchase_line_id, self.po_line)
        self.assertEqual(inv_line.product_id, self.product)

    def test_10(self):
        """match product by supplier code for product template suuplierinfo"""
        self.purchase_order.partner_ref = "FAC/2023/00052"
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.partner.id,
                "product_code": "leasing001",
                "product_tmpl_id": self.product.product_tmpl_id.id,
            }
        )
        bill = self._import_invoice(self.company_data["default_journal_purchase"])
        inv_line = bill.invoice_line_ids
        self.assertFalse(
            inv_line.supplier_product_code, "the value is not stored if match auto"
        )
        self.assertEqual(inv_line.purchase_line_id, self.po_line)
        self.assertEqual(inv_line.product_id, self.product)

    def test_11(self):
        """
        product supplier code is stored in seller information at manual match
        """
        self.purchase_order.partner_ref = "FAC/2023/00052"
        bill = self._import_invoice(self.company_data["default_journal_purchase"])
        inv_line = bill.invoice_line_ids
        self.assertEqual(inv_line.supplier_product_code, "leasing001")
        self.assertEqual(inv_line.price_unit, 657.0)
        action = inv_line.action_select_purchase_line()
        wizard = (
            self.env[action.get("res_model")]
            .with_context(**action.get("context"))
            .create({})
        )
        wizard.product_id = self.product
        wizard.select_purchase_line()
        self.assertEqual(self.product.seller_ids.product_name, "Locations and leasing")
        self.assertEqual(self.product.seller_ids.product_code, "leasing001")

    def test_12(self):
        """test purchase price unit mismatch warning"""
        self.purchase_order.partner_ref = "FAC/2023/00052"
        self.product.default_code = "leasing001"
        bill = self._import_invoice(
            self.company_data["default_journal_purchase"],
            file_path="account_edi_ubl_cii_purchase_match/tests/test_files/"
            "bis3_bill_example_price_unit_mismatch.xml",
        )
        self.assertTrue(bill.purchase_mismatch)
        self.assertIn(
            "Unit price differs from the purchase order line",
            bill.purchase_mismatch_details,
        )
        bill.action_post()
        self.assertFalse(bill.purchase_mismatch)
        self.assertFalse(bill.purchase_mismatch_details)

    def test_13(self):
        """test purchase invoiced qty mismatch warning"""
        self.purchase_order.partner_ref = "FAC/2023/00052"
        self.product.default_code = "leasing001"
        bill = self._import_invoice(
            self.company_data["default_journal_purchase"],
            file_path="account_edi_ubl_cii_purchase_match/tests/test_files/"
            "bis3_bill_example_invoiced_qty_mismatch.xml",
        )
        self.assertTrue(bill.purchase_mismatch)
        self.assertIn(
            "Invoiced quantity exceeds the ordered quantity",
            bill.purchase_mismatch_details,
        )
        bill.action_post()
        self.assertFalse(bill.purchase_mismatch)
        self.assertFalse(bill.purchase_mismatch_details)
