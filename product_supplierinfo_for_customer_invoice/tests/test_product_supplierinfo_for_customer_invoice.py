#  Copyright 2021 Alfredo Zamora - Agile Business Group
#  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import Form, SavepointCase


class TestProductSupplierinfoForCustomerInvoice(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProductSupplierinfoForCustomerInvoice, cls).setUpClass()

        cls.product_code = "0101"
        cls.partner_id = cls._create_partner("Partner Test")
        cls.product_id = cls.env.ref("product.product_product_6")
        cls.customerinfo = cls._create_product_customerinfo(
            cls.partner_id, cls.product_id
        )

    @classmethod
    def _create_partner(cls, name):
        """Create a Partner."""
        return cls.env["res.partner"].create(
            {"name": name, "email": "example@yourcompany.com", "phone": 123456}
        )

    @classmethod
    def _create_product_customerinfo(cls, partner, product):
        return cls.env["product.customerinfo"].create(
            {
                "name": partner.id,
                "product_tmpl_id": product.product_tmpl_id.id,
                "product_code": cls.product_code,
            }
        )

    def _create_invoice(self, move_type):
        with Form(
            self.env["account.move"].with_context(default_move_type=move_type)
        ) as invoice_form:
            invoice_form.partner_id = self.partner_id
            with invoice_form.invoice_line_ids.new() as invoice_line_form:
                invoice_line_form.product_id = self.product_id
                invoice_line_form.name = "Invoice Line Test"
        invoice = invoice_form.save()
        invoice_form = Form(invoice)
        return invoice_form.save()

    def test_customer_invoice(self):
        """ check correct product_customer_code on move line for out_invoice """
        invoice_id = self._create_invoice("out_invoice")
        product_customer_code = invoice_id.invoice_line_ids.product_customer_code
        self.assertEqual(self.product_code, product_customer_code)

    def test_vendor_bill(self):
        """ check empty product_customer_code on move line for in_invoice """
        invoice_id = self._create_invoice("in_invoice")
        product_customer_code = invoice_id.invoice_line_ids.product_customer_code
        self.assertEqual("", product_customer_code)
