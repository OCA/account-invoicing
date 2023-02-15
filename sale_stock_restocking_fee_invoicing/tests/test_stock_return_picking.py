# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import Form, TransactionCase


class TestStockReturnPicking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.partner = cls.env["res.partner"].create(
            {"name": "Partner", "charge_restocking_fee": False}
        )

        cls.product_categ = cls.env["product.category"].create(
            {"name": "Test category"}
        )

        cls.product_1 = cls.env["product.product"].create(
            {"name": "test product 1", "list_price": 20, "type": "product"}
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "test product 2", "list_price": 30, "type": "product"}
        )
        cls.so = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product_1.name,
                            "product_id": cls.product_1.id,
                            "product_uom_qty": 5.0,
                            "product_uom": cls.product_1.uom_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.product_2.name,
                            "product_id": cls.product_2.id,
                            "product_uom_qty": 15.0,
                            "product_uom": cls.product_2.uom_id.id,
                        },
                    ),
                ],
            }
        )
        cls.so.action_confirm()

        cls.picking = cls.so.picking_ids
        cls._process_picking(cls.picking)

    @staticmethod
    def _process_picking(picking):
        picking.action_assign()
        for move in picking.move_ids:
            move.quantity_done = move.product_qty
        picking.button_validate()

    def _create_return_wizard(self):
        return_wizard = Form(
            self.env["stock.return.picking"].with_context(
                active_ids=self.picking.ids,
                active_id=self.picking.ids[0],
                active_model="stock.picking",
            )
        )
        res = return_wizard.save()
        return res

    def _create_return_picking(self):
        wizard = self._create_return_wizard()
        res = wizard.create_returns()
        return self.env["stock.picking"].browse(res["res_id"])

    def test_00(self):
        """
        Data:
            A customer not charged with restocking fee
            A delivered SO with 2 lines
        Test case:
            Create a stock return wizard
        Expected result:
            The stock return must:
             * marked as customer return
             * contains 2 lines
             * be configured to not charge the customer with restocking fee
        """
        self.assertFalse(self.partner.charge_restocking_fee)
        wizard = self._create_return_wizard()
        self.assertTrue(wizard.is_customer_return)
        self.assertFalse(wizard.charge_restocking_fee)
        for line in wizard.product_return_moves:
            self.assertFalse(line.charge_restocking_fee)

    def test_01(self):
        """
        Data:
            A customer charged with restocking fee
            A delivered SO with 2 lines
        Test case:
            Create a stock return wizard
        Expected result:
            The stock return must:
             * marked as customer return
             * contains 2 lines
             * be configured to charge the customer with restocking fee
        """
        self.partner.charge_restocking_fee = True
        wizard = self._create_return_wizard()
        self.assertTrue(wizard.is_customer_return)
        self.assertTrue(wizard.charge_restocking_fee)
        for line in wizard.product_return_moves:
            self.assertTrue(line.charge_restocking_fee)

    def test_02(self):
        """
        Data:
            A customer charged with restocking fee
            A delivered SO with 2 lines
        Test case:
            Create the return picking from the wizard
            Process the picking.
        Expected result:
            2 new lines for customer fees must be added to the SO
            (one by product) with qty 1
        """
        self.partner.charge_restocking_fee = True
        self.assertEqual(2, len(self.so.order_line))
        picking = self._create_return_picking()
        self.assertEqual(2, len(self.so.order_line))
        self._process_picking(picking)
        self.assertEqual(4, len(self.so.order_line))
        fees_line = self.so.order_line.filtered("is_restocking_fee")
        self.assertEqual(2, len(fees_line))

    def test_03(self):
        """
        Data:
            A customer not charged with restocking fee
            A delivered SO with 2 lines
        Test case:
            Create the return picking from the wizard
            Process the picking.
        Expected result:
            SO has no new lines
        """
        self.partner.charge_restocking_fee = False
        self.assertEqual(2, len(self.so.order_line))
        picking = self._create_return_picking()
        self.assertEqual(2, len(self.so.order_line))
        self._process_picking(picking)
        self.assertEqual(2, len(self.so.order_line))
        fees_line = self.so.order_line.filtered("is_restocking_fee")
        self.assertEqual(0, len(fees_line))

    def test_04(self):
        """
        Data:
            A customer charged with restocking fee
            A delivered SO with 2 lines
        Test case:
            Create the wizard
            Modify the first line on the wizard to not charge this product
            Create the return picking from the wizard
            Process the picking.
        Expected result:
            SO has 1 new line
        """
        self.partner.charge_restocking_fee = True
        self.assertEqual(2, len(self.so.order_line))
        wizard = self._create_return_wizard()
        wizard.product_return_moves[0].charge_restocking_fee = False
        res = wizard.create_returns()
        picking = self.env["stock.picking"].browse(res["res_id"])
        self.assertEqual(2, len(self.so.order_line))
        self._process_picking(picking)
        self.assertEqual(3, len(self.so.order_line))
        fees_line = self.so.order_line.filtered("is_restocking_fee")
        self.assertEqual(1, len(fees_line))

    def test_05(self):
        """
        Data:
            A customer not charged with restocking fee
            A delivered SO with 2 lines
        Test case:
            Create the wizard
            Modify the first line on the wizard to charge this product
            Create the return picking from the wizard
            Process the picking.
        Expected result:
            SO has 1 new line
        """
        self.partner.charge_restocking_fee = False
        self.assertEqual(2, len(self.so.order_line))
        wizard = self._create_return_wizard()
        wizard.product_return_moves[0].charge_restocking_fee = True
        res = wizard.create_returns()
        picking = self.env["stock.picking"].browse(res["res_id"])
        self.assertEqual(2, len(self.so.order_line))
        self._process_picking(picking)
        self.assertEqual(3, len(self.so.order_line))
        fees_line = self.so.order_line.filtered("is_restocking_fee")
        self.assertEqual(1, len(fees_line))
