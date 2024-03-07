from odoo.tests.common import SavepointCase


class TestInvoiceSaleOriginLink(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.sale_order_model = cls.env["sale.order"]
        cls.partner = cls.env["res.partner"].create({"name": "John Doe"})
        cls.product = cls.env["product.product"].create({"name": "Product A"})
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "Pricelist for test"}
        )

        cls.so = cls.sale_order_model.create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Line one",
                            "product_id": cls.product.id,
                            "product_uom_qty": 4,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 123,
                        },
                    )
                ],
                "pricelist_id": cls.pricelist.id,
            }
        )

    def test_invoice_sale_origin_link(self):

        self.so.action_confirm()
        self.so.order_line.qty_delivered = 4

        invoice = self.so._create_invoices()
        invoice.post()

        self.assertEqual(invoice.origin_reference, self.so)
