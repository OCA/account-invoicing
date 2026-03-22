# Copyright 2023 Tecnativa - Carlos Roca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command
from odoo.tests import TransactionCase


class TestPortalInvoiceSearchByLot(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create partner
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "test@example.com",
            }
        )
        # Create product
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product with Lot",
                "type": "consu",
                "is_storable": True,
                "tracking": "lot",
            }
        )
        # Create lots
        cls.lot_1 = cls.env["stock.lot"].create(
            {
                "name": "LOT-001",
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.lot_2 = cls.env["stock.lot"].create(
            {
                "name": "LOT-002",
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.lot_3 = cls.env["stock.lot"].create(
            {
                "name": "SERIAL-XYZ",
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
            }
        )
        # Create sale order
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "product_uom_qty": 3.0,
                            "price_unit": 100.0,
                        }
                    )
                ],
            }
        )
        cls.sale_order.action_confirm()
        cls.sale_line = cls.sale_order.order_line[0]

        # Create picking and stock moves
        cls.picking = cls.sale_order.picking_ids[0]
        cls.stock_move = cls.picking.move_ids[0]

        # Create stock move lines with lots
        cls.move_line_1 = cls.env["stock.move.line"].create(
            {
                "move_id": cls.stock_move.id,
                "product_id": cls.product.id,
                "lot_id": cls.lot_1.id,
                "quantity": 1.0,
                "location_id": cls.picking.location_id.id,
                "location_dest_id": cls.picking.location_dest_id.id,
                "picking_id": cls.picking.id,
            }
        )
        cls.move_line_2 = cls.env["stock.move.line"].create(
            {
                "move_id": cls.stock_move.id,
                "product_id": cls.product.id,
                "lot_id": cls.lot_2.id,
                "quantity": 2.0,
                "location_id": cls.picking.location_id.id,
                "location_dest_id": cls.picking.location_dest_id.id,
                "picking_id": cls.picking.id,
            }
        )

        # Validate picking
        cls.picking.button_validate()

        # Create invoice from sale order
        cls.invoice = cls.sale_order._create_invoices()
        cls.invoice.action_post()

    def test_search_lot_name_search_with_valid_operator(self):
        """Test _search_lot_name_search with equality operator"""
        result = self.env["account.move"]._search_lot_name_search("=", "LOT-001")
        self.assertIsInstance(result, list)
        self.assertTrue(len(result) > 0)
        # Should return a domain
        self.assertIn("line_ids.sale_line_ids", str(result))

    def test_search_lot_name_search_with_invalid_operator(self):
        """Test _search_lot_name_search with non-equality operator"""
        result = self.env["account.move"]._search_lot_name_search("!=", "LOT-001")
        self.assertEqual(result, [("id", "=", False)])

        result = self.env["account.move"]._search_lot_name_search("ilike", "LOT")
        self.assertEqual(result, [("id", "=", False)])

    def test_search_lot_name_search_nonexistent_lot(self):
        """Test search with a lot that doesn't exist"""
        result = self.env["account.move"]._search_lot_name_search(
            "=", "NONEXISTENT-LOT"
        )
        self.assertEqual(result, [("id", "=", False)])

    def test_search_lot_name_search_existing_lot(self):
        """Test search with existing lot"""
        result = self.env["account.move"]._search_lot_name_search("=", "LOT-001")
        # Should find the invoice
        self.assertNotEqual(result, [("id", "=", False)])

    def test_search_lot_name_search_partial_match(self):
        """Test search with partial lot name (case insensitive)"""
        result = self.env["account.move"]._search_lot_name_search("=", "lot-001")
        # Should find the invoice (ilike is case insensitive)
        self.assertNotEqual(result, [("id", "=", False)])

    def test_portal_search_by_lot(self):
        """Test portal invoice search by lot name"""
        domain = [("partner_id", "=", self.partner.id)]
        result = (
            self.env["account.move"]
            .with_context(portal_invoice_filter="LOT-001")
            .search(domain)
        )
        # Should find the invoice
        self.assertIn(self.invoice, result)

    def test_portal_search_by_serial(self):
        """Test portal invoice search by serial number"""
        # Create another picking with serial
        sale_order_2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 150.0,
                        }
                    )
                ],
            }
        )
        sale_order_2.action_confirm()
        picking_2 = sale_order_2.picking_ids[0]
        stock_move_2 = picking_2.move_ids[0]

        self.env["stock.move.line"].create(
            {
                "move_id": stock_move_2.id,
                "product_id": self.product.id,
                "lot_id": self.lot_3.id,
                "quantity": 1.0,
                "location_id": picking_2.location_id.id,
                "location_dest_id": picking_2.location_dest_id.id,
                "picking_id": picking_2.id,
            }
        )
        picking_2.button_validate()
        invoice_2 = sale_order_2._create_invoices()
        invoice_2.action_post()

        domain = [("partner_id", "=", self.partner.id)]
        result = (
            self.env["account.move"]
            .with_context(portal_invoice_filter="SERIAL-XYZ")
            .search(domain)
        )
        self.assertIn(invoice_2, result)
        self.assertNotIn(self.invoice, result)

    def test_portal_search_no_results(self):
        """Test portal search with no matching lot"""
        # We test specifically the lot search returns empty
        lot_result = self.env["account.move"]._search_lot_name_search(
            "=", "NONEXISTENT"
        )
        self.assertEqual(lot_result, [("id", "=", False)])

    def test_get_portal_search_domain(self):
        """Test _get_portal_search_domain method includes lot search"""
        domain = self.env["account.move"]._get_portal_search_domain("LOT-001")
        # Domain should be an OR expression including lot_name_search
        self.assertIn("lot_name_search", str(domain))
        # Should be an OR with parent domain
        self.assertIn("|", domain)

    def test_search_without_sale_order(self):
        """Test search when stock moves don't have sale_line_id"""
        # Create a picking without sale order
        picking_no_sale = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            }
        )
        lot_no_sale = self.env["stock.lot"].create(
            {
                "name": "LOT-NO-SALE",
                "product_id": self.product.id,
                "company_id": self.env.company.id,
            }
        )
        move_no_sale = self.env["stock.move"].create(
            {
                "name": "Test Move",
                "product_id": self.product.id,
                "product_uom_qty": 1.0,
                "product_uom": self.product.uom_id.id,
                "picking_id": picking_no_sale.id,
                "location_id": picking_no_sale.location_id.id,
                "location_dest_id": picking_no_sale.location_dest_id.id,
            }
        )
        self.env["stock.move.line"].create(
            {
                "move_id": move_no_sale.id,
                "product_id": self.product.id,
                "lot_id": lot_no_sale.id,
                "quantity": 1.0,
                "location_id": picking_no_sale.location_id.id,
                "location_dest_id": picking_no_sale.location_dest_id.id,
                "picking_id": picking_no_sale.id,
            }
        )
        picking_no_sale.button_validate()

        # Search should return empty domain (no sale lines)
        result = self.env["account.move"]._search_lot_name_search("=", "LOT-NO-SALE")
        self.assertEqual(result, [("id", "=", False)])

    def test_search_with_draft_moves(self):
        """Test that only done moves are considered"""
        # Create a draft picking
        sale_order_draft = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "product_uom_qty": 1.0,
                            "price_unit": 200.0,
                        }
                    )
                ],
            }
        )
        sale_order_draft.action_confirm()
        picking_draft = sale_order_draft.picking_ids[0]
        lot_draft = self.env["stock.lot"].create(
            {
                "name": "LOT-DRAFT",
                "product_id": self.product.id,
                "company_id": self.env.company.id,
            }
        )
        self.env["stock.move.line"].create(
            {
                "move_id": picking_draft.move_ids[0].id,
                "product_id": self.product.id,
                "lot_id": lot_draft.id,
                "quantity": 1.0,
                "location_id": picking_draft.location_id.id,
                "location_dest_id": picking_draft.location_dest_id.id,
                "picking_id": picking_draft.id,
            }
        )
        # Don't validate the picking (keep it in draft/assigned state)

        # Search should not find this lot because move is not done
        result = self.env["account.move"]._search_lot_name_search("=", "LOT-DRAFT")
        self.assertEqual(result, [("id", "=", False)])

    def test_portal_search_combined_with_other_filters(self):
        """Test lot search combined with other portal filters"""
        domain = [
            ("partner_id", "=", self.partner.id),
            ("move_type", "=", "out_invoice"),
        ]
        result = (
            self.env["account.move"]
            .with_context(portal_invoice_filter="LOT-001")
            .search(domain)
        )
        # Should find the invoice
        self.assertIn(self.invoice, result)
        # All results should be out_invoice type
        self.assertTrue(all(inv.move_type == "out_invoice" for inv in result))
