# Copyright 2020 Jarsa
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

from odoo.tests import SavepointCase, tagged


@tagged("post_install", "-at_install")
class TestAccountMoveSecondaryUnit(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_uom_gram = cls.env.ref("uom.product_uom_gram")
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.account = cls.env["account.account"].search(
            [
                (
                    "user_type_id",
                    "=",
                    cls.env.ref("account.data_account_type_revenue").id,
                )
            ],
            limit=1,
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "test",
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
                "secondary_uom_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "unit-700",
                            "uom_id": cls.product_uom_unit.id,
                            "factor": 0.7,
                        },
                    )
                ],
            }
        )
        cls.secondary_unit = cls.env["product.secondary.unit"].search(
            [("product_tmpl_id", "=", cls.product.product_tmpl_id.id)]
        )
        cls.partner = cls.env["res.partner"].create({"name": "test - partner"})

    def create_invoice(self, values):
        return self.env["account.move"].create(
            {
                "partner_id": self.partner.id,
                "journal_id": self.env["account.journal"]
                .search([("type", "=", "sale")], limit=1)
                .id,
                "type": "out_invoice",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "quantity": values.get("quantity", 1.0),
                            "account_id": self.account.id,
                            "name": self.product.name,
                            "price_unit": 1000.00,
                            "product_uom_id": values.get(
                                "product_uom_id", self.product.uom_id.id
                            ),
                            "secondary_uom_id": values.get("secondary_uom_id", False),
                            "secondary_uom_qty": values.get("secondary_uom_qty", 0),
                        },
                    )
                ],
            }
        )

    def test_onchange_secondary_uom(self):
        invoice = self.create_invoice(
            {"secondary_uom_id": self.secondary_unit.id, "secondary_uom_qty": 5}
        )
        invoice.invoice_line_ids.with_context(
            check_move_validity=False
        ).onchange_secondary_uom()
        self.assertEqual(invoice.invoice_line_ids.quantity, 3.5)

    def test_onchange_secondary_unit_product_uom_qty(self):
        invoice = self.create_invoice(
            {"secondary_uom_id": self.secondary_unit.id, "quantity": 3.5}
        )
        invoice.invoice_line_ids.with_context(
            check_move_validity=False
        ).onchange_secondary_unit_quantity()
        self.assertEqual(invoice.invoice_line_ids.secondary_uom_qty, 5.0)

    def test_onchange_invoice_product_uom_id(self):
        invoice = self.create_invoice(
            {
                "secondary_uom_id": self.secondary_unit.id,
                "product_uom_id": self.product_uom_gram.id,
                "quantity": 3500.00,
            }
        )
        invoice.invoice_line_ids.with_context(
            check_move_validity=False
        ).onchange_product_uom_id_for_secondary()
        self.assertEqual(invoice.invoice_line_ids.secondary_uom_qty, 5.0)
