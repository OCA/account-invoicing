# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon


class TestAccountMoveSecondaryUnit(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.groups_id = [Command.link(cls.env.ref("uom.group_uom").id)]
        cls.product_uom_kg = cls.env.ref("uom.product_uom_kgm")
        cls.product_uom_gram = cls.env.ref("uom.product_uom_gram")
        cls.product_uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "uom_id": cls.product_uom_kg.id,
                "uom_po_id": cls.product_uom_kg.id,
            }
        )
        cls.secondary_unit = cls.env["product.secondary.unit"].create(
            {
                "name": "unit-700",
                "uom_id": cls.product_uom_unit.id,
                "factor": 0.7,
                "product_tmpl_id": cls.product.product_tmpl_id.id,
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.invoice = cls.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": cls.partner.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": "Test Line",
                            "product_id": cls.product.id,
                            "product_uom_id": cls.product.uom_id.id,
                            "quantity": 1,
                            "price_unit": 100.0,
                        }
                    )
                ],
            }
        )

    def test_account_move_secondary_uom(self):
        invoice = Form(self.invoice)
        with invoice.invoice_line_ids.edit(0) as line:
            # Test _compute_quantity
            line.secondary_uom_id = self.secondary_unit
            line.secondary_uom_qty = 1000.0
            self.assertEqual(line.quantity, 700.0)
            # Test onchange_product_uom_for_secondary
            line.product_uom_id = self.product_uom_gram
            self.assertEqual(line.secondary_uom_qty, 1.0)

    def test_account_move_secondary_uom_price(self):
        invoice = Form(self.invoice)
        with invoice.invoice_line_ids.edit(0) as line:
            line.secondary_uom_id = self.secondary_unit
            line.price_unit = 100.0
            # price_unit = 100, factor = 0.7, secondary_uom_price = 70
            self.assertEqual(line.secondary_uom_price, 70.0)

    def test_account_move_secondary_uom_price_inverse(self):
        invoice = Form(self.invoice)
        with invoice.invoice_line_ids.edit(0) as line:
            line.secondary_uom_id = self.secondary_unit
            line.secondary_uom_price = 140.0
            # secondary_uom_price = 140, factor = 0.7, price_unit = 200
            self.assertAlmostEqual(line.price_unit, 200.0)

    def test_account_move_keeps_price_when_secondary_price_rounds(self):
        secondary_unit = self.env["product.secondary.unit"].create(
            {
                "name": "unit-100",
                "uom_id": self.product_uom_unit.id,
                "factor": 0.1,
                "product_tmpl_id": self.product.product_tmpl_id.id,
            }
        )
        with Form(self.invoice) as invoice:
            with invoice.invoice_line_ids.edit(0) as line:
                line.secondary_uom_id = secondary_unit
                line.price_unit = 1.23
                self.assertAlmostEqual(line.secondary_uom_price, 0.12)
                self.assertAlmostEqual(line.price_unit, 1.23)
        self.assertAlmostEqual(self.invoice.invoice_line_ids.price_unit, 1.23)

    def test_account_move_secondary_uom_price_line_uom(self):
        with Form(self.invoice) as invoice:
            with invoice.invoice_line_ids.edit(0) as line:
                line.secondary_uom_id = self.secondary_unit
                line.product_uom_id = self.product_uom_gram
                line.secondary_uom_qty = 1.0
                self.assertAlmostEqual(line.quantity, 700.0)
                line.price_unit = 0.1
                # 0.1 per g = 100 per kg, factor = 0.7, secondary_uom_price = 70
                self.assertAlmostEqual(line.secondary_uom_price, 70.0)
                line.secondary_uom_price = 140.0
                # 140 per unit = 200 per kg = 0.2 per g
                self.assertAlmostEqual(line.price_unit, 0.2)
        self.assertAlmostEqual(self.invoice.invoice_line_ids.price_subtotal, 140.0)
