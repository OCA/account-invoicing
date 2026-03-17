# Copyright 2026 ACSONE SA/NV
# Copyright 2026 BCIM
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestAccountMoveLinePackaging(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "consu", "uom_id": cls.uom_unit.id}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Test Product", "type": "consu", "uom_id": cls.uom_unit.id}
        )
        cls.packaging = cls.env["product.packaging"].create(
            {"name": "pallet 72", "product_id": cls.product.id, "qty": 72.0}
        )
        cls.packaging_2 = cls.env["product.packaging"].create(
            {"name": "pallet 72", "product_id": cls.product_2.id, "qty": 72.0}
        )

    def _create_invoice(self, move_type="in_invoice"):
        return self.env["account.move"].create(
            {
                "move_type": move_type,
                "partner_id": self.partner.id,
                "invoice_line_ids": [
                    Command.create(
                        {
                            "name": self.product.display_name,
                            "product_id": self.product.id,
                            "product_uom_id": self.uom_unit.id,
                            "price_unit": 10.0,
                        },
                    )
                ],
            }
        )

    def test_packaging_recomputes_quantity(self):
        bill = self._create_invoice()
        line = bill.invoice_line_ids
        line.write(
            {"product_packaging_id": self.packaging.id, "product_packaging_qty": 1.0}
        )
        self.assertEqual(line.quantity, 72.0)
        # check no inverse compute from quantity
        line.quantity = 100
        self.assertEqual(line.product_packaging_id, self.packaging)
        self.assertEqual(line.product_packaging_qty, 1)

    def test_packaging_reset_if_product_changes(self):
        bill = self._create_invoice()
        line = bill.invoice_line_ids
        line.write(
            {"product_packaging_id": self.packaging.id, "product_packaging_qty": 1.0}
        )
        line.write({"product_id": self.product_2.id})
        self.assertFalse(line.product_packaging_id)
        self.assertFalse(line.product_packaging_qty)
        self.assertEqual(line.quantity, 72.0)

    def test_check_product_packaging(self):
        bill = self._create_invoice()
        line = bill.invoice_line_ids
        with self.assertRaisesRegex(
            ValidationError,
            "The selected packaging does not belong to the selected product",
        ):
            line.write(
                {
                    "product_packaging_id": self.packaging_2.id,
                    "product_packaging_qty": 1.0,
                }
            )
