# Copyright 2025 Studio73 - Eugenio Micó <eugenio@studio73.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.base.tests.common import BaseCommon


class TestStockRule(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.picking_type = cls.env.ref("stock.picking_type_out")
        cls.location_src = cls.env.ref("stock.stock_location_stock")
        cls.location_dest = cls.env.ref("stock.stock_location_customers")
        cls.route = cls.env.ref("stock.route_warehouse0_mto")
        cls.rule = cls.env["stock.rule"].create(
            {
                "name": "Test Rule",
                "action": "pull",
                "picking_type_id": cls.picking_type.id,
                "location_src_id": cls.location_src.id,
                "location_dest_id": cls.location_dest.id,
                "route_id": cls.route.id,
            }
        )

    def test_get_custom_move_fields(self):
        fields = self.rule._get_custom_move_fields()
        self.assertIn("invoice_state", fields)
