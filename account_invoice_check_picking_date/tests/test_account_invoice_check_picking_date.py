# Copyright 2025 Moduon Team
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from datetime import datetime
from unittest.mock import patch

from freezegun import freeze_time

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon

PATH_ACCOUNT_MOVE = (
    "odoo.addons.account_invoice_check_picking_date.models.account_move.AccountMove"
)


@freeze_time("2025-01-01")
class TestAccountInvoiceCheckPickingDate(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test product", "type": "consu"}
        )
        cls.picking = cls.env["stock.picking"].create(
            {
                "partner_id": cls.partner.id,
                "picking_type_id": cls.env.ref("stock.picking_type_in").id,
                "location_id": cls.env.ref("stock.stock_location_suppliers").id,
                "location_dest_id": cls.env.ref("stock.stock_location_stock").id,
                "move_ids": [
                    Command.create(
                        {
                            "name": "Test move",
                            "product_id": cls.product.id,
                            "product_uom_qty": 1,
                            "product_uom": cls.product.uom_id.id,
                            "location_id": cls.env.ref(
                                "stock.stock_location_suppliers"
                            ).id,
                            "location_dest_id": cls.env.ref(
                                "stock.stock_location_stock"
                            ).id,
                        },
                    )
                ],
            }
        )
        cls.invoice = cls.env["account.move"].create(
            {
                "partner_id": cls.partner.id,
                "move_type": "in_invoice",
                "date": "2025-02-01",
                "invoice_date": "2025-02-01",
                "invoice_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "quantity": 1,
                            "price_unit": 100,
                        }
                    )
                ],
            }
        )

    def _enable_picking_date_check(self, moves):
        self.patch(
            self.registry["account.move"],
            "_stock_account_get_last_step_stock_moves",
            lambda *args, **kwargs: moves,
        )
        self.patch(
            self.registry["account.move"],
            "_is_test_enabled",
            lambda *args, **kwargs: False,
        )

    def test_account_invoice_check_picking_date(self):
        # Patch methods to deactivate test mode temporarily and return my moves
        self.patch(
            self.registry["account.move"],
            "_stock_account_get_last_step_stock_moves",
            lambda *args, **kwargs: self.picking.move_ids,
        )
        self.patch(
            self.registry["account.move"],
            "_is_test_enabled",
            lambda *args, **kwargs: False,
        )
        # Picking
        self.picking.action_confirm()
        self.picking.action_assign()
        self.picking.button_validate()
        # Invoice
        wizard_action = self.invoice.action_post()
        self.assertEqual(wizard_action["res_model"], "invoice.picking.date.check.wiz")
        self.assertEqual(self.invoice.state, "draft")
        wiz = self.env["invoice.picking.date.check.wiz"].browse(wizard_action["res_id"])
        wiz.button_continue()
        self.assertEqual(self.invoice.state, "posted")

    def test_moves_invalid_dates(self):
        path_stock_move_dates = PATH_ACCOUNT_MOVE + "._get_min_max_stock_move_dates"
        path_match_stock_move_dates = (
            PATH_ACCOUNT_MOVE + "._match_invoice_and_stock_move_dates"
        )
        min_date = "2025-10-01"
        max_date = "2025-11-01"
        with patch(path_stock_move_dates) as stock_move_dates:
            stock_move_dates.return_value = False, False
            min_d, max_d = self.invoice._get_min_max_stock_move_dates()
            self.assertFalse(min_d)
            self.assertFalse(max_d)

        with patch(path_stock_move_dates) as stock_move_dates:
            stock_move_dates.return_value = min_date, max_date
            min_d, max_d = self.invoice._get_min_max_stock_move_dates()
            self.assertEqual(min_d, min_date)
            self.assertEqual(max_d, max_date)

        with patch(path_stock_move_dates) as stock_move_dates, patch(
            path_match_stock_move_dates
        ) as match_stock_move_dates:
            stock_move_dates.return_value = min_date, False
            min_d, max_d = self.invoice._get_min_max_stock_move_dates()
            self.assertEqual(min_d, min_date)
            self.assertFalse(max_d)
            self.assertTrue(match_stock_move_dates.return_value)

        with patch(path_stock_move_dates) as stock_move_dates, patch(
            path_match_stock_move_dates
        ) as match_stock_move_dates:
            self.invoice.date = max_date
            stock_move_dates.return_value = min_date, max_date
            min_d, max_d = self.invoice._get_min_max_stock_move_dates()
            self.assertEqual(min_d, min_date)
            self.assertTrue(max_date)
            self.assertTrue(match_stock_move_dates.return_value)

    def test_match_dates_by_day(self):
        same_month = datetime(2025, 2, 15, 10, 0)
        same_day = datetime(2025, 2, 1, 10, 0)
        self.assertTrue(
            self.invoice._match_invoice_and_stock_move_dates(same_month, same_month)
        )
        self.env["ir.config_parameter"].sudo().set_param(
            "account_invoice_check_picking_date.accounting_date_comparison", True
        )
        self.assertFalse(
            self.invoice._match_invoice_and_stock_move_dates(same_month, same_month)
        )
        self.assertTrue(
            self.invoice._match_invoice_and_stock_move_dates(same_day, same_day)
        )

    def test_min_max_stock_move_dates(self):
        location = self.env.ref("stock.stock_location_suppliers")
        location_dest = self.env.ref("stock.stock_location_stock")
        moves = self.env["stock.move"].create(
            [
                {
                    "name": "Test move",
                    "product_id": self.product.id,
                    "product_uom_qty": 1,
                    "product_uom": self.product.uom_id.id,
                    "location_id": location.id,
                    "location_dest_id": location_dest.id,
                    "date": date,
                }
                for date in (
                    datetime(2025, 1, 15),
                    datetime(2025, 1, 10),
                    datetime(2025, 1, 20),
                )
            ]
        )
        self._enable_picking_date_check(moves)
        min_date, max_date = self.invoice._get_min_max_stock_move_dates()
        self.assertEqual(min_date, datetime(2025, 1, 10))
        self.assertEqual(max_date, datetime(2025, 1, 20))

    def test_match_dates_without_stock_moves(self):
        self.assertTrue(self.invoice._match_invoice_and_stock_move_dates(False, False))

    def test_post_when_dates_match(self):
        self._enable_picking_date_check(self.picking.move_ids)
        self.picking.action_confirm()
        self.picking.action_assign()
        self.picking.button_validate()
        self.invoice.write({"invoice_date": "2025-01-20", "date": "2025-01-20"})
        self.assertFalse(self.invoice.action_post())
        self.assertEqual(self.invoice.state, "posted")

    def test_post_invoice_type_not_checked(self):
        self._enable_picking_date_check(self.picking.move_ids)
        self.picking.action_confirm()
        self.picking.action_assign()
        self.picking.button_validate()
        self.env["ir.config_parameter"].sudo().set_param(
            "account_invoice_check_picking_date.invoice_types", "in_refund"
        )
        self.assertFalse(self.invoice.action_post())
        self.assertEqual(self.invoice.state, "posted")

    def test_is_test_enabled(self):
        self.assertTrue(self.env["account.move"]._is_test_enabled())
