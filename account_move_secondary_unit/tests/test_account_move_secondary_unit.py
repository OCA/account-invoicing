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
