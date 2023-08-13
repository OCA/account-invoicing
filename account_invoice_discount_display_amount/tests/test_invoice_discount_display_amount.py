# Copyright 2022 Manuel Regidor <manuel.regidor@sygel.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestInvoiceDiscountDisplayAmount(TransactionCase):
    def test_invoice_discount_value(self):
        invoice = self.env["account.move"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "move_type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Product A",
                            "price_unit": 100,
                            "quantity": 1,
                            "discount": 10,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Product B",
                            "price_unit": 25,
                            "quantity": 2,
                            "discount": 50,
                        },
                    ),
                ],
            }
        )

        self.assertAlmostEqual(invoice.invoice_line_ids[0].price_total_no_discount, 100)
        self.assertAlmostEqual(invoice.invoice_line_ids[0].discount_total, 10)
        self.assertAlmostEqual(invoice.invoice_line_ids[1].price_total_no_discount, 50)
        self.assertAlmostEqual(invoice.invoice_line_ids[1].discount_total, 25)
        self.assertAlmostEqual(invoice.price_total_no_discount, 150)
        self.assertAlmostEqual(invoice.discount_total, 35)
